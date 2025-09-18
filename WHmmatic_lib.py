'''
Librería de funciones utilizadas en Warhammatic
Creada por Guser_06 como proyecto personal para facilitar el juego Warhammer 40k 10ma edición
Se recomienda leer este modulo y sus comentarios para entender la estructura bajo la
que se esta programando el archivo 'main vx.x.py'
'''
##Librerías
import random as rand

##Listas formadoras de diccionarios
##Usar como claves para obtener datos en interacciones
StatsTx = ["Movimiento", "Resistencia", "Salvación",
           "Heridas", "Liderazgo", "Control de objetivo"]   #Nombre de las stats de las miniaturas

ArmaTx = ["Alcance", "No. de Ataques",
          "Habilidad", "Fuerza", "Perforación", "Daño"] #Nombre de las stats de las armas


##Clases
class Arma:
    def __init__(self, diccionario):
        self.nombre = diccionario.get("Nombre")
        self.stats = dict(zip(ArmaTx, diccionario.get("stats")))
        self.claves = diccionario.get("Claves")
        self.usado = False
    
    def reboot(self):
        self.usado = False

class Individuo:
    def __init__(self, diccionario):
        self.nombre = diccionario.get("Nombre")    #Nombre de la miniatura
        self.stats_base = dict(zip(StatsTx, diccionario.get("Stats"))) #Stats de la miniatura
        self.rango = [] # Armas de rango
        self.mele = [] # Armas cuerpo a cuerpo
        self.dmg = 0    #Daño recibido por la miniatura
        self.vivo = True    #La miniatura esta viva

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

    def recibir_dano(self, dano):
        self.dmg += dano
        if self.dmg >= self.stats_base["Heridas"]:  # Si daño >= heridas
            self.vivo = False
            return f"{self.nombre} ha muerto."

    def __repr__(self):
        estado = "Vivo" if self.vivo else "Muerto"
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
            mini for mini in self.miembros if mini.vivo == True]
    
    def __repr__(self):
        return f"{self.nombre}:\n" + "\n".join(str(miembro) for miembro in self.miembros) + ("\nAcobardado" if self.shock else "")

class Lider(Unidad):
    def __init__(self, diccionario):
        Unidad.__init__(self, diccionario = diccionario)
        self.liderando = True
    
    def AddLider(self, ej):
        for i in ej.unidades:
            if isinstance(i.posLid, list) and i.lider == '':
                for x in i.posLid:
                    if x == self.nombre:
                        i.lider = self.nombre
                        i.miembros += self.miembros
                        i.habilidades = i.habilidades|self.habilidades
                        i.nm += self.nm
                        i.claves += self.claves
                        return -1
        else:
            self.liderando = False
            ej.unidades.append(self)
            return 0

class Ejercito:
    def __init__(self, diccionario):
        self.pc = 0
        self.pv = 0
        self.faccion = diccionario.get('Faccion')
        self.nu = diccionario.get('Numero Unidades')
        self.unidades = []

    def eliminar_unidades(self):
        self.unidades =[
            Unidad for uni in self.unidades if any in Unidad.miembros
        ]
    
    def __repr__(self):
        return f"{self.faccion}:\n" + "\n".join(str(unidad) for unidad in self.unidades)

#Función de dados
def Dados(n_dados, Dx, ret_num = True): #Numero de dados que se desean, Numero de caras del dado a lanzar
    ##ret_type False devuelve lista de valores, True devuelve la suma
    res_dados = [rand.randint(1, int(Dx)) for _ in range(0, int(n_dados))]
    if ret_num:
        res_dados = sum(res_dados)
    return res_dados

def AtkDmg_Rand(nDX):
    res = []
    ud = str(nDX).find('D')
    cantidad = int(str(nDX)[ud-1]) if ud != 0 else 1
    cantidad = Dados(cantidad, int(str(nDX)[ud+1]), True)
    if '+' in str(nDX):
        um = str(nDX).find('+')
        cantidad += int(str(nDX[um+1]))
    res += Dados(cantidad, int(str(nDX)[ud+1]), False)
    return res
    
##Funciones estandar

##Aumentar puntos de comando
def Aumentar_PC(Ejer_Obj):
    for i in Ejer_Obj:
        i.pc += 1
    return

def Aumentar_Mov_Atk(Ejercito):
    for u in Ejercito.unidades:
        u.mov = 3
        u.atk = 3
    return

def Shock_Test(unidad, term):
    with term.fullscreen(), term.cbreak(), term.hidden_cursor():

        while True:
            print(term.home + term.clear)
            if len(unidad.miembros)<(unidad.nm/2) and (unidad.nm != 1):
                mayor = 0
                for mini in unidad.miembros:
                    if mini.stats_base.get("Liderazgo") > mayor:
                        mayor = mini.stats_base.get("Liderazgo")
                
                prueba = Dados(2, 6)
                if prueba < mayor:   
                    unidad.shock = True
                    print(term.springgreen4_on_black(unidad.__repr__()))
                    print(term.springgreen4_on_black("Presione cualquier tecla para continuar"))
                    term.inkey()
                    break
        
                else:
                    unidad.shock = False
                    print(term.springgreen4_on_black(unidad.__repr__()))
                    print(term.springgreen4_on_black("Presione cualquier tecla para continuar"))
                    term.inkey()
                    break
        
            elif unidad.nm == 1 and unidad.miembros[0].dmg > unidad.miembros[0].stats_base.get("Heridas"):
                prueba = Dados(2, 6)
                if prueba < unidad.miembros[0].stats_base.get("Liderazgo"):   
                    unidad.shock = True
                    print(term.springgreen4_on_black(unidad.__repr__()))
                    print(term.springgreen4_on_black("Presione cualquier tecla para continuar"))
                    term.inkey()
                    break
        
                else:
                    unidad.shock = False
                    print(term.springgreen4_on_black(unidad.__repr__()))
                    print(term.springgreen4_on_black("Presione cualquier tecla para continuar"))
                    term.inkey()
                    break
                
            else: 
                print(term.springgreen4_on_black(f"La unidad {unidad.nombre} paso la prueba"))
                print(term.springgreen4_on_black("Presione cualquier tecla para continuar"))
                term.inkey()
                break
    return
    
    
def Disparo(term, unidad, Ejer_Enem):
    whitelist = ["Vehiculo", "Monstruo", "Pistola", "Asalto"]
    graylist = ["Vehiculo", "Monstruo", ]
    with term.fullscreen(), term.cbreak(), term.hidden_cursor():
        print(term.home + term.clear)
        keysu = []
        keysu = set(keysu)
        ##Buscar claves de armas
        for miembro in unidad.miembros:
            for arma in miembro.rango:
                keysu|=(arma.claves.keys()) & set(whitelist)
        keysu|=(set(unidad.claves) & set(whitelist))
        
        ##Verificar que la unidad no haya retrocedido
        if unidad.atk == 0:
            print(term.springgreen4_on_black(f"{unidad.nombre} ya no puede disparar en este turno"))
            print(term.springgreen4_on_black("Presiona cualquier tecla para continuar"))
            term.inkey()
            print(term.home + term.clear)
            return
            
        ##Verificar que la unidad tenga armas de rango
        for miembro in unidad.miembros:
            if len(miembro.rango) != 0:
                break
        else:
            print(term.springgreen4_on_black(f"{unidad.nombre} no tiene armas para disparar"))
            print(term.springgreen4_on_black("Presiona cualquier tecla para continuar"))
            term.inkey()
            print(term.home + term.clear)
            return
        
        ##Verificar que la unidad no esté en zona de amenaza
        if unidad.engaged == True and not any(unidad.claves & whitelist):
            print(term.springgreen4_on_black(f"{unidad.nombre} no puede disparar, está demasiado cerca de un enemigo"))
            print(term.springgreen4_on_black("Presiona cualquier tecla para continuar"))
            term.inkey()
            print(term.home + term.clear)
            return
        else:
            ##Seleccionar un arma
            for miembro in unidad.miembros:
                indice = 0
                while True:
                    ##Romper ciclo en caso de que se hallan usado todas las armas
                    if all([x.usado for x in miembro.rango]):
                        break

                    print(term.home + term.clear)
                    print(term.springgreen4_on_black(f"Elija un arma para disparar con {miembro.nombre}:"))

                    ##Construir menú

                    for i, arma in enumerate(miembro.rango):
                        if i == indice:
                            print(term.black_on_springgreen4(f"{i+1}. {arma.nombre}"))
                        else:
                            print(term.springgreen4_on_black(f"{i+1}. {arma.nombre}"))

                    tecla = term.inkey()

                    if tecla.name in ("KEY_UP", "KEY_LEFT"):
                        indice = (indice - 1 + len(miembro.rango)) % len(miembro.rango)
                        continue
        
                    elif tecla.name in ("KEY_DOWN", "KEY_RIGHT"):
                        indice = (indice + 1 + len(miembro.rango)) % len(miembro.rango)
                        continue
            
                    elif tecla.name == "KEY_ENTER" or tecla == '\n':
                        if not miembro.rango[indice].usado:
                            ##Si no se ha usado el arma elegida, seguir proceso
                            print(term.springgreen4_on_black(f"\nElegiste: {miembro.rango[indice].nombre}"))
                            print(term.home + term.clear)

                            ##Elegir un blanco y recuperar sus claves
                            blanco = Selec_Blanco(term=term, unidad=unidad, accion='Disparar', Ejer_Enem=Ejer_Enem)
                            miembro.rango[indice].usado = True
                            if blanco is None:
                                break

                            keysb = []
                            keysb = set(keysb)
                            keysb|=(set(blanco.claves) & set(graylist))

                            ##Ingresar distancia
                            CadenaIngreso = ''
                            dist = 0
                            print(term.home + term.clear)
                            print(term.springgreen4_on_black(f"Ingrese la distancia entre {unidad.nombre} y {blanco.nombre}"))
                            while True:

                                key = term.inkey()

                                if key and (key.is_sequence == False):
                                    CadenaIngreso += key
                                    print(term.move_x(0), end='')
                                    print(term.springgreen4_on_black(f"{CadenaIngreso}"), end='', flush=True)
                                    continue
        
                                elif key.name == "KEY_ENTER":
                                    print(term.springgreen4_on_black(f"\nIngresaste: {CadenaIngreso}"))
                                    print(term.springgreen4_on_black("\nPresiona ENTER para continuar"))
                                    print(term.springgreen4_on_black("\nPresiona cualquier tecla para reintentar"))
            
                                    key = term.inkey()

                                    if key.name == "KEY_ENTER" or key == '\n':
                                        dist = int(CadenaIngreso)
                                        break
                                    else:
                                        CadenaIngreso = ''
                                        print(term.home + term.clear)
                                        print(term.on_black)
                                        print(term.springgreen4_on_black(f"Ingrese la distancia entre {unidad.nombre} y {blanco.nombre}"))
                                        continue

                            ##Verificar alcance
                            if dist > miembro.rango[indice].stats.get("Alcance"):
                                print(term.springgreen4_on_black(f"El blanco elegido está fuera del alcance de {miembro.rango[indice].nombre}"))
                                break

                            else:
                                ##Tirada para impactar
                                print(term.home + term.clear)
                                n = miembro.rango[indice].stats.get("No. de Ataques")
                                impact = Dados(n, 6, False) if isinstance(miembro.rango[indice].stats.get("No. de Ataques"), int) else AtkDmg_Rand(n)
                                impact = [dado for dado in impact if dado >= miembro.rango[indice].stats.get("Habilidad")]
                                print(term.springgreen4_on_black(f"Se han lanzado {miembro.rango[indice].stats.get("No. de Ataques")} ataques"))
                                print(term.springgreen4_on_black("Las tiradas para impactar exitosas:"))
                                print(term.springgreen4_on_black(f"{impact}"))
                                print(term.springgreen4_on_black("Presione cualquier tecla para continuar"))
                                term.inkey()
                                if len(impact) == 0:
                                    break
                                else:
                                        
                                    ##Tirada para herir
                                    herir = Dados(len(impact), 6, ret_num=False)
                                    if miembro.rango[indice].stats.get("Fuerza") >= 2*blanco.miembros[0].stats_base.get("Resistencia"):
                                        herir = [dado for dado in herir if dado >= 2]
                                    
                                    elif miembro.rango[indice].stats.get("Fuerza") > blanco.miembros[0].stats_base.get("Resistencia"):
                                        herir = [dado for dado in herir if dado >= 3]
                                    
                                    elif miembro.rango[indice].stats.get("Fuerza") == blanco.miembros[0].stats_base.get("Resistencia"):
                                        herir = [dado for dado in herir if dado >= 4]
                                    
                                    elif miembro.rango[indice].stats.get("Fuerza") < blanco.miembros[0].stats_base.get("Resistencia"):
                                        herir = [dado for dado in herir if dado >= 5]
                                    
                                    elif miembro.rango[indice].stats.get("Fuerza")*2 <= blanco.miembros[0].stats_base.get("Resistencia"):
                                        herir = [dado for dado in herir if dado >= 6]

                                    print(term.springgreen4_on_black("Las tiradas que han herido:"))
                                    print(term.springgreen4_on_black(f"{herir}\n"))
                                    if len(herir) == 0:
                                        print(term.springgreen4_on_black("Presione cualquier tecla para continuar"))
                                        term.inkey()
                                        break

                                    print(term.springgreen4_on_black(f"A continuación, permita al oponente usar la terminal"))
                                    print(term.springgreen4_on_black("Presione cualquier tecla para continuar"))
                                    term.inkey()
                                    print(term.home + term.clear)
                                    print(term.springgreen4_on_black(f"Es momento de las tiradas de salvación de {blanco.nombre}"))
                                    print(term.springgreen4_on_black(f"El factor de perforación del arma atacante es -{miembro.rango[indice].stats.get("Perforación")}"))
                                    
                                    salvacion = blanco.miembros[0].stats_base.get("Salvación")
                                    if miembro.rango[indice].stats.get("Perforación") > 0:
                                        print(term.springgreen4_on_black(f"La salvación requerida sube a {blanco.miembros[0].stats_base.get("Salvación") + miembro.rango[indice].stats.get("Perforación")}"))
                                        salvacion += miembro.rango[indice].stats.get("Perforación")

                                    if 'Invulnerable' in blanco.habilidades.keys():
                                        print(term.springgreen4_on_black(f"\nLa unidad atacada tiene una salvación invulnerable de {blanco.habilidades.get('Invulnerable')}"))
                                        print(term.springgreen4_on_black(f"¿Que perfil desea usar?\n"))

                                        index = 0
                                        while True:
                                            S = [f"Salvación regular: {blanco.miembros[0].stats_base.get('Salvación') + miembro.rango[indice].stats.get('Perforación')}+",
                                                f"Salvación invulnerable: {blanco.habilidades.get('Invulnerable')}+"]

                                            for i, opcion in enumerate(S):    #Crear lista de opciones
                                                if i == index:
                                                    print(term.black_on_springgreen4(f"{i+1}. {opcion}"))
                                                else:
                                                    print(term.springgreen4_on_black(f"{i+1}. {opcion}"))

                                            boton = term.inkey()

                                            if boton.name in ("KEY_UP", "KEY_LEFT"):
                                                index = (index - 1 + len(S)) % len(S)
        
                                            elif boton.name in ("KEY_DOWN", "KEY_RIGHT"):
                                                index = (index + 1 + len(S)) % len(S)
            
                                            elif boton.name == "KEY_ENTER" or boton == '\n':
                                                if index == 0:
                                                    salvacion = blanco.miembros[0].stats_base.get("Salvación") + miembro.rango[indice].stats.get("Perforación")
                                                    break
                                                elif index == 1:
                                                    salvacion = blanco.habilidades.get('Invulnerable')
                                                    break
                                        
                                    salvar = Dados(len(herir), 6, False)
                                    salvar = [dado for dado in salvar if dado >= salvacion]
                                    print(term.home + term.clear)
                                    print(term.black_on_springgreen4(f"Se han salvado {len(salvar)} de {len(herir)} ataques"))

                                    if len(herir) > len(salvar):
                                        print(term.black_on_springgreen4(f"A que miniatura se le asignarán las heridas?"))
                                        salvar = len(herir) - len(salvar)
                                        m = miembro.rango[indice].stats.get("Daño")
                                        if isinstance(m, str):
                                            dano = sum(AtkDmg_Rand(m))
                                        else:
                                            dano = int(m)
                                        salvar*=dano

                                        print(term.springgreen4_on_black("Presione cualquier tecla para continuar"))
                                        term.inkey()

                                        while salvar >= 1:
                                            danada = Selec_mini(term, blanco)
                                            if salvar >= blanco.miembros[danada].stats_base.get("Heridas"):
                                                print(term.springgreen4_on_black(f"{blanco.miembros[danada].recibir_dano(blanco.miembros[danada].stats_base.get("Heridas"))}"))
                                                print(term.springgreen4_on_black("Presione cualquier tecla para continuar"))
                                                term.inkey()
                                                salvar -= blanco.miembros[danada].stats_base.get("Heridas")
                                                blanco.eliminar_muertos()
                                                continue
                                            else:
                                                blanco.miembros[danada].recibir_dano(salvar)
                                                print(term.springgreen4_on_black(f"{blanco.miembros[danada].__repr__()}\nHeridas recibidas: {blanco.miembros[danada].dmg}"))
                                                print(term.springgreen4_on_black("Presione cualquier tecla para continuar"))
                                                term.inkey()
                                                salvar = 0
                                                break

                
                        else:
                            print("El arma ya fue usada")
                            print(term.home + term.clear)
                            continue      
                
                    else:
                        print(term.springgreen4_on_black(f"\nLa tecla presionada '{tecla}' es invalida"))
                        term.inkey()
                        continue


def Combate(unidad, blanco, term):
    while True:
        with term.fullscreen(), term.cbreak(), term.hidden_cursor():
            if unidad.engaged and blanco is not None:
                print(term.springgreen4_on_black(f"La {unidad.nombre} va a tronarse a {blanco.nombre}"))
                if "Tem Pelea Primero" in unidad.habilidades:
                    unidad.habilidades.remove("Tem Pelea Primero")
            else:
                break

            print(term.springgreen4_on_black("Presiona cualquier tecla para continuar"))
            term.inkey()
            blanco.eliminar_muertos()
            break
    return


def Estatico(term, unidad, p3 = None):
    while True:
        with term.fullscreen(), term.cbreak(), term.hidden_cursor():
            print(term.springgreen4_on_black(f"La unidad {unidad.nombre} se quedara estatica"))
            unidad.mov = 1
            print(term.springgreen4_on_black("Presiona cualquier tecla para continuar"))
            term.inkey()
            break
    return
    
def Normal(term, unidad, p3 = None):
    with term.fullscreen(), term.cbreak(), term.hidden_cursor():
        if unidad.mov >= 1:
            print(term.springgreen4_on_black(f"La unidad se moverá hasta {unidad.miembros[0].stats_base["Movimiento"]} pulgadas"))
            unidad.mov = 1
            print(term.springgreen4_on_black(f"Presione cualquier tecla para continuar"))
            term.inkey()
            return
        else:
            print(term.springgreen4_on_black(f"Esta unidad no se puede mover mas"))
            print(term.springgreen4_on_black(f"Presione cualquier tecla para continuar"))
            term.inkey()
            return
        

def Avance(term, unidad, p3 = None):
    with term.fullscreen(), term.cbreak(), term.hidden_cursor():
        if unidad.mov >= 2:
            temp = Dados(1, 6)
            print(term.springgreen4_on_black(f"1D6: {temp}"))
            print(term.springgreen4_on_black(f"La unidad avanzará hasta {unidad.miembros[0].stats_base["Movimiento"]}'' + {temp}'' "))
            unidad.mov = 1
            unidad.atk = 1
            print(term.springgreen4_on_black(f"Presione cualquier tecla para continuar"))
            term.inkey()
            return
        else:
            print(term.springgreen4_on_black(f"Esta unidad no se puede mover mas"))
            print(term.springgreen4_on_black(f"Presione cualquier tecla para continuar"))
            term.inkey()
            return

def Retroceder(term, unidad, p3 = None):
    with term.fullscreen(), term.cbreak(), term.hidden_cursor():
        whitelist = ["Volador", "Titanico"]
        if unidad.shock == True or not any(unidad.claves & whitelist):
            print(term.springreen4_on_black("La unidad realizara una huida desesperada!"))
            for mini in unidad.miembros:
                d = Dados(1, 3)
                if d < 2:
                    print("Una miniatura no ha pasado la prueba!")
                    print("Elije cual será eliminada: ")
                    indice = Selec_mini(term, unidad)
                    print(term.springgreen4_on_black(unidad.miembros[indice].recibir_dano(unidad.miembros.stats_base["Heridas"])))
                    unidad.eliminar_muertos()
            print("La huida desesperada ha terminado")
            print("Presione cualquier tecla para continuar")
            term.inkey()
            unidad.mov = 0
            unidad.atk = 0
            unidad.engaged = False
            return
        
        else:
            print(term.springreen4_on_black(f"La unidad retrocederá hasta {unidad.miembros[0].stats_base.get("Movimiento")}'' "))
            print(term.springreen4_on_black("Recuerde que las miniaturas no pueden terminar este movimiento en zona de amenaza de una unidad enemiga"))
            print(term.springreen4_on_black("\nPresione cualquier tecla para continuar"))
            term.inkey()
            unidad.mov = 0
            unidad.atk = 0
            unidad.engaged = False
            return


def Carga(term, unidad, blanco):
    while True:
        with term.fullscreen(), term.cbreak(), term.hidden_cursor():
            if blanco is not None:
                CadenaIngreso = ''
                print(term.home + term.clear)
                print(term.on_black)
                print(term.springgreen4_on_black(f"Ingrese la distancia entre {unidad.nombre} y {blanco.nombre}"))
        
                tecla = term.inkey()

                if tecla and (tecla.is_sequence == False):
                    CadenaIngreso += tecla
                    print(term.move_x(0), end='')
                    print(term.springgreen4_on_black(f"{CadenaIngreso}"), end='', flush=True)
                    continue
            
                elif tecla.name == "KEY_ENTER":
                    print(term.springgreen4_on_black(f"\nIngresaste: {CadenaIngreso}''"))
                    print(term.springgreen4_on_black("\nPresiona ENTER para continuar"))
                    print(term.springgreen4_on_black("\nPresiona cualquier tecla para reintentar"))
            
                    tecla = term.inkey()
            
                    if tecla.name == "KEY_ENTER" or tecla == '\n':
                        dis = int(CadenaIngreso)
                        d = Dados(2, 6)
                        print(term.springgreen4_on_black(f"2D6: {d}"))
                        if d < dis:
                            print(term.springgreen4_on_black(f"La unidad {unidad.nombre} ha fallado la carga!"))
                            unidad.mov = 1
                            unidad.atk = 1
                            print(term.springgreen4_on_black(f"Presione cualquier tecla para continuar"))
                            term.inkey()
                            return

                        else:
                            print(term.springgreen4_on_black(f"La unidad ha cargado con exito!"))
                            unidad.mov -= 1
                            unidad.atk -= 1
                            unidad.habilidades.append["Tem Pelea Primero"]
                            unidad.engaged = True
                            print(term.springgreen4_on_black(f"Presione cualquier tecla para continuar"))
                            term.inkey()
                            return
                
                    else:
                        CadenaIngreso = ''
                        print(term.home + term.clear)
                        print(term.on_black)
                        print(term.springgreen4_on_black(f"Ingrese la distancia entre {unidad.nombre} y {blanco.nombre}"))
                        continue
            
            else:
                break
            


##Estratagemas
def Overwatch(unidad, blanco, term):
    if (unidad.atk)>=1:
        print(term.springgreen4_on_black(f"{unidad.nombre} va a disparar a {blanco.nombre} usando el estratagema 'overwatch'"))
        Disparo(unidad, blanco)
        return
        
    else: 
        print(term.springgreen4_on_black(f"Tu ere pobre tu no tiene aifon"))
        return


def Granadas(unidad, blanco, term):
        if ("Granadas" in unidad.claves):
            ##disparo() modificado
            Disparo(unidad, blanco, term= term)
            return

     
##Combatir con regla "Pelea primero" v1 (sistema dos colas)
'''
primero = []
segundo = []
for i in Ejercitos_objetos[turno%2].unidades:
    if "Tem Pelea Primero" in i.habilidades or "Pelea Primero" in i.habilidades:
        primero.append(i)
    else:
        segundo.append(i)
        
for i in primero:
    combate(i, blanco)
for i in segundo:
    combate(i, blanco)
'''

##Combatir con regla "Pelea primero" v2 (ordenar) #Inestable
'''
for i in Ejercitos_objetos[turno%2].unidades:
    if "Tem Pelea Primero" in i.habilidades or "Pelea Primero" in i.habilidades:
        aux = Ejercitos_objetos[turno%2].unidades.pop(i)
        Ejercitos_objetos[turno%2].unidades.insert(aux, 0)
        
for j in Ejercitos_objetos[turno%2].unidades:
    combate(i, blanco)
'''

##Combarir con regla "Pelea Primero" v3 (yield) #Menos iteraciones por la lista
def Pelea_Primero(ejercito):
    for i in ejercito.unidades:
        if "Tem Pelea Primero" in i.habilidades or "Pelea Primero" in i. habilidades:
            if i.engaged:
                yield i
    
    for i in ejercito.unidades:
            if not "Tem Pelea Primero" in i.habilidades or not "Pelea Primero" in i. habilidades:
                if i.engaged:
                    yield i 

##Funciones GUI
##Función menu
def Menu(term, unidad, TXT, FUN, par = None):
    Indice = 0
    while True:
        with term.fullscreen(), term.cbreak(), term.hidden_cursor():
            print(term.home + term.clear)
            print(term.on_black)
            print(term.springgreen4_on_black(f"Elige una acción para realizar con {unidad.nombre}"))
            print(term.springgreen4_on_black(f"Si ya seleccionó una acción, elija continuar \n"))
    
            for i, opcion in enumerate(TXT):    #Crear lista de opciones
                if i == Indice:
                    print(term.black_on_springgreen4(f"{i+1}. {opcion}"))
                else:
                    print(term.springgreen4_on_black(f"{i+1}. {opcion}"))
    
            tecla = term.inkey()
    
            if tecla.name in ("KEY_UP", "KEY_LEFT"):
                Indice = (Indice - 1 + len(TXT)) % len(TXT)
        
            elif tecla.name in ("KEY_DOWN", "KEY_RIGHT"):
                Indice = (Indice + 1 + len(TXT)) % len(TXT)
            
            elif tecla.name == "KEY_ENTER" or tecla == '\n':
                if Indice == len(TXT) - 1:
                    ##menu anterior
                    return
    
                else:
                    print(term.springgreen4_on_black(f"\nElegiste {TXT[Indice]}"))
                    Conf_usr(term = term, lista_F=FUN, lista_T=TXT, indice_F=Indice, p1= unidad, p2 =par)
                
                        
                    
            else:
                print(term.springgreen4_on_black(f"\nLa tecla presionada '{tecla}' es invalida"))
                term.inkey()

##Funcion confirmación
def Conf_usr(term, lista_F, lista_T, indice_F, p1, p2 = None):     ##Enviar terminal, lista de funciones, el indice de la lista y al menos un parametro
    while True:
        with term.fullscreen(), term.cbreak(), term.hidden_cursor():

            print(term.home + term.clear)

            print(term.springgreen4_on_black(f"\nIngresaste: {str(lista_T[indice_F])}"))
            print(term.springgreen4_on_black("\nPresiona ENTER para continuar"))
            print(term.springgreen4_on_black("\nPresiona cualquier otra tecla para regresar"))
            
            tecla = term.inkey()
            
            if tecla.name == "KEY_ENTER" or tecla == '\n':
                    ##Hacer algo
                lista_F[indice_F](term, p1, p2)
                return
                
            else:
                print(term.home + term.clear)
                print(term.on_black)
                print(term.springgreen4_on_black("Regresando..."))
                break
                
    return

##Funcion seleccionar blanco devuelve una unidad
def Selec_Blanco(term, unidad, accion, Ejer_Enem):   ##Accion debe ser una cadena: 'cargar', 'disparar', 'combatir'
    indice = 0
    Ejer_Enem.eliminar_unidades()
    while True:
        with term.fullscreen(), term.cbreak(), term.hidden_cursor():
            
            print(term.home + term.clear)
            print(term.on_black)
            print(term.springgreen4_on_black(f"Elige un blanco para {accion} con {unidad.nombre}"))
            print(term.springgreen4_on_black(f"Asegurese que el blanco sea valido para {accion}\n"))

    
            for i, opcion in enumerate(Ejer_Enem.unidades + [f"No {accion}"]):    #Crear lista de opciones
                if i == indice:
                    print(term.black_on_springgreen4(f"{i+1}. {opcion.nombre if isinstance(opcion, Unidad) else opcion}"))
                else:
                    print(term.springgreen4_on_black(f"{i+1}. {opcion.nombre if isinstance(opcion, Unidad) else opcion}"))
    
            tecla = term.inkey()
    
            if tecla.name in ("KEY_UP", "KEY_LEFT"):
                indice = (indice - 1 + len(Ejer_Enem.unidades + [f"No {accion}"])) % len(Ejer_Enem.unidades + [f"No {accion}"])
        
            elif tecla.name in ("KEY_DOWN", "KEY_RIGHT"):
                indice = (indice + 1 + len(Ejer_Enem.unidades + [f"No {accion}"])) % len(Ejer_Enem.unidades + [f"No {accion}"])
            
            elif tecla.name == "KEY_ENTER" or tecla == '\n':
                if indice > len(Ejer_Enem.unidades)-1:
                    print(term.springgreen4_on_black(f"\nElegiste: No {accion}"))
                    return None
                else:
                    print(term.springgreen4_on_black(f"\nElegiste: {Ejer_Enem.unidades[indice].nombre}"))
                    print(term.springgreen4_on_black(f"Presione cualquier tecla para continuar"))

                    term.inkey()

                    return Ejer_Enem.unidades[indice]
                    
            else:
                print(term.springgreen4_on_black(f"\nLa tecla presionada '{tecla}' es invalida"))
                term.inkey()

def Selec_mini(term, unidad): ##Devuelve indice que la miniatura ocupa en la unidad
    indice = 0
    while True:
        with term.fullscreen(), term.cbreak(), term.hidden_cursor():
            
            print(term.springgreen4_on_black(f"Elige una miniatura de {unidad.nombre} para recibir daño"))

            for i, opcion in enumerate(unidad.miembros):    #Crear lista de opciones
                if i == indice:
                    print(term.black_on_springgreen4(f"{i+1}. {opcion.nombre}"))
                else:
                    print(term.springgreen4_on_black(f"{i+1}. {opcion.nombre}"))
            
            tecla = term.inkey()

            if tecla.name in ("KEY_UP", "KEY_LEFT"):
                indice = (indice - 1 + len(unidad.miembros)) % len(unidad.miembros)
        
            elif tecla.name in ("KEY_DOWN", "KEY_RIGHT"):
                indice = (indice + 1 + len(unidad.miembros)) % len(unidad.miembros)
            
            elif tecla.name == "KEY_ENTER" or tecla == '\n':
                print(term.springgreen4_on_black(f"\nElegiste: {unidad.miembros[indice].nombre}"))
                print(term.springgreen4_on_black(f"Presione cualquier tecla para continuar"))
                term.inkey()
                return indice
                    
            else:
                print(term.springgreen4_on_black(f"\nLa tecla presionada '{tecla}' es invalida"))
                term.inkey()
