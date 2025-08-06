
lista1 = ['''Aqui va la lista sacada del JSON no 1''']
lista2 = ['''Aqui va la lista sacada del JSON no 2''']
Ejercitos_listas = [lista1, lista2]#Listas provenientes de los JSON
Ejercitos_objetos =[]#Lista donde se guardaran los ejercitos convertidos en objetos de Python

StatsTx = ["Movimiento", "Resistencia", "Salvación",
           "Heridas", "Liderazgo", "Control de objetivo"]#Nombre de las stats de las miniaturas

ArmaTx = ["Nombre", "Alcance", "No. de Ataques",
          "Habilidad", "Fuerza", "Perforación", "Daño"]#Nombre de las stats de las armas
    
class Individuo:
    def __init__(self, lista):
        self.nombre = lista[0]#Nombre de la miniatura
        self.stats_base = dict(zip(StatsTx, lista[1])) #Stats de la miniatura
        self.rango1 = dict(zip(ArmaTx, lista[2]))  # Armas de rango
        self.rango2 = dict(zip(ArmaTx, lista[3]))
        self.rango3 = dict(zip(ArmaTx, lista[4]))
        self.rango4 = dict(zip(ArmaTx, lista[5]))
        self.mele1 = dict(zip(ArmaTx, lista[6])) # Armas cuerpo a cuerpo
        self.mele2 = dict(zip(ArmaTx, lista[7]))
        self.habilidades = [lista[8]]#Claves y "habilidades del lado del datasheet"
        self.dmg = 0 #Daño recibido por la miniatura
        self.vivo = True#La miniatura esta viva

    def recibir_dano(self, dano):
        self.dmg += dano
        if self.dmg >= self.stats_base[3]:  # Si daño >= heridas
            self.vivo = False
            print(f"{self.nombre} ha muerto.")

    def __repr__(self):
        estado = "Vivo" if self.vivo else "Muerto"
        return f"{self.nombre} ({estado})"

class Unidad:
    def __init__(self, lista):
        self.mov = 0
        self.atk = 0
        self.shock = False
        self.miembros = []
        self.nombre = lista[0]
        self.lider = lista[1]
        self.habilidades = lista[2]
        self.claves = lista[3]
        self.nm = lista[-1]

    def eliminar_muertos(self):
        self.miembros = [
            Individuo for mini in self.miembros if Individuo.vivo == False]

    def __repr__(self):
        return f"{self.nombre}:\n" + "\n".join(str(miembro) for miembro in self.miembros)

class Ejercito:
    def __init__(self, lista):
        self.pc = 0
        self.pv = 0
        self.faccion = lista[-1]
        self.nu = lista[-2]
        self.unidades = []

    def __repr__(self):
        return f"{self.faccion}:\n" + "\n".join(str(unidad) for unidad in self.unidades)

m = 0
for e in Ejercitos_listas:
    Ejercitos_objetos[m] = Ejercito(e)
    for u in range(e[m][-1]):
        Ejercitos_objetos[m].unidades[u] = Unidad(e[m][u])
        for i in range(e[m][u][-1]):
            Ejercitos_objetos[m].unidades[u].miembros[i] = Individuo(e[m][u][i])
    m+1
