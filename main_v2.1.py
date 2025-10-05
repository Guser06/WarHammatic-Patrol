from WHmmatic_lib import *
import blessed

#Inicializar ventana
Term = blessed.Terminal()
#Elegir ejercitos
Ejercitos_diccionarios = Elegir_Ejs(Term)

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

##Construir los objetos
Ejercitos_objetos = Build_Armies(Ejercitos_diccionarios)

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
    'Retroceder',
    'Continuar'
]

MOVIMIENTO_F = [
    Normal,
    Estatico,
    Avance,
    Retroceder
]

CARGA_T = [
    'Carga',
    'Estatico',
    'Continuar'
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
    
    unidades = Pelea_Primero(Ejercitos_objetos[turno%2])
    for u in unidades:
        Combate(term=Term, unidad= u, Ejer_Enem=Ejercitos_objetos[(turno%2)-1])        
        if "Tem Pelea Primero" in u.habilidades.keys():
            del u.habilidades["Tem Pelea Primero"]
    
    turno += 1
    
    if Victoria(Term, Ejercitos_objetos):
        break

if (Ejercitos_objetos[0].nu - len(Ejercitos_objetos[0].unidades)) > (Ejercitos_objetos[1].nu - len(Ejercitos_objetos[1].unidades)):
    print(Term.springgreen4_on_black(f"El ejercito de {Ejercitos_objetos[1].faccion} ha ganado tras destruir mas unidades enemigas!"))
elif (Ejercitos_objetos[0].nu - len(Ejercitos_objetos[0].unidades)) < (Ejercitos_objetos[1].nu - len(Ejercitos_objetos[1].unidades)):
    print(Term.springgreen4_on_black(f"El ejercito de {Ejercitos_objetos[0].faccion} ha ganado tras destruir mas unidades enemigas!"))
elif (Ejercitos_objetos[0].nu - len(Ejercitos_objetos[0].unidades)) == (Ejercitos_objetos[1].nu - len(Ejercitos_objetos[1].unidades)):
    print(Term.springgreen4_on_black(f"Ningun ejercito ha destruido mas unidades enemigas que el otro, la partida termina en empate!"))
        
print(Term.springgreen4_on_black("Presione cualquier tecla para terminar el programa"))
Term.inkey()
sys.exit()