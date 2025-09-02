'''
Librería de funciones utilizadas en Warhammatic
Creada por Guser_06 como proyecto personal para facilitar el juego Warhammer 40k 10ma edición
Se recomienda leer este modulo y sus comentarios para entender la estructura bajo la
que se esta programando el archivo 'main vx.x.py'
'''
##Librerías
import random as rand
import time

#Función de dados
def Dados(n_dados, Dx):     ##Numero de dados que se desean, Numero de caras del dado a lanzar
    res_dados=[]
    res_dados = [rand.randint(1, Dx) for _ in range(1, (n_dados+1))]
    return res_dados


##Funciones estandar

##Aumentar puntos de comando
def Aumentar_PC(Ejer_Obj):
    for i in Ejer_Obj:
        i.pc += 1

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
                if (prueba[0]+prueba[1]) < mayor:   
                    unidad.shock = True
                    print(term.springreen4_on_black(unidad.__repr__()))
                    print(term.springgreen4_on_black("Presione cualquier tecla para continuar"))
                    term.inkey()
                    break
        
                else:
                    unidad.shock = False
                    print(term.springreen4_on_black(unidad.__repr__()))
                    print(term.springgreen4_on_black("Presione cualquier tecla para continuar"))
                    term.inkey()
                    break
        
            elif unidad.nm == 1 and unidad.miembros[0].dmg > unidad.miembros[0].stats_base.get("Heridas"):
                prueba = Dados(2, 6)
                if (prueba[0]+prueba[1]) < unidad.miembros[0].stats_base.get("Liderazgo"):   
                    unidad.shock = True
                    print(term.springreen4_on_black(unidad.__repr__()))
                    print(term.springgreen4_on_black("Presione cualquier tecla para continuar"))
                    term.inkey()
                    break
        
                else:
                    unidad.shock = False
                    print(term.springreen4_on_black(unidad.__repr__()))
                    print(term.springgreen4_on_black("Presione cualquier tecla para continuar"))
                    term.inkey()
                    break
            else: break
    
    
def Disparo(unidad, blanco, term):
    ##SI
    print(term.springgreen4_on_black(f"La {unidad.nombre} va a tronarse a {blanco.nombre}"))

def Combate(unidad, blanco, term):
    if unidad.engaged:
        print(term.springgreen4_on_black(f"La {unidad.nombre} va a tronarse a {blanco.nombre}"))
        if "Tem Pelea Primero" in unidad.habilidades:
            unidad.habilidades.remove("Tem Pelea Primero")
        blanco.eliminar_muertos()

def Estatico(unidad, term):
    print(term.springgreen4_on_black(f"La unidad {unidad.nombre} se quedara estatica"))
    unidad.mov -= 1
    
def Normal(unidad, term):
    print(term.springgreen4_on_black(f"La unidad se moverá hasta {unidad.miembros[0].stats_base["Movimiento"]}"))
    unidad.mov -= 1
    
def Avance(unidad, term):
    temp = Dados(1, 6)
    print(term.springgreen4_on_black(f"1D6: {temp}"))
    print(term.springgreen4_on_black(f"La unidad avanzará hasta {unidad.miembros[0].stats_base["Movimiento"]}'' + {temp}'' "))
    unidad.mov -= 2
    
def Carga(unidad, term):
    dis = int(input(f"Ingrese la distancia entre la unidad {unidad.nombre} y la unidad objetivo"))
    d = Dados(2, 6)
    print(term.springgreen4_on_black(f"2D6: {d} = {d[0]+d[1]}"))
    if (d[0]+d[1])<dis:
        print(term.springgreen4_on_black(f"La unidad {unidad.nombre} ha fallado la carga!"))
        unidad.mov -= 1
        unidad.atk -= 1
    else:
        print(term.springgreen4_on_black(f"La unidad ha cargado con exito!"))
        unidad.mov -= 1
        unidad.atk -= 1
        unidad.habilidades.append["Tem Pelea Primero"]
        unidad.engaged = True


##Estratagemas
def Overwatch(unidad, blanco, term):
    if (unidad.atk)>=1:
        print(term.springgreen4_on_black(f"{unidad.nombre} va a disparar a {blanco.nombre} usando el estratagema 'overwatch'"))
        Disparo(unidad, blanco)
    else: print(term.springgreen4_on_black(f"Tu ere pobre tu no tiene aifon"))
    unidad.atk-=2

def Granadas(unidad, blanco, term):
    for i in unidad:
        if (any("granadas") in unidad.claves):
            ##disparo() modificado
            Disparo(unidad, blanco, term= term)

     
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

##Combarir con regla "Pelea Primero" v3 (yield) #ChatGPT
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
def Menu(unidad, TXT, FUN, term, par = None):
    Indice = 0
    with term.fullscreen(), term.cbreak(), term.hidden_cursor():
        while True:
            print(term.home + term.clear)
            print(term.on_black)
            print(term.springgreen4_on_black(f"Elige una acción para realizar con {unidad.nombre} \n"))
    
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
                    Conf_usr(term, FUN, Indice, unidad, par)
                
                        
                    
            else:
                print(term.springgreen4_on_black(f"\nLa tecla presionada '{tecla}' es invalida"))
                term.inkey()

##Funcion confirmación
def Conf_usr(term, lista_F, indice_F, p1, p2 = None):     ##Enviar terminal, lista de funciones, el indice de la lista y al menos un parametro
    with term.fullscreen(), term.cbreak(), term.hidden_cursor():
        print(term.home + term.clear)
    
        while True:
        
            tecla = term.inkey()
        
            if tecla.name == "KEY_ENTER":
                print(term.springgreen4_on_black(f"\nIngresaste: {str(lista_F[indice_F])}"))
                print(term.springgreen4_on_black("\nPresiona ENTER para continuar"))
                print(term.springgreen4_on_black("\nPresiona cualquier tecla para regresar"))
            
                tecla = term.inkey()
            
                if tecla.name == "KEY_ENTER" or tecla == '\n':
                    ##Hacer algo
                    lista_F[indice_F](p1, p2 if p2 else None)
                    break
                else:
                    print(term.home + term.clear)
                    print(term.on_black)
                    print(term.springgreen4_on_black("Regresando..."))
                    time.sleep(1.5)
                    break

##Funcion seleccionar blanco
def Selec_Blanco(term, accion, Ejer_Enem):   ##Accion debe ser una cadena: 'cargar', 'disparar', 'combatir'
    indice = 0
    with term.fullscreen(), term.cbreak(), term.hidden_cursor():
        while True:
            print(term.home + term.clear)
            print(term.on_black)
            print(term.springgreen4_on_black(f"Elige un blanco para {accion}:\n"))
    
            for i, opcion in enumerate(Ejer_Enem.unidades):    #Crear lista de opciones
                if i == indice:
                    print(term.black_on_springgreen4(f"{i+1}. {opcion.nombre}"))
                else:
                    print(term.springgreen4_on_black(f"{i+1}. {opcion.nombre}"))
    
            tecla = term.inkey()
    
            if tecla.name in ("KEY_UP", "KEY_LEFT"):
                indice = (indice - 1 + len(Ejer_Enem.unidades)) % len(Ejer_Enem.unidades)
        
            elif tecla.name in ("KEY_DOWN", "KEY_RIGHT"):
                indice = (indice + 1 + len(Ejer_Enem.unidades)) % len(Ejer_Enem.unidades)
            
            elif tecla.name == "KEY_ENTER" or tecla == '\n':
                print(term.springgreen4_on_black(f"\nElegiste: {Ejer_Enem.unidades[indice].nombre}"))
                return Ejer_Enem.unidades[indice]
                    
            else:
                print(term.springgreen4_on_black(f"\nLa tecla presionada '{tecla}' es invalida"))
                term.inkey()
