'''
Librería de funciones utilizadas en Warhammatic
Creada por Guser_06 como proyecto personal para facilitar el juego Warhammer 40k 10ma edición
Se recomienda leer este modulo y sus comentarios para entender la estructura bajo la
que se esta programando el archivo 'main vx.x.py'
'''
##-----Librerías-----
import random as rand
import json
from pathlib import Path
import sys
import blessed

import blessed.win_terminal as _wt
import time
_original_kbhit = _wt.Terminal.kbhit  # guarda función bugeada original

##Wrapear bug con blessed
def _safe_kbhit(s, timeout=0.000000000001):
    try:
        return _original_kbhit(s, timeout)
    except KeyboardInterrupt:
        return False
_wt.Terminal.kbhit = _safe_kbhit

term = blessed.Terminal()

##Listas formadoras de diccionarios
##Usar como claves para obtener datos en interacciones
StatsTx = ["Movimiento", "Resistencia", "Salvación",
           "Heridas", "Liderazgo", "Control de objetivo"]   #Nombre de las stats de las miniaturas

ArmaTx = ["Alcance", "No. de Ataques",
          "Habilidad", "Fuerza", "Perforación", "Daño"] #Nombre de las stats de las armas

#Menú de ejercitos disponibles
DISPONIBLE = [
    'Tyranidos v1',
    'Tyrannofex',
    'Space Marines v1',
    'Gladiator Lancer',
    'Debug',
    'salir'
]

##Otras listas constantes
MOVIMIENTO_T = [
    'Movimiento normal',
    'Estatico',
    'Avance',
    'Retroceder',
    'Continuar'
]

CARGA_T = [
    'Carga',
    'Estatico',
    'Continuar'
]

##Lista donde se guardaran los ejercitos convertidos en objetos de Python
##Usada como global aqui por que me dió weba
Ejercitos_objetos = []
#Inicializar ventana de manera global
Term = blessed.Terminal()


##-----Clases-----
class Arma:
    def __init__(self, diccionario, tx=ArmaTx):
        self.nombre = diccionario.get("Nombre")     ##Nombre del arma
        self.stats = dict(zip(tx, diccionario.get("Stats")))    ##Estadisticas del arma
        self.claves = diccionario.get("Claves")     ##Claves del arma
        self.usado = False  ##El arma se ha usado
    
    def reboot(self):
        self.usado = False

class Individuo(Arma):  ##Clase individuo usando ducktyping
    def __init__(self, diccionario):
        super().__init__(diccionario, StatsTx)  ##Usar nombre y stats como tales, claves no se usa
        self.usado = True  #Usado indica si la miniatura esta viva
        self.rango = []  #Armas de rango
        self.mele = []  #Armas cuerpo a cuerpo
        self.dmg = 0    #Daño recibido por la miniatura

    def AddWeap(self, diccionario):
        rans = ["Rango1", "Rango2", "Rango3", "Rango4"]
        for i in rans:
            if diccionario.get(i) is not None:
                self.rango.append(Arma(diccionario.get(i)))
            else:
                break
        mels = ["Mele1", "Mele2"]
        for i in mels:
            if diccionario.get(i) is not None:
                self.mele.append(Arma(diccionario.get(i)))
            else:
                break

    def recibir_dano(self, dano, habs):
        if 'No hay dolor' in habs.keys():
            nhd = habs.get('No hay dolor')
            if nhd > Dados(1, 6, True):
                self.dmg += dano
                return
            else:
                return f"No hay dolor {nhd}+ salvó {dano} heridas"
        else:
            self.dmg += dano
            
        if self.dmg >= self.stats["Heridas"]:  # Si daño >= heridas
            self.usado = False
            if 'Final Violento' in habs.keys():
                fv = Dados(1, 6, True)
                if fv == 6:
                    FinViol(habs, self.nombre, Ejercitos_objetos)
            return f"{self.nombre} ha muerto."

    def __repr__(self):
        estado = "Vivo" if self.usado else "Muerto"
        return f"{self.nombre} ({estado})"
   
class Unidad:
    def __init__(self, diccionario):
        self.mov = 0
        self.atk = 0
        self.engaged = False
        self.shock = False
        self.miembros = []
        self.nombre = diccionario.get("Nombre")
        self.posLid = diccionario.get("Lider")
        self.lider = ''
        self.habilidades = dict(diccionario.get("Habilidades"))
        self.claves = diccionario.get("Claves")
        self.nm = diccionario.get("Numero Miniaturas")

    def eliminar_muertos(self):
        self.miembros = [
            mini for mini in self.miembros if mini.usado == True]
    
    def __repr__(self):
        return f"{self.nombre}:\n" + "\n".join(str(miembro) for miembro in self.miembros) + ("\nAcobardado" if self.shock else "")

class Lider(Unidad):
    def __init__(self, diccionario):
        Unidad.__init__(self, diccionario = diccionario)
        self.liderando = True
        self.old_T = 0
        self.escolta_N = ''
        
    def AddLider(self, ej):        
        for i in ej.unidades:
            if isinstance(i.posLid, list) and i.lider == '':
                for x in i.posLid:
                    if x == self.nombre:
                        self.old_T = self.miembros[0].stats["Resistencia"]
                        self.escolta_N = i.nombre
                        self.miembros[0].stats["Resistencia"] = i.miembros[0].stats["Resistencia"]
                        self.miembros += i.miembros
                        self.habilidades |= i.habilidades
                        self.nm += i.nm
                        self.claves += i.claves
                        ej.unidades.append(self)
                        ej.unidades.remove(i)
                        return
        else:
            self.liderando = False
            ej.unidades.append(self)
            return
        
    def eliminar_muertos(self):
        super().eliminar_muertos()
        if len(self.miembros) == 1 and self.miembros[0].nombre == self.nombre:
            self.miembros[0].stats["Resistencia"] = self.old_T
            self.nm = 1
        elif not self.nombre in [m.nombre for m in self.miembros]:
            self.nombre = self.escolta_N
            self.nm -= 1

class Ejercito:
    def __init__(self, diccionario):
        self.pc = 0
        self.pv = 0
        self.faccion = diccionario.get('Faccion')
        self.nu = diccionario.get('Numero Unidades')
        self.unidades = []

    def eliminar_unidades(self):
        self.unidades = [uni for uni in self.unidades if len(uni.miembros) != 0]
    
    def __repr__(self):
        return f"{self.faccion}:\n" + "\n".join(str(unidad) for unidad in self.unidades)

##-----Funciones de Servidor-----
##Empaquetado


##Desempaquetado


##Request


##-----Funciones de dados-----
##Tirar dados
def Dados(n_dados, Dx, ret_num = True): #Numero de dados que se desean, Numero de caras del dado a lanzar
    ##ret_type False devuelve lista de valores, True devuelve la suma
    res_dados = [rand.randint(1, int(Dx)) for _ in range(0, int(n_dados))]
    if ret_num:
        res_dados = sum(res_dados)
    return res_dados

##Realizar un numero al azar de ataques
def AtkDmg_Rand(nDX, dmg = False):
    res = []
    ud = str(nDX).find('D')
    cantidad = int(str(nDX)[ud-1]) if ud != 0 else 1
    cantidad = Dados(cantidad, int(str(nDX)[ud+1]), True)
    if dmg: ##Si es para hacer cantidad de daño al azar
        if '+' in str(nDX):
            um = str(nDX).find('+')
            cantidad += int(str(nDX[um+1]))
        return cantidad
    
    if not dmg: ##Si es para hacer un numero de ataques al azar
        if '+' in str(nDX):
            um = str(nDX).find('+')
            cantidad += int(str(nDX[um+1]))
        res += Dados(cantidad, int(str(nDX)[ud+1]), False)
        return res

##Repetir las tiradas de dados que fallaron
def RepFallos(lista_dados, val, DX, ret_num = False):   
    exito = [dado for dado in lista_dados if dado >= val]
    n_fallos = len([dado for dado in lista_dados if dado < val])
    exito += Dados(n_dados=n_fallos, Dx=DX, ret_num= False)
    if ret_num:
        exito = sum(exito)
    return exito


##-----Funciones TUI-----
##Elegir limite rondas
def Limite_Rondas():
    with Term.fullscreen(), Term.cbreak(), Term.hidden_cursor():
        CadenaIngreso = ''
        print(Term.home + Term.clear)
        print(Term.springgreen4_on_black("Ingrese el limite de rondas"))
        
        while True:
            
            tecla = Term.inkey()
            
            if tecla and (tecla.is_sequence == False):
                CadenaIngreso += tecla
                print(Term.move_x(0), end='')
                print(Term.springgreen4_on_black(f"{CadenaIngreso}"), end='', flush=True)
                continue
            
            elif tecla.name == "KEY_ENTER":
                print(Term.springgreen4_on_black(f"\nIngresaste: {CadenaIngreso}"))
                print(Term.springgreen4_on_black("\nPresiona ENTER para continuar"))
                print(Term.springgreen4_on_black("\nPresiona cualquier tecla para reintentar"))
                
                tecla = Term.inkey()
                
                if tecla.name == "KEY_ENTER" or tecla == '\n':
                    return int(CadenaIngreso)
                    
                else:
                    CadenaIngreso = ''
                    print(Term.home + Term.clear)
                    print(Term.on_black)
                    print(Term.springgreen4_on_black("Ingrese el limite de rondas"))
                    continue

##Elegir ejercitos
def Elegir_Ejs():
    Ejercitos_diccionarios = [] #Diccionarios provenientes de los JSON
    Indice_ejercito = 0
    with Term.fullscreen(), Term.cbreak(), Term.hidden_cursor():
        while True:
            print(Term.home + Term.clear)
            print(Term.on_black)
            print(Term.springgreen4_on_black("Elige un ejercito:\n"))
    
            for i, opcion in enumerate(DISPONIBLE):    #Crear lista de opciones
                if i == Indice_ejercito:
                    print(Term.black_on_springgreen4(f"{i+1}. {opcion}"))
                else:
                    print(Term.springgreen4_on_black(f"{i+1}. {opcion}"))
    
            tecla = Term.inkey()

            if tecla.name in ("KEY_UP", "KEY_LEFT"):
                Indice_ejercito = (Indice_ejercito - 1 + len(DISPONIBLE)) % len(DISPONIBLE)
        
            elif tecla.name in ("KEY_DOWN", "KEY_RIGHT"):
                Indice_ejercito = (Indice_ejercito + 1 + len(DISPONIBLE)) % len(DISPONIBLE)

            elif tecla.name == "KEY_ENTER" or tecla == '\n':
                if Indice_ejercito == len(DISPONIBLE) - 1:
                    sys.exit()
                else:
                    print(Term.springgreen4_on_black(f"\nElegiste {DISPONIBLE[Indice_ejercito]}"))
                    #Constructor de unidades 
                    match (Indice_ejercito%len(DISPONIBLE)):
                        case 0:
                            filepath = Path(__file__).parent / "Ejercitos/Ty_patrol.json"
                            with open(filepath, 'r') as file:
                                Ejercitos_diccionarios.append(json.load(file))
                            if len(Ejercitos_diccionarios) == 2:
                                break
                            else: Term.inkey()
                    
                        case 1:
                            filepath = Path(__file__).parent / "Ejercitos/Ty_Tyrannofex.json"
                            with open(filepath, 'r') as file:
                                Ejercitos_diccionarios.append(json.load(file))
                            if len(Ejercitos_diccionarios) == 2:
                                break
                            else: Term.inkey()
                    
                        case 2:
                            filepath = Path(__file__).parent / "Ejercitos/UM_patrol.json"
                            with open(filepath, 'r') as file:
                                Ejercitos_diccionarios.append(json.load(file))
                            if len(Ejercitos_diccionarios)  == 2:
                                break
                            else: Term.inkey()
                    
                        case 3:
                            filepath = Path(__file__).parent / "Ejercitos/UM_Lancer.json"
                            with open(filepath, 'r') as file:
                                Ejercitos_diccionarios.append(json.load(file))
                            if len(Ejercitos_diccionarios) == 2:
                                break
                            else: Term.inkey()
                            
                        case 4:
                            filepath = Path(__file__).parent / "Ejercitos/Debug_army.json"
                            with open(filepath, 'r') as file:
                                Ejercitos_diccionarios.append(json.load(file))
                            if len(Ejercitos_diccionarios) == 2:
                                break
                            else: Term.inkey()

            else:
                print(Term.springgreen4_on_black(f"\nLa tecla presionada '{tecla}' es invalida"))
                Term.inkey()
        
        return Ejercitos_diccionarios

##Definir que jugador empieza
def DeTerminar_turno():
    with Term.fullscreen(), Term.cbreak(), Term.hidden_cursor():
        turno = 0
        while True:
            while turno == 0:
                print(Term.home + Term.clear)
                print(Term.on_black)
                print(Term.springgreen4_on_black("Determinando los turnos"))
            
                comenzar = Dados(2, 6, ret_num=False)
                print(Term.springgreen4_on_black(f"Dado Jugador 1 ({Ejercitos_objetos[0].faccion}): {comenzar[0]}"))
                print(Term.springgreen4_on_black(f"Dado Jugador 2 ({Ejercitos_objetos[1].faccion}): {comenzar[1]}"))
                if comenzar[0] > comenzar[1]:
                    print(Term.springgreen4_on_black("\nComienza el jugador 1"))
                    turno = 2
                    break
                if comenzar[0] < comenzar[1]:
                    print(Term.springgreen4_on_black("\nComienza el jugador 2"))
                    turno = 1
                    break
                
                else: continue
            
            print(Term.springgreen4_on_black("Presione cualquier tecla para continuar"))
            Term.inkey()
            print(Term.home + Term.clear)
            return turno

##Mostrar un mensaje en terminal y esperar confirmación
def Mostrar_Mensaje(mensaje, limpiar=True):
    """Muestra un mensaje simple en verde sobre negro y espera una tecla."""
    with Term.cbreak(), Term.hidden_cursor():
        if limpiar:
            print(Term.home + Term.clear)
        print(Term.springgreen4_on_black(mensaje))
        print(Term.springgreen4_on_black("Presione cualquier tecla para continuar"))
        return Term.inkey()

##Solicitar elección
def Menu_Seleccion(titulo, opciones, indice_actual):
    """Dibuja un menú de opciones con un elemento resaltado."""
    while True:
        print(Term.home + Term.clear)
        print(Term.springgreen4_on_black(titulo))
        for i, opcion in enumerate(opciones):
            if i == indice_actual:
                print(Term.black_on_springgreen4(f"{i+1}. {opcion}"))
            else:
                print(Term.springgreen4_on_black(f"{i+1}. {opcion}"))
        tecla = Term.inkey()

        if tecla.name in ("KEY_UP", "KEY_LEFT"):
            indice_actual = (indice_actual - 1 + len(opciones)) % len(opciones)
            continue

        elif tecla.name in ("KEY_DOWN", "KEY_RIGHT"):
            indice_actual = (indice_actual + 1 + len(opciones)) % len(opciones)
            continue

        elif tecla.name == "KEY_ENTER" or tecla == '\n':
            return indice_actual
        
        else:
            print(Term.springgreen4_on_black(f"\nLa tecla presionada '{tecla}' es invalida"))
            Term.inkey()
            continue

##Solicitar un numero
def Leer_Numero(prompt):
    """Maneja la entrada numérica por teclado con retroalimentación visual."""
    cadena = ''
    print(Term.home + Term.clear)
    print(Term.springgreen4_on_black(prompt))
    while True:
        key = Term.inkey()
        if key.is_sequence is False and key.isdigit():
            cadena += key
            print(Term.move_x(0) + Term.springgreen4_on_black(cadena), end='', flush=True)
        elif key.name == "KEY_ENTER" and cadena:
            return int(cadena)

##Función menu
def Menu_func(unidad, TXT:list, FUN:list, par = None):
    Indice = 0
    while True:
        with Term.fullscreen(), Term.cbreak(), Term.hidden_cursor():
            print(Term.home + Term.clear)
            print(Term.on_black)
            print(Term.springgreen4_on_black(f"Elige una acción para realizar con {unidad.nombre}"))
            print(Term.springgreen4_on_black(f"Si ya seleccionó una acción, elija continuar \n"))
    
            for i, opcion in enumerate(TXT):    #Crear lista de opciones
                if i == Indice:
                    print(Term.black_on_springgreen4(f"{i+1}. {opcion}"))
                else:
                    print(Term.springgreen4_on_black(f"{i+1}. {opcion}"))
    
            tecla = Term.inkey()
    
            if tecla.name in ("KEY_UP", "KEY_LEFT"):
                Indice = (Indice - 1 + len(TXT)) % len(TXT)
        
            elif tecla.name in ("KEY_DOWN", "KEY_RIGHT"):
                Indice = (Indice + 1 + len(TXT)) % len(TXT)
            
            elif tecla.name == "KEY_ENTER" or tecla == '\n':
                if Indice == len(TXT) - 1:
                    ##menu anterior
                    return
    
                else:
                    print(Term.springgreen4_on_black(f"\nElegiste {TXT[Indice]}"))
                    Conf_usr(lista_F=FUN, lista_T=TXT, indice_F=Indice, p1= unidad, p2 =par)
                
                        
                    
            else:
                print(Term.springgreen4_on_black(f"\nLa tecla presionada '{tecla}' es invalida"))
                Term.inkey()

##Funcion confirmación de funcion
def Conf_usr(lista_F:list, lista_T:list, indice_F:int, p1, p2 = None):     ##lista de funciones, el indice de la lista y al menos un parametro
    while True:
        with Term.fullscreen(), Term.cbreak(), Term.hidden_cursor():

            print(Term.home + Term.clear)

            print(Term.springgreen4_on_black(f"\nIngresaste: {str(lista_T[indice_F])}"))
            print(Term.springgreen4_on_black("\nPresiona ENTER para continuar"))
            print(Term.springgreen4_on_black("\nPresiona cualquier otra tecla para regresar"))
            
            tecla = Term.inkey()
            
            if tecla.name == "KEY_ENTER" or tecla == '\n':
                    ##Hacer algo
                lista_F[indice_F](p1, p2)
                return
                
            else:
                print(Term.home + Term.clear)
                print(Term.on_black)
                print(Term.springgreen4_on_black("Regresando..."))
                break
                
    return

##Funcion seleccionar blanco devuelve una unidad
def Selec_Blanco(unidad, accion:str, Ejer_Enem, Indirecta = False):   ##Accion debe ser una cadena: 'cargar', 'disparar', 'combatir'
    indice = 0
    Ejer_Enem.eliminar_unidades()
    while True:
        with Term.fullscreen(), Term.cbreak(), Term.hidden_cursor():
            
            print(Term.home + Term.clear)
            print(Term.on_black)
            print(Term.springgreen4_on_black(f"Elige un blanco para {accion} con {unidad.nombre}"))
            print(Term.springgreen4_on_black(f"Asegurese que el blanco sea valido para {accion}\n"))
            
            if Indirecta:
                print(Term.springgreen4_on_black(f"El arma seleccionada es un arma Indirecta, puede atacar a unidades no visibles"))

    
            for i, opcion in enumerate(Ejer_Enem.unidades + [f"No {accion}"]):    #Crear lista de opciones
                if i == indice:
                    print(Term.black_on_springgreen4(f"{i+1}. {opcion.nombre if isinstance(opcion, Unidad) else opcion}"))
                else:
                    print(Term.springgreen4_on_black(f"{i+1}. {opcion.nombre if isinstance(opcion, Unidad) else opcion}"))
    
            tecla = Term.inkey()
    
            if tecla.name in ("KEY_UP", "KEY_LEFT"):
                indice = (indice - 1 + len(Ejer_Enem.unidades + [f"No {accion}"])) % len(Ejer_Enem.unidades + [f"No {accion}"])
        
            elif tecla.name in ("KEY_DOWN", "KEY_RIGHT"):
                indice = (indice + 1 + len(Ejer_Enem.unidades + [f"No {accion}"])) % len(Ejer_Enem.unidades + [f"No {accion}"])
            
            elif tecla.name == "KEY_ENTER" or tecla == '\n':
                if indice > len(Ejer_Enem.unidades)-1:
                    print(Term.springgreen4_on_black(f"\nElegiste: No {accion}"))
                    return None
                else:
                    print(Term.springgreen4_on_black(f"\nElegiste: {Ejer_Enem.unidades[indice].nombre}"))
                    print(Term.springgreen4_on_black(f"Presione cualquier tecla para continuar"))

                    Term.inkey()

                    return Ejer_Enem.unidades[indice]
                    
            else:
                print(Term.springgreen4_on_black(f"\nLa tecla presionada '{tecla}' es invalida"))
                Term.inkey()

##Funcion seleccionar miniatura Devuelve indice que la miniatura ocupa en la unidad
def Selec_mini(unidad, Precision = False):
    indice = 0
    while True:
        with Term.fullscreen(), Term.cbreak(), Term.hidden_cursor():
            if len(unidad.miembros) == 0:
                print(Term.springgreen4_on_black(f"Ya no quedan miembros de {unidad.nombre}"))
                print(Term.springgreen4_on_black(f"Presiona cualquier tecla para continuar"))
                Term.inkey()
                return None
                
            else:
                
                print(Term.springgreen4_on_black(f"Elige una miniatura de {unidad.nombre} para recibir daño"))
                if Precision:
                    print(Term.black_on_springgreen4(f"El arma utilizada es de Precision, el atacante puede elegir un Personaje para recibir el daño! (si es visible)"))

                for i, opcion in enumerate(unidad.miembros):    #Crear lista de opciones
                    if i == indice:
                        print(Term.black_on_springgreen4(f"{i+1}. {opcion.nombre}   {opcion.dmg if opcion.dmg != 0 else ''}"))
                    else:
                        print(Term.springgreen4_on_black(f"{i+1}. {opcion.nombre}   {opcion.dmg if opcion.dmg != 0 else ''}"))
            
                tecla = Term.inkey()

                if tecla.name in ("KEY_UP", "KEY_LEFT"):
                    indice = (indice - 1 + len(unidad.miembros)) % len(unidad.miembros)
        
                elif tecla.name in ("KEY_DOWN", "KEY_RIGHT"):
                    indice = (indice + 1 + len(unidad.miembros)) % len(unidad.miembros)
            
                elif tecla.name == "KEY_ENTER" or tecla == '\n':
                    return indice
                    
                else:
                    print(Term.springgreen4_on_black(f"\nLa tecla presionada '{tecla}' es invalida"))
                    Term.inkey()

##Eleccion Si NO
def Selec_SN(row, col, text):
    indice = 0
    ops = ['Si', 'No']
    while True:
        with Term.fullscreen(), Term.cbreak(), Term.location(row, col), Term.hidden_cursor():
            print(Term.home + Term.clear)
            print(Term.springgreen4_on_black(text))
            

            for i, opcion in enumerate(ops):    #Crear lista de opciones
                if i == indice:
                    print(Term.black_on_springgreen4(f"{i+1}. {opcion}"))
                else:
                    print(Term.springgreen4_on_black(f"{i+1}. {opcion}"))
            
            tecla = Term.inkey()

            if tecla.name in ("KEY_UP", "KEY_LEFT"):
                indice = (indice - 1 + len(ops)) % len(ops)
        
            elif tecla.name in ("KEY_DOWN", "KEY_RIGHT"):
                indice = (indice + 1 + len(ops)) % len(ops)
            
            elif tecla.name == "KEY_ENTER" or tecla == '\n':
                return True if indice == 0 else False
                    
            else:
                print(Term.springgreen4_on_black(f"\nLa tecla presionada '{tecla}' es invalida"))
                Term.inkey()
                
##Definir si se Terminó la partida
def Victoria(lista_Ejs):
    for j in len(lista_Ejs):
        if len(lista_Ejs[j].unidades) == 0:
            print(Term.springgreen4_on_black(f"El ejercito de {lista_Ejs[j].faccion} ha sido eliminado"))
            print(Term.springgreen4_on_black(f"El ejercito de {lista_Ejs[j-1].faccion} ha salido ganador"))
            print(Term.springgreen4_on_black(f"La partida ha Terminado"))
        
        if (Ejercitos_objetos[0].nu - len(Ejercitos_objetos[0].unidades)) > (Ejercitos_objetos[1].nu - len(Ejercitos_objetos[1].unidades)):
            print(Term.springgreen4_on_black(f"El ejercito de {Ejercitos_objetos[1].faccion} ha ganado tras destruir mas unidades enemigas!"))
        elif (Ejercitos_objetos[0].nu - len(Ejercitos_objetos[0].unidades)) < (Ejercitos_objetos[1].nu - len(Ejercitos_objetos[1].unidades)):
            print(Term.springgreen4_on_black(f"El ejercito de {Ejercitos_objetos[0].faccion} ha ganado tras destruir mas unidades enemigas!"))
        elif (Ejercitos_objetos[0].nu - len(Ejercitos_objetos[0].unidades)) == (Ejercitos_objetos[1].nu - len(Ejercitos_objetos[1].unidades)):
            print(Term.springgreen4_on_black(f"Ningun ejercito ha destruido mas unidades enemigas que el otro, la partida termina en empate!"))
                
        print(Term.springgreen4_on_black("Presione cualquier tecla para terminar el programa"))
        Term.inkey()
        sys.exit()
    else: return False

#------Funciones estandar------
##Construir ejercitos
def Build_Armies(Dics):
    i = 0
    for d in Dics:    #iterar por lista de diccionarios
        j = 0
        if isinstance(d, dict):     #DeTerminar si el objeto es un diccionario
            Ejercitos_objetos.append(Ejercito(d))   #Crear el objeto ejercito
            lids = []
            k = 0
            for cu, vu in d.items():    #iterar por diccionario
                if isinstance(vu, dict):    #DeTerminar si el objeto es un subdiccionario
                    if vu["Lider"] is True:
                        lids.append(Lider(vu))
                        for cm, vm in vu.items():   #Iterar por el subdiccionario
                            if isinstance(vm, dict) and cm != 'Habilidades':    #DeTerminar si el objeto es un subsubdiccionario y no es el diccionario de habilidades
                                lids[k].miembros.append(Individuo(vm))     #Crear el objeto individuo y añadirlo a una unidad
                                lids[k].miembros[-1].AddWeap(vm)   #Crear armas y añadirlas al individuo
                        k += 1

                    if vu["Lider"] is not True:
                        Ejercitos_objetos[i].unidades.append(Unidad(vu))    #Crear el objeto unidad y añadirlo a un ejercito
                        for cm, vm in vu.items():   #Iterar por el subdiccionario
                            if isinstance(vm, dict) and cm != 'Habilidades':    #DeTerminar si el objeto es un subsubdiccionario y no es el diccionario de habilidades
                                Ejercitos_objetos[i].unidades[j].miembros.append(Individuo(vm))     #Crear el objeto individuo y añadirlo a una unidad
                                Ejercitos_objetos[i].unidades[j].miembros[-1].AddWeap(vm)   #Crear armas y añadirlas al individuo
                        j += 1

            for lid in lids:
                lid.AddLider(Ejercitos_objetos[i])

            i += 1
    return Ejercitos_objetos

##Aumentar puntos de comando
def Aumentar_PC(Ejer_Obj):
    for i in Ejer_Obj:
        i.pc += 1
    return

##Reestablecer condiciones de movimiento
def Aumentar_Mov_Atk(Ejercito):
    for u in Ejercito.unidades:
        u.mov = 3
        u.atk = 3
    return

##Prueba de shock de batalla
def Shock_Test(unidad):
    if len(unidad.miembros)<(unidad.nm//2) and (unidad.nm != 1):
        mayor = max([mini.stats.get("Liderazgo") for mini in unidad.miembros])
        
        prueba = Dados(2, 6)
        if prueba < mayor:   
            unidad.shock = True
            Mostrar_Mensaje(unidad.__repr__())
            
        else:
            unidad.shock = False
            Mostrar_Mensaje(unidad.__repr__())

    elif unidad.nm == 1 and unidad.miembros[0].dmg > unidad.miembros[0].stats.get("Heridas")//2:
        prueba = Dados(2, 6)
        if prueba < unidad.miembros[0].stats.get("Liderazgo"):   
            unidad.shock = True
            Mostrar_Mensaje(unidad.__repr__())
            

        else:
            unidad.shock = False
            Mostrar_Mensaje(unidad.__repr__())
            
    else: 
        Mostrar_Mensaje(f"La unidad {unidad.nombre} paso la prueba")
        
    return

##Repartir heridas
def RepDmg(blanco, dano, Precision = False):
    while dano >= 1:
        danada = Selec_mini(blanco, Precision)
        if danada == None:
            dano = 0
            return
        Qt_dmg = blanco.miembros[danada].stats.get("Heridas")-blanco.miembros[danada].dmg
        if dano >= Qt_dmg:
            Mostrar_Mensaje(f"{blanco.miembros[danada].recibir_dano(Qt_dmg, blanco.habilidades)}")
            dano -= Qt_dmg
            blanco.eliminar_muertos()
        else:
            blanco.miembros[danada].recibir_dano(dano, blanco.habilidades)
            Mostrar_Mensaje(f"{blanco.miembros[danada].__repr__()}\nHeridas recibidas: {blanco.miembros[danada].dmg}")
            dano = 0
    return

##Funcion de disparo
def Disparo(unidad, Ejer_Enem):
    whitelist = ["Vehiculo", "Monstruo", "Pistola", "Asalto"]
    graylist = ["Vehiculo", "Monstruo", ]
    ##Verificar que la unidad tenga armas de rango
    for miembro in unidad.miembros:
        if len(miembro.rango) != 0:
            break
    else:
        Mostrar_Mensaje(f"{unidad.nombre} no tiene armas para disparar")
        return

    keysu = []
    keysu = set(keysu)
    ##Buscar claves de armas
    for miembro in unidad.miembros:
        for arma in miembro.rango:
            keysu|=(arma.claves.keys()) & set(whitelist)
    keysu|=(set(unidad.claves) & set(whitelist))
    
    ##Verificar que la unidad no haya retrocedido
    if unidad.atk == 0:
        Mostrar_Mensaje(f"{unidad.nombre} ya no puede disparar en este turno")
        return
    
    ##Regla Asalto
    asalt = (unidad.atk == 1 and unidad.mov == 1 and 'Asalto' in keysu)
    ##Verificar si la unidad Avanzo
    if asalt:
        Mostrar_Mensaje(f"{unidad.nombre} solo puede disparar con armas de Asalto en este turno")
    elif unidad.atk == 1 and unidad.mov and not 'Asalto' in keysu:
        Mostrar_Mensaje(f"{unidad.nombre} ya no puede disparar en este turno")
        return     
    
    ##Verificar que la unidad no esté en zona de amenaza
    if unidad.engaged == True and not any(unidad.claves & whitelist):
        Mostrar_Mensaje(f"{unidad.nombre} no puede disparar, está demasiado cerca de un enemigo")
        return
    else:
        ##Seleccionar un arma
        for miembro in unidad.miembros:
            indice = 0
            while True:
                ##Romper ciclo en caso de que se hallan usado todas las armas
                l_armas = [x.usado for x in miembro.rango]
                if all(l_armas):
                    break
                nombres = ([arma.nombre for arma in miembro.rango])

                indice = Menu_Seleccion(f"Elija un arma para disparar con {miembro.nombre}:", nombres, 0)
                """print(Term.home + Term.clear)
                print(Term.springgreen4_on_black(f"Elija un arma para disparar con {miembro.nombre}:"))

                ##Construir menú

                for i, arma in enumerate(miembro.rango):
                    if i == indice:
                        print(Term.black_on_springgreen4(f"{i+1}. {arma.nombre}"))
                    else:
                        print(Term.springgreen4_on_black(f"{i+1}. {arma.nombre}"))

                tecla = Term.inkey()

                if tecla.name in ("KEY_UP", "KEY_LEFT"):
                    indice = (indice - 1 + len(miembro.rango)) % len(miembro.rango)
                    continue
    
                elif tecla.name in ("KEY_DOWN", "KEY_RIGHT"):
                    indice = (indice + 1 + len(miembro.rango)) % len(miembro.rango)
                    continue
        
                elif tecla.name == "KEY_ENTER" or tecla == '\n':"""
                if not miembro.rango[indice].usado:

                    ##Hacer valida regla asalto
                    if asalt and not 'Asalto' in miembro.rango[indice].claves.keys():
                        Mostrar_Mensaje(f"No puede disparar con {miembro.rango[indice].nombre} en este turno")
                        miembro.rango[indice].usado = True
                        continue
                    
                    ##Verificar regla precisiom
                    if 'Precision' in miembro.rango[indice].claves.keys():
                        Precision = True
                    
                    ##Regla indirecta
                    Ind = False
                    if 'Indirecta' in miembro.rango[indice].claves.keys():
                        Ind = True

                    ##Si no se ha usado el arma elegida, seguir proceso
                    Mostrar_Mensaje(f"\nElegiste: {miembro.rango[indice].nombre}")

                    ##Elegir un blanco y recuperar sus claves si es valido
                    blanco = Selec_Blanco(unidad=unidad, accion='Disparar', Ejer_Enem=Ejer_Enem, Indirecta = Ind)
                    if blanco is None:
                        miembro.rango[indice].usado = True
                        continue
                    else:

                        keysb = []
                        keysb = set(keysb)
                        keysb|=(set(blanco.claves) & set(graylist))

                        if blanco.engaged and not any(keysb):
                            Mostrar_Mensaje(f"{blanco.nombre} está muy cerca de un aliado!")
                            continue

                        ##Ingresar distancia
                        dist = Leer_Numero(f"Ingrese la distancia entre {unidad.nombre} y {blanco.nombre}")

                        ##Verificar alcance
                        if dist > miembro.rango[indice].stats.get("Alcance"):
                            Mostrar_Mensaje(f"El blanco elegido está fuera del alcance de {miembro.rango[indice].nombre}")
                            continue

                        ##Regla Agente solitario
                        if blanco.lider != '' and 'Agente Solitario' in blanco.habilidades.keys() and dist >= 12:
                            Mostrar_Mensaje(f"{blanco.nombre} es un agente solitario y se ha escabullido!")
                            continue                                

                        else:
                            ##Tirada para impactar
                            n = miembro.rango[indice].stats.get("No. de Ataques")
                            ##Usar en caso de torrente, para evitar activar reglas de impacto critico
                            tor = 0
                            
                            if isinstance(miembro.rango[indice].claves, dict):

                                ##Regla Area (blast)                                
                                if 'Area' in miembro.rango[indice].claves.keys():
                                    if blanco.engaged == True:
                                        Mostrar_Mensaje(f"{blanco.nombre} esta demasiado cerca de una unidad aliada para usar esta arma")
                                        continue
                                    else:
                                        n += ('+' + str(len(blanco.miembros)//5))

                                ##Regla Fuego rapido
                                elif 'Fuego Rapido' in miembro.rango[indice].claves.keys():
                                    if dist <= miembro.rango[indice].stats.get("Alcance")//2:
                                        Mostrar_Mensaje(f"{unidad.nombre} está cerca de su objetivo y lanza {miembro.rango[indice].claves.get('Fuego Rapido')} ataques adicionales")
                                        n += miembro.rango[indice].claves.get('Fuego Rapido') if isinstance(n, int) else f'+{miembro.rango[indice].claves.get('Fuego Rapido')}'

                                elif 'Torrente' in miembro.rango[indice].claves.keys():
                                    Mostrar_Mensaje(f"{miembro.rango[indice].nombre} es un arma de Torrente e impacta directamente!")
                                    tor = 5
                        
                            ##Si se repite el arma usar Tirada rapida
                            impact = []
                            nAI = Repetida(miembro.rango[indice], unidad)
                            if nAI > 1:
                                t = f"\nMultiples miniaturas en {unidad.nombre} usan {miembro.rango[indice].nombre}\nDesea hacer una tirada rápida para dispararlas todas contra {blanco.nombre}?"
                                r, c = Term.get_location()
                                if Selec_SN(r, c, t):
                                    for m in unidad.miembros:
                                        for a in m.rango:
                                            if miembro.rango[indice].nombre == a.nombre and not a.usado:
                                                impact += Dados(n, tor if tor else 6, False) if isinstance(miembro.rango[indice].stats.get("No. de Ataques"), int) else AtkDmg_Rand(n)
                                                a.usado = True
                                                if 'Perfil' in miembro.rango[indice].claves.keys():
                                                    for arma in miembro.rango:
                                                        if 'Perfil' in arma.claves.keys():
                                                            arma.usado = True
                                            else: continue
                                else:
                                    miembro.rango[indice].nombre
                                    impact = Dados(n, tor if tor else 6, False) if isinstance(miembro.rango[indice].stats.get("No. de Ataques"), int) else AtkDmg_Rand(n)

                            else:
                                ##Una vez pasado cualquier filtro se considera usada el arma
                                miembro.rango[indice].usado = True
                            
                                ##Colocar como usadas las armas de perfiles opcionales
                                if 'Perfil' in miembro.rango[indice].claves.keys():
                                    for arma in miembro.rango:
                                        if 'Perfil' in arma.claves.keys():
                                            arma.usado = True
                                    
                                impact = Dados(n, 6, False) if isinstance(miembro.rango[indice].stats.get("No. de Ataques"), int) else AtkDmg_Rand(n)
                            
                            if isinstance(miembro.rango[indice].claves, dict):
                                ##Regla indirecta
                                if 'Indirecta' in miembro.rango[indice].claves.keys():
                                    r, c = Term.get_location()
                                    texto = f"{blanco.nombre} es visible para {unidad.nombre}?"
                                    visible = Selec_SN(row=r, col=c, text=texto)
                                    if not visible:
                                        cobertura = True
                                        impact = [dado-1 for dado in impact if dado > 1]
                                
                                ##Golpes sostenidos
                                elif 'Golpes Sostenidos' in miembro.rango[indice].claves.keys():
                                    nGS = miembro.rango[indice].claves.get('Golpes Sostenidos')
                                    nAd = 0
                                    print(Term.springgreen4_on_black(f"El arma {miembro.rango[indice].nombre} hace golpes sostenidos"))
                                    for dado in impact:
                                        if dado == 6:
                                            nAd += nGS if isinstance(nGS, int) else AtkDmg_Rand(nGS, False)
                                    print(Term.springgreen4_on_black(f"Se produjeron {nAd} impactos adicionales")) 
                                    impact += [6] * nAd
                                        
                        
                                ##Impactos letales
                                elif 'Impactos Letales' in miembro.rango[indice].claves.keys():
                                    print(Term.springgreen4_on_black(f"El arma {miembro.mele[indice].nombre} causa impactos letales"))
                                    seis = [dado for dado in impact if dado == 6]
                                    impact = [dado for dado in impact if dado != 6]
                                    print(Term.springgreen4_on_black(f"{len(seis)} impactos fueron letales"))
                                    m = miembro.mele[indice].stats.get("Daño")
                                    dano = 0
                                    for d in seis:
                                        dano += m if isinstance(m, int) else AtkDmg_Rand(m, True)
                                    RepDmg(blanco, dano)

                                ##Regla Pesada
                                elif 'Pesado' in miembro.rango[indice].claves.keys() and unidad.mov == 3:
                                    print(Term.springgreen4_on_black(f"{unidad.nombre} no se movió en este turno y se beneficia de ello"))
                                    impact = [dado+1 for dado in impact]

                                elif ('Monstruo' in unidad.claves or 'Vehiculo' in unidad.claves) and unidad.engaged == True:
                                    print(Term.springgreen4_on_black(f"{unidad.nombre} ha tenido problemas para apuntar por estar muy cerca de otro enemigo"))
                                    impact = [dado for dado in impact if dado > 1]
                                    impact = [dado-1 for dado in impact]
                                    print(Term.springgreen4_on_black("Presiona cualquier tecla para continuar"))

                                elif 'Sigilo' in blanco.habilidades.keys():
                                    print(Term.springgreen4_on_black(f"{blanco.nombre} es sigiloso y ha sido dificil impactarle!"))
                                    impact = [dado for dado in impact if dado > 1]
                                    impact = [dado-1 for dado in impact]
                                    print(Term.springgreen4_on_black("Presiona cualquier tecla para continuar"))
                                    Term.inkey()
                                
                            Mostrar_Mensaje(f"Se han lanzado {len(impact)} ataques")
                            impact = [dado for dado in impact if dado >= miembro.rango[indice].stats.get("Habilidad")]
                            Mostrar_Mensaje(f"Las tiradas para impactar exitosas: {impact}")
                            if len(impact) == 0:
                                continue
                            else:
                                
                                ##Tirada para herir
                                herir = Dados(len(impact), 6, ret_num=False)
                                obj = 0

                                if miembro.rango[indice].stats.get("Fuerza") >= 2*blanco.miembros[0].stats.get("Resistencia"):
                                    obj = 2
                            
                                elif miembro.rango[indice].stats.get("Fuerza") > blanco.miembros[0].stats.get("Resistencia"):
                                    obj = 3
                            
                                elif miembro.rango[indice].stats.get("Fuerza") == blanco.miembros[0].stats.get("Resistencia"):
                                    obj = 4
                            
                                elif miembro.rango[indice].stats.get("Fuerza") < blanco.miembros[0].stats.get("Resistencia"):
                                    obj = 5
                            
                                elif miembro.rango[indice].stats.get("Fuerza")*2 <= blanco.miembros[0].stats.get("Resistencia"):
                                    obj = 6

                                herir = [dado for dado in herir if dado >= obj]
                            
                                ##Regla Heridas devastadoras
                                if 'Heridas devastadoras' in miembro.rango[indice].claves.keys():
                                    dev = [dado for dado in herir if dado == 6]
                                    herir = [dado for dado in herir if dado != 6]
                                
                                    if len(dev) != 0:
                                        Mostrar_Mensaje(f"{blanco.nombre} ha sufrido heridas devastadoras")
                                        salvar = len(dev)
                                        m = miembro.rango[indice].stats.get("Daño")
                                        if isinstance(m, str):
                                            dano_azar = []
                                            for x in range(0, len(dev)):
                                                dano_azar.append(AtkDmg_Rand(m, True) )
                                            salvar = sum(dano_azar)
                                        else:
                                            dano = int(m)
                                            salvar*=dano

                                        Mostrar_Mensaje(f"A que miniatura se le asignarán {salvar} heridas?")

                                        RepDmg(blanco, salvar)
                            
                                Mostrar_Mensaje(f"Las tiradas que han herido: {herir}\n")

                                ##Palabra clave acoplado
                                if 'Acoplado' in miembro.rango[indice].claves:
                                    t = f"{miembro.rango[indice].nombre} es un arma acoplada, ¿Desea repetir la tirada para herir?"
                                    r, c = Term.get_location()
                                    if Selec_SN(r, c, t):
                                        herir = RepFallos(lista_dados=herir, val=obj, DX=6)

                                        herir = [dado for dado in herir if dado >= obj]
                                    
                                        Mostrar_Mensaje(f"Las tiradas que han herido: \n{herir}")
                                        if len(herir) == 0:
                                            continue
                                    
                                if len(herir) == 0:
                                    Mostrar_Mensaje("", False)
                                    continue

                                ##Regla anti
                                if 'Anti' in miembro.rango[indice].claves.keys():
                                    if miembro.rango[indice].claves.get('Anti')[0] in blanco.claves:
                                        a = 0
                                        for i in herir:
                                            if i >= miembro.rango[indice].claves.get('Anti')[1]:
                                                a += 1
                                        if a:
                                            Mostrar_Mensaje(f"{blanco.nombre} ha sufrido heridas mortales!\nA que miniatura se le asignarán las heridas?")
                                            m = miembro.rango[indice].stats.get("Daño")
                                            if isinstance(m, str):
                                                dano_azar = []
                                                for x in range(0, a):
                                                    dano_azar.append(AtkDmg_Rand(m, True) )
                                                dano = sum(dano_azar)
                                            else:
                                                dano = int(m)
                                                dano*=a

                                            Mostrar_Mensaje("")

                                            RepDmg(blanco, dano)
                                            


                                Mostrar_Mensaje(f"A continuación, permita al oponente usar la Terminal")

                                if len(blanco.miembros) == 0:
                                    continue

                                index = 0
                                while True:
                                    Mostrar_Mensaje(f"Es momento de las tiradas de salvación de {blanco.nombre}\nEl factor de perforación del arma atacante es -{miembro.rango[indice].stats.get('Perforación')}")
                                    
                                    ##Blanco se beneficia de cobertura
                                    r, c = Term.get_location()
                                    texto = f"{blanco.nombre} se beneficia de cobertura?"
                                    cobertura = Selec_SN(row=r, col=c, text= texto)
                        
                                    salvacion = blanco.miembros[0].stats.get("Salvación")
                                    
                                    if miembro.rango[indice].stats.get("Perforación") > 0:
                                        Mostrar_Mensaje(f"La salvación requerida sube a {blanco.miembros[0].stats.get("Salvación") + miembro.rango[indice].stats.get("Perforación")}")
                                        salvacion += miembro.rango[indice].stats.get("Perforación")

                                    if 'Invulnerable' in blanco.habilidades.keys():
                                        titulo = f"La unidad atacada tiene una salvación invulnerable de {blanco.habilidades.get('Invulnerable')}\n¿Que perfil desea usar?"
                                        S = [f"Salvación regular: {blanco.miembros[0].stats.get('Salvación') + miembro.rango[indice].stats.get('Perforación')}+",
                                            f"Salvación invulnerable: {blanco.habilidades.get('Invulnerable')}+"]
                                        index = Menu_Seleccion(titulo, S, 0)

                                        if index == 0:
                                            salvacion = blanco.miembros[0].stats.get("Salvación") + miembro.rango[indice].stats.get("Perforación")
                                        elif index == 1:
                                            salvacion = blanco.habilidades.get('Invulnerable')
                                            cobertura = False
                                
                                    if not 'Invulnerable' in blanco.habilidades.keys():
                                        Mostrar_Mensaje("", False)
                                        break
                                    
                                    ##Caso donde cobertura se invalida
                                    elif cobertura and salvacion <= 3 and miembro.rango[indice].stats.get('Perforación') == 0:
                                        cobertura = False
                                    
                                    ##Regla ignora cobertura
                                    elif 'Ignora Cobertura' in miembro.rango[indice].claves.keys():
                                        cobertura = False
                                
                                salvar = Dados(len(herir), 6, False)
                                
                                ##Hacer valida regla cobertura
                                if cobertura:
                                    salvar = [dado+1 for dado in salvar]
                                
                                salvar = [dado for dado in salvar if dado >= salvacion]
                                Mostrar_Mensaje(f"Se han salvado {len(salvar)} de {len(herir)} ataques")

                                if len(herir) > len(salvar):
                                    salvar = len(herir) - len(salvar)
                                    m = miembro.rango[indice].stats.get("Daño")
                                    
                                    ##Regla Melta (fusion)
                                    Dmg_Melta = 0
                                    if 'Fusion' in miembro.rango[indice].claves.keys() and dist <= miembro.rango[indice].stats.get('Alcance'):
                                        Dmg_Melta = miembro.rango[indice].claves.get('Fusion')
                                        Mostrar_Mensaje(f"El arma {miembro.rango[indice].nombre} es un arma de fusión y hace {Dmg_Melta} mas de daño", False)
                                        

                                    
                                    if isinstance(m, str):
                                        dano_azar = []
                                        for x in range(0, salvar):
                                            dano_azar.append(AtkDmg_Rand(m, True)+Dmg_Melta)
                                        salvar = sum(dano_azar)
                                    else:
                                        dano = int(m) + Dmg_Melta
                                        salvar*=dano

                                    Mostrar_Mensaje(f"A que miniatura se le asignarán {salvar} heridas?")

                                    RepDmg(blanco, salvar)

                                else:
                                    Mostrar_Mensaje("")
                                    continue

                            ##Prueba de riesgo
                            if 'Riesgoso' in miembro.rango[indice].claves.keys():
                                Mostrar_Mensaje(f"Es hora de tomar una prueba de riesgo")
                                d = Dados(1, 6, True)
                                Mostrar_Mensaje(f"1D6: {d}", False)
                                lista_blanca = ['Personaje', 'Vehiculo', 'Monstruo']

                                dano = 0

                                if any(set(unidad.claves)&set(lista_blanca)) and d == 1:
                                    dano = 3
                                elif not any(set(unidad.claves)&set(lista_blanca)) and d == 1:
                                    dano = miembro.stats.get("Heridas") - miembro.dmg
                                elif d != 1:
                                    Mostrar_Mensaje(f"{miembro.nombre} ha pasado la prueba de riesgo", False)
                                    continue
                                Mostrar_Mensaje(miembro.recibir_dano(dano, unidad.habilidades))
                                continue
        
                else:
                    Mostrar_Mensaje("El arma ya fue usada")
                    continue      

    unidad.atk -= 1
    return

##Funcion de combate cuerpo a cuerpo (/Aun falta refactorizar a partir de aqui/)
def Combate(unidad, Ejer_Enem):
    with Term.fullscreen(), Term.cbreak(), Term.hidden_cursor():
        print(Term.home + Term.clear)
        
        ##Todas las unidades deben combatir 
        
        ##Verificar que la unidad esté en zona de amenaza
        if not unidad.engaged:
            print(Term.springgreen4_on_black(f"{unidad.nombre} no puede combatir, está demasiado lejos de un enemigo"))
            print(Term.springgreen4_on_black("Presiona cualquier tecla para continuar"))
            Term.inkey()
            print(Term.home + Term.clear)
            return
        else:
            ##Seleccionar un arma
            for miembro in unidad.miembros:
                indice = 0
                while True:
                    ##Romper ciclo en caso de que se halla usado un arma
                    l_armas = [x.usado for x in miembro.mele if not 'Ataques Adicionales' in x.claves.keys()]
                    l_adicionales = [x.usado for x in miembro.mele if 'Ataques Adicionales' in x.claves.keys()]
                    
                    if any(l_armas) and all(l_adicionales):
                        break

                    print(Term.home + Term.clear)
                    print(Term.springgreen4_on_black(f"Elija un arma para combatir con {miembro.nombre}:"))

                    ##Construir menú

                    for i, arma in enumerate(miembro.mele):
                        if i == indice:
                            print(Term.black_on_springgreen4(f"{i+1}. {arma.nombre}"))
                        else:
                            print(Term.springgreen4_on_black(f"{i+1}. {arma.nombre}"))

                    tecla = Term.inkey()

                    if tecla.name in ("KEY_UP", "KEY_LEFT"):
                        indice = (indice - 1 + len(miembro.mele)) % len(miembro.mele)
                        continue
        
                    elif tecla.name in ("KEY_DOWN", "KEY_RIGHT"):
                        indice = (indice + 1 + len(miembro.mele)) % len(miembro.mele)
                        continue
            
                    elif tecla.name == "KEY_ENTER" or tecla == '\n':
                        if not miembro.mele[indice].usado:

                            ##Si no se ha usado el arma elegida, seguir proceso
                            print(Term.springgreen4_on_black(f"\nElegiste: {miembro.mele[indice].nombre}"))                            
                            print(Term.home + Term.clear)

                            ##Elegir un blanco y recuperar sus claves si es valido
                            blanco = Selec_Blanco(unidad=unidad, accion='Combatir', Ejer_Enem=Ejer_Enem)
                            if blanco is None:
                                print(Term.springgreen4_on_black(f"\nCombatir no es una opción, ¡Lanzate a la batalla!"))
                                Term.inkey()                            
                                continue
                            else:
                                ##Tirada para impactar
                                print(Term.home + Term.clear)

                                n = miembro.mele[indice].stats.get("No. de Ataques")
                                
                                ##Si se repite el arma usar Tirada rapida
                                impact = []
                                nAI = Repetida(miembro.mele[indice], unidad)
                                if nAI > 1:
                                    t = f"\nMultiples miniaturas en {unidad.nombre} usan {miembro.mele[indice].nombre}\nDesea hacer una tirada rápida para combatirlas todas contra {blanco.nombre}?"
                                    r, c = Term.get_location()
                                    if Selec_SN(r, c, t):
                                        for m in unidad.miembros:
                                            for a in m.mele:
                                                if miembro.mele[indice].nombre == a.nombre and not a.usado:
                                                    impact += Dados(n, 6, False) if isinstance(miembro.mele[indice].stats.get("No. de Ataques"), int) else AtkDmg_Rand(n)
                                                    a.usado = True
                                                    if isinstance(miembro.mele[indice].claves, dict) and 'Perfil' in miembro.mele[indice].claves.keys():
                                                        for arma in miembro.mele:
                                                            if 'Perfil' in arma.claves.keys():
                                                                arma.usado = True
                                                else: continue
                                    else:
                                        miembro.mele[indice].nombre
                                        impact = Dados(n, 6, False) if isinstance(miembro.mele[indice].stats.get("No. de Ataques"), int) else AtkDmg_Rand(n)
        
                                else:
                                    ##Una vez pasado cualquier filtro se considera usada el arma
                                    miembro.mele[indice].usado = True
                                    
                                    ##Colocar como usadas las armas de perfiles opcionales
                                    if isinstance(miembro.mele[indice].claves, dict) and 'Perfil' in miembro.mele[indice].claves.keys():
                                        for arma in miembro.mele:
                                            if 'Perfil' in arma.claves.keys():
                                                arma.usado = True
                                            
                                    impact = Dados(n, 6, False) if isinstance(miembro.mele[indice].stats.get("No. de Ataques"), int) else AtkDmg_Rand(n)
                                        
                                print(Term.springgreen4_on_black(f"Se han lanzado {len(impact)} ataques"))
                                impact = [dado for dado in impact if dado >= miembro.mele[indice].stats.get("Habilidad")]
                                print(Term.springgreen4_on_black("Las tiradas para impactar exitosas:"))
                                print(Term.springgreen4_on_black(f"{impact}"))
                                print(Term.springgreen4_on_black("Presione cualquier tecla para continuar"))
                                Term.inkey()
                                if len(impact) == 0:
                                    break
                                else:
                                    
                                    if isinstance(miembro.mele[indice].claves, dict):
                                        
                                        ##Golpes sostenidos
                                        if 'Golpes Sostenidos' in miembro.mele[indice].claves.keys():
                                            nGS = miembro.mele[indice].claves.get('Golpes Sostenidos')
                                            nAd = 0
                                            print(Term.springgreen4_on_black(f"El arma {miembro.mele[indice].nombre} hace golpes sostenidos"))
                                            for dado in impact:
                                                if dado == 6:
                                                    nAd += nGS if isinstance(nGS, int) else AtkDmg_Rand(nGS, False)
                                            print(Term.springgreen4_on_black(f"Se produjeron {nAd} impactos adicionales")) 
                                            impact += [6] * nAd
  
                                        ##Impactos letales
                                        elif 'Impactos Letales' in miembro.mele[indice].claves.keys():
                                            print(Term.springgreen4_on_black(f"El arma {miembro.mele[indice].nombre} causa impactos letales"))
                                            seis = [dado for dado in impact if dado == 6]
                                            impact = [dado for dado in impact if dado != 6]
                                            print(Term.springgreen4_on_black(f"{len(seis)} impactos fueron letales"))
                                            m = miembro.mele[indice].stats.get("Daño")
                                            for d in seis:
                                                dano += m if isinstance(m, int) else AtkDmg_Rand(m, True)
                                            RepDmg(blanco, dano)
                                    
                                        ##Regla Pesada
                                        elif 'Pesado' in miembro.rango[indice].claves.keys() and unidad.mov == 3:
                                            print(Term.springgreen4_on_black(f"{unidad.nombre} no se movió en este turno y se beneficia de ello"))
                                            impact = [dado+1 for dado in impact]

                                    ##Tirada para herir
                                    herir = Dados(len(impact), 6, ret_num=False)
                                    obj = 0

                                    if miembro.mele[indice].stats.get("Fuerza") >= 2*blanco.miembros[0].stats.get("Resistencia"):
                                        obj = 2
                                    
                                    elif miembro.mele[indice].stats.get("Fuerza") > blanco.miembros[0].stats.get("Resistencia"):
                                        obj = 3
                                    
                                    elif miembro.mele[indice].stats.get("Fuerza") == blanco.miembros[0].stats.get("Resistencia"):
                                        obj = 4
                                    
                                    elif miembro.mele[indice].stats.get("Fuerza") < blanco.miembros[0].stats.get("Resistencia"):
                                        obj = 5
                                    
                                    elif miembro.mele[indice].stats.get("Fuerza")*2 <= blanco.miembros[0].stats.get("Resistencia"):
                                        obj = 6
                                        
                                    herir = [dado for dado in herir if dado >= obj]
                                    
                                    ##Regla Lanza
                                    if isinstance(miembro.mele[indice].claves, dict) and 'Lanza' in miembro.mele[indice].claves.keys() and 'Tem Pelea Primero' in unidad.habilidades.keys():
                                        herir = [dado+1 for dado in herir]
                                    
                                    ##Regla Heridas devastadoras
                                    elif isinstance(miembro.mele[indice].claves, dict) and 'Heridas devastadoras' in miembro.mele[indice].claves.keys():
                                        dev = [dado for dado in herir if dado == 6]
                                        herir = [dado for dado in herir if dado != 6]
                                        
                                        if len(dev) != 0:
                                            print(Term.black_on_springgreen4(f"{blanco.nombre} ha sufrido heridas devastadoras"))
                                            salvar = len(dev)
                                            m = miembro.mele[indice].stats.get("Daño")
                                            if isinstance(m, str):
                                                dano_azar = []
                                                for x in range(0, len(dev)):
                                                    dano_azar.append(AtkDmg_Rand(m, True) )
                                                salvar = sum(dano_azar)
                                            else:
                                                dano = int(m)
                                                salvar*=dano

                                            print(Term.black_on_springgreen4(f"A que miniatura se le asignarán {salvar} heridas?"))
                                            print(Term.springgreen4_on_black("Presione cualquier tecla para continuar"))
                                            Term.inkey()

                                            RepDmg(blanco, salvar)
                                    
                                    print(Term.springgreen4_on_black("Las tiradas que han herido:"))
                                    print(Term.springgreen4_on_black(f"{herir}\n"))
                                            
                                    if len(herir) == 0:
                                        print(Term.springgreen4_on_black("Presione cualquier tecla para continuar"))
                                        Term.inkey()
                                        break

                                    ##Regla anti
                                    if isinstance(miembro.mele[indice].claves, dict) and 'Anti' in miembro.mele[indice].claves.keys():
                                        if miembro.mele[indice].claves.get('Anti')[0] in blanco.claves:
                                            a = 0
                                            for i in herir:
                                                if i >= miembro.mele[indice].claves.get('Anti')[1]:
                                                    a += 1
                                            if a:
                                                print(Term.black_on_springgreen4(f"{blanco.nombre} ha sufrido heridas mortales!"))
                                                print(Term.black_on_springgreen4(f"A que miniatura se le asignarán las heridas?"))
                                                m = miembro.mele[indice].stats.get("Daño")
                                                if isinstance(m, str):
                                                    dano_azar = []
                                                    for x in range(0, a):
                                                        dano_azar.append(AtkDmg_Rand(m, True) )
                                                    dano = sum(dano_azar)
                                                else:
                                                    dano = int(m)
                                                    dano*=a

                                                print(Term.springgreen4_on_black("Presione cualquier tecla para continuar"))
                                                Term.inkey()

                                                RepDmg(blanco, dano)
                                                    


                                    print(Term.springgreen4_on_black(f"A continuación, permita al oponente usar la Terminal"))
                                    print(Term.springgreen4_on_black("Presione cualquier tecla para continuar"))
                                    Term.inkey()

                                    if len(blanco.miembros)==0:
                                        continue

                                    index = 0
                                    while True:
                                        print(Term.home + Term.clear)
                                        print(Term.springgreen4_on_black(f"Es momento de las tiradas de salvación de {blanco.nombre}"))
                                        print(Term.springgreen4_on_black(f"El factor de perforación del arma atacante es -{miembro.mele[indice].stats.get("Perforación")}"))
                                        
                                        salvacion = blanco.miembros[0].stats.get("Salvación")
                                        if miembro.mele[indice].stats.get("Perforación") > 0:
                                            print(Term.springgreen4_on_black(f"La salvación requerida sube a {blanco.miembros[0].stats.get("Salvación") + miembro.mele[indice].stats.get("Perforación")}"))
                                            salvacion += miembro.mele[indice].stats.get("Perforación")

                                        if 'Invulnerable' in blanco.habilidades.keys():
                                            print(Term.springgreen4_on_black(f"\nLa unidad atacada tiene una salvación invulnerable de {blanco.habilidades.get('Invulnerable')}"))
                                            print(Term.springgreen4_on_black(f"¿Que perfil desea usar?\n"))

                                            S = [f"Salvación regular: {blanco.miembros[0].stats.get('Salvación') + miembro.mele[indice].stats.get('Perforación')}+",
                                                f"Salvación invulnerable: {blanco.habilidades.get('Invulnerable')}+"]

                                            for i, opcion in enumerate(S):    #Crear lista de opciones
                                                if i == index:
                                                    print(Term.black_on_springgreen4(f"{i+1}. {opcion}"))
                                                else:
                                                    print(Term.springgreen4_on_black(f"{i+1}. {opcion}"))

                                            boton = Term.inkey()

                                            if boton.name in ("KEY_UP", "KEY_LEFT"):
                                                index = (index - 1 + len(S)) % len(S)
        
                                            elif boton.name in ("KEY_DOWN", "KEY_RIGHT"):
                                                index = (index + 1 + len(S)) % len(S)
            
                                            elif boton.name == "KEY_ENTER" or boton == '\n':
                                                if index == 0:
                                                    salvacion = blanco.miembros[0].stats.get("Salvación") + miembro.mele[indice].stats.get("Perforación")
                                                    break
                                                elif index == 1:
                                                    salvacion = blanco.habilidades.get('Invulnerable')
                                                    break
                                        
                                        if not 'Invulnerable' in blanco.habilidades.keys():
                                            print(Term.springgreen4_on_black("Presione cualquier tecla para continuar"))
                                            Term.inkey()
                                            break
                                        
                                    salvar = Dados(len(herir), 6, False)
                                    salvar = [dado for dado in salvar if dado >= salvacion]
                                    print(Term.home + Term.clear)
                                    print(Term.black_on_springgreen4(f"Se han salvado {len(salvar)} de {len(herir)} ataques"))

                                    if len(herir) > len(salvar):
                                        salvar = len(herir) - len(salvar)
                                        m = miembro.mele[indice].stats.get("Daño")
                                        if isinstance(m, str):
                                            dano_azar = []
                                            for x in range(0, salvar):
                                                dano_azar.append(AtkDmg_Rand(m, True))
                                            salvar = sum(dano_azar)
                                        else:
                                            dano = int(m)
                                            salvar*=dano

                                        print(Term.black_on_springgreen4(f"A que miniatura se le asignarán {salvar} heridas?"))
                                        print(Term.springgreen4_on_black("Presione cualquier tecla para elegir"))
                                        Term.inkey()

                                        RepDmg(blanco, salvar)

                                    else:
                                        print(Term.springgreen4_on_black("Presione cualquier tecla para continuar"))
                                        Term.inkey()
                                        continue

                                ##Prueba de riesgo
                                if isinstance(miembro.mele[indice].claves, dict) and 'Riesgoso' in miembro.mele[indice].claves.keys():
                                    print(Term.home + Term.clear)
                                    print(Term.black_on_springgreen(f"Es hora de tomar una prueba de riesgo"))
                                    d = Dados(1, 6, True)
                                    print(Term.black_on_springgreen(f"1D6: {d}"))
                                    lista_blanca = ['Personaje', 'Vehiculo', 'Monstruo']

                                    dano = 0

                                    if any(set(unidad.claves)&set(lista_blanca)) and d == 1:
                                        dano = 3
                                    elif not any(set(unidad.claves)&set(lista_blanca)) and d == 1:
                                        dano = miembro.stats.get("Heridas") - miembro.dmg
                                    elif d != 1:
                                        print(Term.black_on_springgreen(f"{miembro.nombre} ha pasado la prueba de riesgo"))
                                        print(Term.black_on_springgreen(f"Presione cualquier tecla para continuar"))
                                        Term.inkey()
                                        continue
                                    print(Term.springgreen4_on_black(miembro.recibir_dano(dano, unidad.habilidades)))
                                    print(Term.black_on_springgreen(f"Presione cualquier tecla para continuar"))
                                    Term.inkey()
                                    continue
            
                        else:
                            print("El arma ya fue usada")
                            print(Term.home + Term.clear)
                            continue      
            
                    else:
                        print(Term.springgreen4_on_black(f"\nLa tecla presionada '{tecla}' es invalida"))
                        Term.inkey()
                        continue

        unidad.atk -= 1
        return


##Reglas de movimiento
##Permanecer estatico
def Estatico(unidad, p3 = None):
    while True:
        with Term.fullscreen(), Term.cbreak(), Term.hidden_cursor():
            print(Term.springgreen4_on_black(f"La unidad {unidad.nombre} se quedara estatica"))
            print(Term.springgreen4_on_black("Presiona cualquier tecla para continuar"))
            Term.inkey()
            break
    return
    
##Movimiento normal
def Normal(unidad, p3 = None):
    with Term.fullscreen(), Term.cbreak(), Term.hidden_cursor():
        if unidad.mov == 3:
            print(Term.springgreen4_on_black(f"La unidad se moverá hasta {unidad.miembros[0].stats["Movimiento"]} pulgadas"))
            unidad.mov -= 1
            print(Term.springgreen4_on_black(f"Presione cualquier tecla para continuar"))
            Term.inkey()
            return
        else:
            print(Term.springgreen4_on_black(f"Esta unidad no se puede mover mas"))
            print(Term.springgreen4_on_black(f"Presione cualquier tecla para continuar"))
            Term.inkey()
            return
        
##Movimiento de avance
def Avance(unidad, p3 = None):
    with Term.fullscreen(), Term.cbreak(), Term.hidden_cursor():
        if unidad.mov == 3:
            temp = Dados(1, 6)
            print(Term.springgreen4_on_black(f"1D6: {temp}"))
            print(Term.springgreen4_on_black(f"La unidad avanzará hasta {unidad.miembros[0].stats["Movimiento"]}'' + {temp}'' "))
            unidad.mov -= 2
            unidad.atk -= 2
            print(Term.springgreen4_on_black(f"Presione cualquier tecla para continuar"))
            Term.inkey()
            return
        else:
            print(Term.springgreen4_on_black(f"Esta unidad no se puede mover mas"))
            print(Term.springgreen4_on_black(f"Presione cualquier tecla para continuar"))
            Term.inkey()
            return      

##Movimiento de retroceder/Huida
def Retroceder(unidad, p3 = None):
    with Term.fullscreen(), Term.cbreak(), Term.hidden_cursor():
        whitelist = ["Volador", "Titanico"]
        if unidad.shock == True or not any(unidad.claves & whitelist):
            print(Term.springreen4_on_black("La unidad realizara una huida desesperada!"))
            for mini in unidad.miembros:
                d = Dados(1, 3)
                if d < 2:
                    print("Una miniatura no ha pasado la prueba!")
                    print("Elije cual será eliminada: ")
                    indice = Selec_mini(unidad)
                    if indice == None:
                        break
                    print(Term.springgreen4_on_black(unidad.miembros[indice].recibir_dano(unidad.miembros.stats["Heridas"], unidad.habilidades)))
                    unidad.eliminar_muertos()
            print("La huida desesperada ha Terminado")
            print("Presione cualquier tecla para continuar")
            Term.inkey()
            unidad.mov -= 3
            unidad.atk -= 3
            unidad.engaged = False
            return
        
        else:
            print(Term.springreen4_on_black(f"La unidad retrocederá hasta {unidad.miembros[0].stats.get("Movimiento")}'' "))
            print(Term.springreen4_on_black("Recuerde que las miniaturas no pueden Terminar este movimiento en zona de amenaza de una unidad enemiga"))
            print(Term.springreen4_on_black("\nPresione cualquier tecla para continuar"))
            Term.inkey()
            unidad.mov -= 3
            unidad.atk -= 3
            unidad.engaged = False
            return

##Cargar
def Carga(unidad, blanco):
    CadenaIngreso = ''
    if unidad.atk <= 2 and unidad.mov <= 2:
        print(Term.springgreen4_on_black(f"{unidad.nombre} ya no puede cargar"))
        Term.inkey()
        return
    while True:
        with Term.fullscreen(), Term.cbreak(), Term.hidden_cursor():
            if blanco is not None:
                print(Term.home + Term.clear)
                print(Term.on_black)
                print(Term.springgreen4_on_black(f"Ingrese la distancia entre {unidad.nombre} y {blanco.nombre}"))
                print(Term.springgreen4_on_black(CadenaIngreso))
        
                tecla = Term.inkey()

                if tecla and (tecla.is_sequence == False):
                    CadenaIngreso += tecla
                    print(Term.move_x(0), end='')
                    print(Term.springgreen4_on_black(f"{CadenaIngreso}"), end='', flush=True)
                    continue
            
                elif tecla.name == "KEY_ENTER":
                    print(Term.springgreen4_on_black(f"\nIngresaste: {CadenaIngreso}''"))
                    print(Term.springgreen4_on_black("\nPresiona ENTER para continuar"))
                    print(Term.springgreen4_on_black("\nPresiona cualquier tecla para reintentar"))
            
                    tecla = Term.inkey()
            
                    if tecla.name == "KEY_ENTER" or tecla == '\n':
                        dis = int(CadenaIngreso)
                        d = Dados(2, 6)
                        print(Term.springgreen4_on_black(f"2D6: {d}"))
                        if d < dis:
                            print(Term.springgreen4_on_black(f"La unidad {unidad.nombre} ha fallado la carga!"))
                            unidad.mov -= 2
                            unidad.atk -= 2
                            print(Term.springgreen4_on_black(f"Presione cualquier tecla para continuar"))
                            Term.inkey()
                            return

                        else:
                            print(Term.springgreen4_on_black(f"La unidad ha cargado con exito!"))
                            unidad.mov -= 2
                            unidad.atk -= 2
                            unidad.habilidades.update({"Tem Pelea Primero": None})
                            unidad.engaged = True
                            print(Term.springgreen4_on_black(f"Presione cualquier tecla para continuar"))
                            Term.inkey()
                            return
                
                    else:
                        CadenaIngreso = ''
                        print(Term.home + Term.clear)
                        print(Term.on_black)
                        print(Term.springgreen4_on_black(f"Ingrese la distancia entre {unidad.nombre} y {blanco.nombre}"))
                        continue
            
            else:
                break


##Estratagemas
def ReRoll(Ej, Lista_D, val, DX):
    if Ej.pc:
        Ej.pc -= 1
        for j in Lista_D:
            if j < val:
                Lista_D.pop(j)
                Lista_D.append(Dados(1, DX))
                break

def Overwatch(unidad, blanco):
    if (unidad.atk)>=1:
        print(Term.springgreen4_on_black(f"{unidad.nombre} va a disparar a {blanco.nombre} usando el estratagema 'overwatch'"))
        Disparo(unidad, blanco)
        return
        
    else: 
        print(Term.springgreen4_on_black(f"Tu ere pobre tu no tiene aifon"))
        return

def Granadas(unidad, blanco):
        if ("Granadas" in unidad.claves):
            ##disparo() modificado
            Disparo(unidad, blanco)
            return

##Otras reglas
##Combatir con regla "Pelea Primero" v3 (yield) #Menos iteraciones por la lista
def Pelea_Primero(ejercito):
    for i in ejercito.unidades:
        if "Tem Pelea Primero" in i.habilidades or "Pelea Primero" in i. habilidades:
            if i.engaged:
                yield i
    
    for i in ejercito.unidades:
            if not "Tem Pelea Primero" in i.habilidades or not "Pelea Primero" in i. habilidades:
                if i.engaged:
                    yield i 

def Repetida(arma, unidad):   ##Devuelve el número de veces que un arma está repetida en una unidad
    nombre = arma.nombre
    n = 0
    for miembro in unidad.miembros:
        if nombre in [x.nombre for x in miembro.rango if x.usado == False]:
            n+=1
    for miembro in unidad.miembros:
        if nombre in [x.nombre for x in miembro.mele if x.usado == False]:
            n+=1
    return n

##Regla final violento
def FinViol(dic_habs, nombre, Ejers):
    indice = 0
    while True:
        with Term.fullscreen(), Term.cbreak(), Term.hidden_cursor():
            
            n_heridas = dic_habs.get('Final Violento') if isinstance(dic_habs.get('Final Violento'), int) else AtkDmg_Rand(dic_habs.get('Final Violento'), True)
            
            print(Term.home + Term.clear)
            print(Term.on_black)
            print(Term.springgreen4_on_black(f"{nombre} ha muerto con un final violento"))
            print(Term.springgreen4_on_black(f"Todas las unidades a 6'' o menos sufrirán {n_heridas}\n"))
            print(Term.springgreen4_on_black("Seleccionelas a continuación:"))

            All_u = []
            for e in Ejers:
                All_u += e.unidades
    
            for i, opcion in enumerate(All_u + ["Terminar"]):    #Crear lista de opciones
                if i == indice:
                    print(Term.black_on_springgreen4(f"{i+1}. {opcion.nombre if isinstance(opcion, Unidad) else opcion}"))
                else:
                    print(Term.springgreen4_on_black(f"{i+1}. {opcion.nombre if isinstance(opcion, Unidad) else opcion}"))
    
            tecla = Term.inkey()
    
            if tecla.name in ("KEY_UP", "KEY_LEFT"):
                indice = (indice - 1 + len(All_u + ["Terminar"])) % len(All_u + ["Terminar"])
        
            elif tecla.name in ("KEY_DOWN", "KEY_RIGHT"):
                indice = (indice + 1 + len(All_u + ["Terminar"])) % len(All_u + ["Terminar"])
            
            elif tecla.name == "KEY_ENTER" or tecla == '\n':
                if indice > len(All_u)-1:
                    print(Term.springgreen4_on_black(f"\nElegiste: Terminar"))
                    return
                else:
                    print(Term.springgreen4_on_black(f"\nElegiste: {All_u[indice].nombre}"))
                    print(Term.springgreen4_on_black(f"Presione cualquier tecla para continuar"))

                    Term.inkey()
                    
                    RepDmg(All_u[indice], n_heridas)
                    continue 
                    
            else:
                print(Term.springgreen4_on_black(f"\nLa tecla presionada '{tecla}' es invalida"))
                Term.inkey()

##Regla empeorar stats si hay daños
def Danado(unidad):
    ## 1 a 4 heridas -> resta 1 a tirada para herir
    ## 1 a 5 heridas -> resta 1 "
    
    return


##Listas de funciones
MOVIMIENTO_F = [
    Normal,
    Estatico,
    Avance,
    Retroceder
]

CARGA_F = [
    Carga,
    Estatico
]
