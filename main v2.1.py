import random as rand
import json
import blessed
import sys
import time

#Función de dados
def Dados(n_dados):
    res_dados=[]
    res_dados = [rand.randint(1, 6) for _ in range(1, (n_dados+1))]
    return res_dados

StatsTx = ["Movimiento", "Resistencia", "Salvación",
           "Heridas", "Liderazgo", "Control de objetivo"]   #Nombre de las stats de las miniaturas

ArmaTx = ["Nombre", "Alcance", "No. de Ataques",
          "Habilidad", "Fuerza", "Perforación", "Daño"] #Nombre de las stats de las armas

#Inicializar ventana
term = blessed.Terminal()

#Menú
DISPONIBLE = [
    'Tyranidos v1',
    'Space Marines v1',
    'salir'
]

Ejercitos_diccionarios = [] #Diccionarios provenientes de los JSON

##Elegir ejercitos
Indice_ejercito = 0
with term.fullscreen(), term.cbreak(), term.hidden_cursor():
    while True:
        print(term.home + term.clear)
        print(term.on_black)
        print(term.springgreen4_on_black("Elige un ejercito:\n"))
    
        for i, opcion in enumerate(DISPONIBLE):    #Crear lista de opciones
            if i == Indice_ejercito:
                print(term.black_on_springgreen4(f"{i+1}. {opcion}"))
            else:
                print(term.springgreen4_on_black(f"{i+1}. {opcion}"))
    
        tecla = term.inkey()
    
        if tecla.name in ("KEY_UP", "KEY_LEFT"):
            Indice_ejercito = (Indice_ejercito - 1 + len(DISPONIBLE)) % len(DISPONIBLE)
        
        elif tecla.name in ("KEY_DOWN", "KEY_RIGHT"):
            Indice_ejercito = (Indice_ejercito + 1 + len(DISPONIBLE)) % len(DISPONIBLE)
            
        elif tecla.name == "KEY_ENTER" or tecla == '\n':
            if Indice_ejercito == len(DISPONIBLE) - 1:
                sys.exit()
            else:
                print(term.springgreen4_on_black(f"\nElegiste {DISPONIBLE[Indice_ejercito]}"))
                #Constructor de unidades 
                match (Indice_ejercito%len(DISPONIBLE)):
                    case 0:
                        with open('Ty_patrol.json', 'r') as file:
                            Ejercitos_diccionarios.append(json.load(file))
                        if len(Ejercitos_diccionarios) == 2:
                            break
                        else: term.inkey()
                    
                    case 1:
                        with open('UM_patrol.json', 'r') as file:
                            Ejercitos_diccionarios.append(json.load(file))
                        if len(Ejercitos_diccionarios)  == 2:
                            break
                        else: term.inkey()
                    
        else:
            print(term.springgreen4_on_black(f"\nLa tecla presionada '{tecla}' es invalida"))
            term.inkey()

##Establecer limite de rondas
limite = 0
CadenaIngreso = ''
with term.fullscreen(), term.cbreak(), term.hidden_cursor():
    time.sleep(1)
    print(term.home + term.clear)
    print(term.springgreen4_on_black("Ingrese el limite de rondas"))
    
    while True:
        
        tecla = term.inkey()
        
        if tecla and (tecla.is_sequence == False):
            CadenaIngreso += tecla
            print(term.move_x(0), end='')
            print(term.springgreen4_on_black(f"{CadenaIngreso}"), end='', flush=True)
            continue
        
        elif tecla.name == "KEY_ENTER":
            print(term.springgreen4_on_black(f"\nIngresaste: {CadenaIngreso}"))
            print(term.springgreen4_on_black("\nPresiona ENTER para continuar"))
            print(term.springgreen4_on_black("\nPresiona cualquier tecla para reintentar"))
            
            tecla = term.inkey()
            
            if tecla.name == "KEY_ENTER" or tecla == '\n':
                limite = int(CadenaIngreso)
                break
            else:
                CadenaIngreso = ''
                print(term.home + term.clear)
                print(term.on_black)
                print(term.springgreen4_on_black("Ingrese el limite de rondas"))
                continue

##Clases
class Individuo:
    def __init__(self, diccionario):
        self.nombre = diccionario.get("Nombre")    #Nombre de la miniatura
        self.stats_base = dict(zip(StatsTx, diccionario.get("Stats"))) #Stats de la miniatura
        self.rango1 = dict(zip(ArmaTx, diccionario.get("Rango1"))) if diccionario.get("Rango1") is not None else None # Armas de rango
        self.rango2 = dict(zip(ArmaTx, diccionario.get("Rango2"))) if diccionario.get("Rango2") is not None else None
        self.rango3 = dict(zip(ArmaTx, diccionario.get("Rango3"))) if diccionario.get("Rango3") is not None else None
        self.rango4 = dict(zip(ArmaTx, diccionario.get("Rango4"))) if diccionario.get("Rango4") is not None else None
        self.mele1 = dict(zip(ArmaTx, diccionario.get("Mele1"))) if diccionario.get("Mele1") is not None else None    # Armas cuerpo a cuerpo
        self.mele2 = dict(zip(ArmaTx, diccionario.get("Mele2"))) if diccionario.get("Mele2") is not None else None
        self.dmg = 0    #Daño recibido por la miniatura
        self.vivo = True    #La miniatura esta viva

    def recibir_dano(self, dano):
        self.dmg += dano
        if self.dmg >= self.stats_base["Heridas"]:  # Si daño >= heridas
            self.vivo = False
            print(f"{self.nombre} ha muerto.")

    def __repr__(self):
        estado = "Vivo" if self.vivo else "Muerto"
        return f"{self.nombre} ({estado})"

class Unidad:
    def __init__(self, diccionario):
        self.mov = 0
        self.atk = 0
        self.shock = False
        self.miembros = []
        self.nombre = diccionario.get("Nombre")
        self.lider = ''
        self.habilidades = diccionario.get("Habilidades")
        self.claves = diccionario.get("Claves")
        self.nm = diccionario.get("Numero Miniaturas")

    def eliminar_muertos(self):
        self.miembros = [
            Individuo for mini in self.miembros if Individuo.vivo == False]

    def __repr__(self):
        return f"{self.nombre}:\n" + "\n".join(str(miembro) for miembro in self.miembros)

class Ejercito:
    def __init__(self, diccionario):
        self.pc = 0
        self.pv = 0
        self.faccion = diccionario.get('Faccion')
        self.nu = diccionario.get('Numero Unidades')
        self.unidades = []

    def __repr__(self):
        return f"{self.faccion}:\n" + "\n".join(str(unidad) for unidad in self.unidades)

Ejercitos_objetos =[]   #Lista donde se guardaran los ejercitos convertidos en objetos de Python

i = 0
for d in Ejercitos_diccionarios:    #iterar por lista de diccionarios
    j = 0
    if isinstance(d, dict):     #Determinar si el objeto es un diccionario
        Ejercitos_objetos.append(Ejercito(d))   #Crear el objeto ejercito
        for cu, vu in d.items():    #iterar por diccionario
            if isinstance(vu, dict):    #Determinar si el objeto es un subdiccionario
                Ejercitos_objetos[i].unidades.append(Unidad(vu))    #Crear el objeto unidad y añadirlo a un ejercito
                for cm, vm in vu.items():   #Iterar por el subdiccionario
                    if isinstance(vm, dict) and cm != 'Habilidades':    #Determinar si el objeto es un subsubdiccionario y no es el diccionario de habilidades
                        Ejercitos_objetos[i].unidades[j].miembros.append(Individuo(vm))     #Crear el objeto individuo y añadirlo a una unidad
                j += 1
        i += 1

#Determinar turno
turno = 0
with term.fullscreen(), term.cbreak(), term.hidden_cursor():
    while True:
        
        while turno == 0:
            print(term.home + term.clear)
            print(term.on_black)
            print(term.springgreen4_on_black("Determinando los turnos"))
        
            comenzar = Dados(2)
            print(term.springgreen4_on_black(f"Dado Jugador 1 ({Ejercitos_objetos[0].faccion}): {comenzar[0]}"))
            print(term.springgreen4_on_black(f"Dado Jugador 2 ({Ejercitos_objetos[1].faccion}): {comenzar[1]}"))
            if comenzar[0] > comenzar[1]:
                print(term.springgreen4_on_black("\nComienza el jugador 1"))
                turno = 0
                break
            if comenzar[0] < comenzar[1]:
                print(term.springgreen4_on_black("\nComienza el jugador 2"))
                turno = 1
                break
            else: continue

#Actua el jugador Ejercitos_objetos[turno%2]

##Bucle de partida

##Funciones estandar
def disparo(unidad, blanco):
    ##SI
    print(f"La {unidad} va a tronarse a {blanco}")

##Estratagemas
def overwatch(unidad, blanco):
    if (unidad.atk)>=1:
        print(f"{unidad.nombre} va a disparar a {blanco.nombre} usando el estratagema 'overwatch'")
        disparo(unidad, blanco)
    else: print("Tu ere pobre tu no tiene aifon")
    unidad.atk-=2

def granadas(unidad, blanco):
    for i in unidad:
        if (any("granadas") in unidad.claves):
            ##disparo() modificado
            disparo(unidad, blanco)
             
