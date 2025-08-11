import random as rand
import json
import curses
import sys

#Inicializar ventana
ventana = curses.initscr()
ventana.keypad(True)
curses.cbreak()
curses.noecho()

curses.start_color()
curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLACK)
negro = curses.color_pair(1)    #Colores utilizados
blanco = curses.color_pair(2)   #Colores utilizados

#Menú
disponible = [
    'Salir',
    'Tyranidos v1',
    'Space Marines v1'
]
limite = 0 
##Solicitar al usuario limite de rondas
def menu_inicio(ventana):
    Indice_ejercito = 0
    while True:
        ventana.clear()
        ventana.addstr('Elige un ejercito: \n', curses.A_UNDERLINE)
        
        for i in range(len(disponible)):    #Crear lista de opciones
            ventana.addstr('{}.- '.format(i+1))
            ventana.addstr(disponible[i] + '\n', negro if i == Indice_ejercito else blanco)
        
        c = ventana.getch()
        
        if c == curses.KEY_UP or c == curses.KEY_LEFT:
            Indice_ejercito = (Indice_ejercito -1 + len(disponible)) % len(disponible)
        
        elif c == curses.KEY_DOWN or c == curses.KEY_RIGHT:
            

#Función de dados
def Dados(n_dados):
    res_dados=[]
    res_dados = [rand.randint(1, 6) for _ in range(1, (n_dados+1))]
    return res_dados

#Constructor de unidades 

Ejercitos_diccionarios = [] #Diccionarios provenientes de los JSON

##Aqui se puede construir una función
with open('UM_patrol.json', 'r') as file:
    Ejercitos_diccionarios.append(json.load(file))

##Aqui sería la función para guardar el segundo json
with open('Ty_patrol.json', 'r') as file:
    Ejercitos_diccionarios.append(json.load(file))  #Aqui va el diccionario sacado del JSON no 2


StatsTx = ["Movimiento", "Resistencia", "Salvación",
           "Heridas", "Liderazgo", "Control de objetivo"]   #Nombre de las stats de las miniaturas

ArmaTx = ["Nombre", "Alcance", "No. de Ataques",
          "Habilidad", "Fuerza", "Perforación", "Daño"] #Nombre de las stats de las armas
    
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
        if self.dmg >= self.stats_base[3]:  # Si daño >= heridas
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
                    if isinstance(vm, dict):    #Determinar si el objeto es un subsubdiccionario 
                        Ejercitos_objetos[i].unidades[j].miembros.append(Individuo(vm))     #Crear el objeto individuo y añadirlo a una unidad
                j += 1
        i += 1

#Determinar turno
turno = 0

while turno == 0:
    comenzar = Dados(2)
    print(f"Dado Jugador 1 ({Ejercitos_objetos[0].faccion}): {comenzar[0]}")
    print(f"Dado Jugador 2 ({Ejercitos_objetos[1].faccion}): {comenzar[1]}")
    if comenzar[0] > comenzar[1]:
        print("Comienza el jugador 1")
        turno = 0
        break
    if comenzar[0] < comenzar[1]:
        print("Comienza el jugador 2")
        turno = 1
        break
    else: continue
    
#Actua el jugador Ejercitos_objetos[turno%2]



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