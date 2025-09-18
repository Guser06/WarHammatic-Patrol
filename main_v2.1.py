from WHmmatic_lib import *
import json
import blessed
import sys

#Inicializar ventana
Term = blessed.Terminal()

#Menú
DISPONIBLE = [
    'Tyranidos v1',
    'Tyrannofex',
    'Space Marines v1',
    'Gladiator Lancer',
    'salir'
]

Ejercitos_diccionarios = [] #Diccionarios provenientes de los JSON

##Elegir ejercitos
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
                        with open('Ejercitos/Ty_patrol.json', 'r') as file:
                            Ejercitos_diccionarios.append(json.load(file))
                        if len(Ejercitos_diccionarios) == 2:
                            break
                        else: Term.inkey()
                    
                    case 1:
                        with open('Ejercitos/Ty_Tyrannofex.json', 'r') as file:
                            Ejercitos_diccionarios.append(json.load(file))
                        if len(Ejercitos_diccionarios) == 2:
                            break
                        else: Term.inkey()
                    
                    case 2:
                        with open('Ejercitos/UM_patrol.json', 'r') as file:
                            Ejercitos_diccionarios.append(json.load(file))
                        if len(Ejercitos_diccionarios)  == 2:
                            break
                        else: Term.inkey()
                    
                    case 3:
                        with open('Ejercitos/UM_Lancer.json', 'r') as file:
                            Ejercitos_diccionarios.append(json.load(file))
                        if len(Ejercitos_diccionarios) == 2:
                            break
                        else: Term.inkey()
                    
        else:
            print(Term.springgreen4_on_black(f"\nLa tecla presionada '{tecla}' es invalida"))
            Term.inkey()

##Establecer limite de rondas
limite = 0
CadenaIngreso = ''
with Term.fullscreen(), Term.cbreak(), Term.hidden_cursor():
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
                limite = int(CadenaIngreso)
                break
            else:
                CadenaIngreso = ''
                print(Term.home + Term.clear)
                print(Term.on_black)
                print(Term.springgreen4_on_black("Ingrese el limite de rondas"))
                continue

Ejercitos_objetos = []   #Lista donde se guardaran los ejercitos convertidos en objetos de Python

i = 0
for d in Ejercitos_diccionarios:    #iterar por lista de diccionarios
    j = 0
    if isinstance(d, dict):     #Determinar si el objeto es un diccionario
        Ejercitos_objetos.append(Ejercito(d))   #Crear el objeto ejercito
        lids = []
        k = 0
        for cu, vu in d.items():    #iterar por diccionario
            if isinstance(vu, dict):    #Determinar si el objeto es un subdiccionario
                if vu["Lider"] is True:
                    lids.append(Lider(vu))
                    for cm, vm in vu.items():   #Iterar por el subdiccionario
                        if isinstance(vm, dict) and cm != 'Habilidades':    #Determinar si el objeto es un subsubdiccionario y no es el diccionario de habilidades
                            lids[k].miembros.append(Individuo(vm))     #Crear el objeto individuo y añadirlo a una unidad
                            lids[k].miembros[-1].AddWeap(vm)   #Crear armas y añadirlas al individuo
                    k += 1

                if vu["Lider"] is not True:
                    Ejercitos_objetos[i].unidades.append(Unidad(vu))    #Crear el objeto unidad y añadirlo a un ejercito
                    for cm, vm in vu.items():   #Iterar por el subdiccionario
                        if isinstance(vm, dict) and cm != 'Habilidades':    #Determinar si el objeto es un subsubdiccionario y no es el diccionario de habilidades
                            Ejercitos_objetos[i].unidades[j].miembros.append(Individuo(vm))     #Crear el objeto individuo y añadirlo a una unidad
                            Ejercitos_objetos[i].unidades[j].miembros[-1].AddWeap(vm)   #Crear armas y añadirlas al individuo
                    j += 1

        for lid in lids:
            lid.AddLider(Ejercitos_objetos[i])

        i += 1

#Determinar turno
turno = 0
with Term.fullscreen(), Term.cbreak(), Term.hidden_cursor():
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
        break
#Actua el jugador Ejercitos_objetos[turno%2]
        
##BUCLE DE PARTIDA

MOVIMIENTO_T = [
    'Movimiento normal',
    'Estatico',
    'Avance',
    'Continuar'
]

MOVIMIENTO_F = [
    Normal,
    Estatico,
    Avance
]

CARGA_T = [
    'Carga',
    'Estatico',
    'Regresar',
    'Omitir'
]

CARGA_F = [
    Carga,
    Estatico
]

while turno/2 <= limite:
    Aumentar_PC(Ejercitos_objetos)

    for u in Ejercitos_objetos[turno%2].unidades:
        Shock_Test(unidad=u, term=Term)

    Aumentar_Mov_Atk(Ejercitos_objetos[turno%2])

    for u in Ejercitos_objetos[turno%2].unidades:
        if u.mov >= 0:
            Menu(term=Term, unidad=u, TXT=MOVIMIENTO_T, FUN=MOVIMIENTO_F)
        else: continue
    
    for u in Ejercitos_objetos[turno%2].unidades:
        Disparo(unidad= u, term= Term, Ejer_Enem=Ejercitos_objetos[(turno%2)-1])
    
    for u in Ejercitos_objetos[turno%2].unidades:
        Menu(term=Term, unidad=u, TXT=CARGA_T, FUN=CARGA_F, par=Selec_Blanco(term=Term, unidad=u, accion='Cargar', Ejer_Enem=Ejercitos_objetos[(turno%2)-1]))
    
    Combate(unidad= Pelea_Primero(Ejercitos_objetos[turno%2]), blanco=Selec_Blanco(term=Term, unidad=u, accion='Combatir', Ejer_Enem=Ejercitos_objetos[(turno%2)-1]))        
      
    turno += 1

