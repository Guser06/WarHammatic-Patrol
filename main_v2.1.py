from WHmmatic_lib import *

#Elegir ejercitos
Ejercitos_diccionarios = Elegir_Ejs()

##Establecer limite de rondas
limite = Limite_Rondas()

##Construir los objetos
Ejercitos_objetos = Build_Armies(Ejercitos_diccionarios)

#Determinar turno
turno = DeTerminar_turno()
#Actua el jugador Ejercitos_objetos[turno%2]
        
##BUCLE DE PARTIDA
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
    
    if Victoria(Ejercitos_objetos):
        break