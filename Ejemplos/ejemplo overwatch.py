import random as rand
import json as js

#Menú

#Constructor

A1 = ["Grupo Capitan"]
A2 = ["Grupo Infernus"]
B1 = ["Primus"]
B2 = ["Psicofago"]

unidades = [A1, A2, 0, "space marines"]
contra = [B1, B2, 0, "tyranidos"]

#bucle:
unidades[-2]+=1
contra[-2]+=1

print(f"El jugador de {unidades[-1]} tiene {unidades[-2]} puntos de comando")

def disparo(unidad, blanco):
    ##SI
    print(f"La {unidad} va a tronarse a {blanco}")

def overwatch(unidad, blanco):
    if (unidades[-2])>=1:
        print(f"La {unidad[0]} va a disparar a {blanco[0]} usando el estratagema 'overwatch'")
        disparo(unidad, blanco)
    else: print("Tu ere pobre tu no tiene aifon")
    unidades[-2]-=2

def granadas(unidad, blanco):
    for i in unidad:
        if (any("granadas") in unidad.claves):
            ##disparo() modificado
            disparo(unidad, blanco)
             

##overwatch(unidades, contra)