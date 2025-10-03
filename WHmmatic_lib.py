'''
Librería de funciones utilizadas en Warhammatic
Creada por Guser_06 como proyecto personal para facilitar el juego Warhammer 40k 10ma edición
Se recomienda leer este modulo y sus comentarios para entender la estructura bajo la
que se esta programando el archivo 'main vx.x.py'
'''
##Librerías
import random as rand
import json
from pathlib import Path
import sys

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

##Lista donde se guardaran los ejercitos convertidos en objetos de Python
##Usada como global aqui por que me dió weba
Ejercitos_objetos = []


##Clases
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

    def recibir_dano(self, dano, habs, term):
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
                    FinViol(term, habs, self.nombre, Ejercitos_objetos)
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
    
    def AddLider(self, ej):
        for i in ej.unidades:
            if isinstance(i.posLid, list) and i.lider == '':
                for x in i.posLid:
                    if x == self.nombre:
                        i.lider = self.nombre
                        i.miembros = i.miembros + self.miembros
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
        self.unidades = [uni for uni in self.unidades if len(uni.miembros) != 0]
    
    def __repr__(self):
        return f"{self.faccion}:\n" + "\n".join(str(unidad) for unidad in self.unidades)


##Funciones de dados
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

def RepFallos(lista_dados, val, DX, ret_num = False):   ##Repetir las tiradas de dados que fallaron
    exito = [dado for dado in lista_dados if dado >= val]
    n_fallos = len([dado for dado in lista_dados if dado < val])
    exito += Dados(n_dados=n_fallos, Dx=DX, ret_num= False)
    if ret_num:
        exito = sum(exito)
    return exito


##Funciones estandar
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
def Shock_Test(unidad, term):
    with term.fullscreen(), term.cbreak(), term.hidden_cursor():

        while True:
            print(term.home + term.clear)
            if len(unidad.miembros)<(unidad.nm//2) and (unidad.nm != 1):
                mayor = 0
                for mini in unidad.miembros:
                    if mini.stats.get("Liderazgo") > mayor:
                        mayor = mini.stats.get("Liderazgo")
                
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
        
            elif unidad.nm == 1 and unidad.miembros[0].dmg > unidad.miembros[0].stats.get("Heridas")//2:
                prueba = Dados(2, 6)
                if prueba < unidad.miembros[0].stats.get("Liderazgo"):   
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

##Repartir heridas
def RepDmg(term, blanco, dano, Presicion = False):
    while dano >= 1:
        danada = Selec_mini(term, blanco, Presicion)
        if danada == None:
            dano = 0
        Qt_dmg = blanco.miembros[danada].stats.get("Heridas")-blanco.miembros[danada].dmg
        if dano >= Qt_dmg:
            print(term.springgreen4_on_black(f"{blanco.miembros[danada].recibir_dano(Qt_dmg, blanco.habilidades)}"))
            print(term.springgreen4_on_black("Presione cualquier tecla para continuar"))
            term.inkey()
            dano -= Qt_dmg
            blanco.eliminar_muertos()
            continue
        else:
            blanco.miembros[danada].recibir_dano(dano, blanco.habilidades)
            print(term.springgreen4_on_black(f"{blanco.miembros[danada].__repr__()}\nHeridas recibidas: {blanco.miembros[danada].dmg}"))
            print(term.springgreen4_on_black("Presione cualquier tecla para continuar"))
            term.inkey()
            dano = 0
            continue
    return

##Funcion de disparo
def Disparo(term, unidad, Ejer_Enem):
    whitelist = ["Vehiculo", "Monstruo", "Pistola", "Asalto"]
    graylist = ["Vehiculo", "Monstruo", ]
    with term.fullscreen(), term.cbreak(), term.hidden_cursor():
        print(term.home + term.clear)

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
        
        ##Regla Asalto
        asalt = False
        ##Verificar si la unidad Avanzo
        if unidad.atk == 1 and 'Asalto' in keysu:
            asalt = True
            print(term.springgreen4_on_black(f"{unidad.nombre} solo puede disparar con armas de Asalto en este turno"))
            print(term.springgreen4_on_black("Presiona cualquier tecla para continuar"))
            term.inkey()
            print(term.home + term.clear)
        elif unidad.atk == 1 and not 'Asalto' in keysu:
            print(term.springgreen4_on_black(f"{unidad.nombre} ya no puede disparar en este turno"))
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
                    l_armas = [x.usado for x in miembro.rango]
                    if all(l_armas):
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

                            ##Hacer valida regla asalto
                            if asalt and not 'Asalto' in miembro.rango[indice].claves.keys():
                                print(term.springgreen4_on_black(f"No puede disparar con {miembro.rango[indice].nombre} en este turno"))
                                print(term.springgreen4_on_black("Presiona cualquier tecla para continuar"))
                                term.inkey()
                                miembro.rango[indice].usado = True
                                print(term.home + term.clear)
                                break
                            
                            ##Verificar regla precisiom
                            if 'Precision' in miembro.rango[indice].claves.keys():
                                Presicion = True

                            ##Si no se ha usado el arma elegida, seguir proceso
                            print(term.springgreen4_on_black(f"\nElegiste: {miembro.rango[indice].nombre}"))                            
                            print(term.home + term.clear)

                            ##Elegir un blanco y recuperar sus claves si es valido
                            blanco = Selec_Blanco(term=term, unidad=unidad, accion='Disparar', Ejer_Enem=Ejer_Enem)
                            if blanco is None:
                                miembro.rango[indice].usado = True
                                continue
                            else:

                                keysb = []
                                keysb = set(keysb)
                                keysb|=(set(blanco.claves) & set(graylist))

                                if blanco.engaged and not any(keysb):
                                    print(term.springgreen4_on_black(f"{blanco.nombre} está muy cerca de un aliado!"))
                                    print(term.springgreen4_on_black("Presiona cualquier tecla para continuar"))
                                    term.inkey()
                                    break

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
                                    print(term.springgreen4_on_black("Presiona cualquier tecla para continuar"))
                                    term.inkey()
                                    continue

                                ##Regla Agente solitario
                                if blanco.lider != '' and 'Agente Solitario' in blanco.habilidades.keys() and dist >= 12:
                                    print(term.springgreen4_on_black(f"{blanco.nombre} es un agente solitario y se ha escabullido!"))
                                    print(term.springgreen4_on_black("Presiona cualquier tecla para continuar"))
                                    term.inkey()
                                    break                                

                                else:
                                    ##Tirada para impactar
                                    print(term.home + term.clear)

                                    n = miembro.rango[indice].stats.get("No. de Ataques")
                                

                                    ##Regla Area (blast)                                
                                    if 'Area' in miembro.rango[indice].claves.keys():
                                        if blanco.engaged == True:
                                            print(term.springgreen4_on_black(f"{blanco.nombre} esta demasiado cerca de una unidad aliada para usar esta arma"))
                                            break
                                        else:
                                            n += ('+' + str(len(blanco.miembros)//5))

                                    ##Regla Fuego rapido
                                    elif 'Fuego Rapido' in miembro.rango[indice].claves.keys():
                                        if dist <= miembro.rango[indice].stats.get("Alcance")//2:
                                            print(term.springgreen4_on_black(f"{unidad.nombre} está cerca de su objetivo y lanza {miembro.rango[indice].claves.get('Fuego Rapido')} ataques adicionales"))
                                            n += miembro.rango[indice].claves.get('Fuego Rapido') if isinstance(n, int) else f'+{miembro.rango[indice].claves.get('Fuego Rapido')}'
                                
                                    ##Si se repite el arma usar Tirada rapida
                                    impact = []
                                    nAI = Repetida(miembro.rango[indice], unidad)
                                    if nAI > 1:
                                        t = f"\nMultiples miniaturas en {unidad.nombre} usan {miembro.rango[indice].nombre}\nDesea hacer una tirada rápida para dispararlas todas contra {blanco.nombre}?"
                                        r, c = term.get_location()
                                        if Selec_SN(term, r, c, t):
                                            for m in unidad.miembros:
                                                for a in m.rango:
                                                    if miembro.rango[indice].nombre == a.nombre and not a.usado:
                                                        impact += Dados(n, 6, False) if isinstance(miembro.rango[indice].stats.get("No. de Ataques"), int) else AtkDmg_Rand(n)
                                                        a.usado = True
                                                        if 'Perfil' in miembro.rango[indice].claves.keys():
                                                            for arma in miembro.rango:
                                                                if 'Perfil' in arma.claves.keys():
                                                                    arma.usado = True
                                                    else: continue
                                        else:
                                            miembro.rango[indice].nombre
                                            impact = Dados(n, 6, False) if isinstance(miembro.rango[indice].stats.get("No. de Ataques"), int) else AtkDmg_Rand(n)
        
                                    else:
                                        ##Una vez pasado cualquier filtro se considera usada el arma
                                        miembro.rango[indice].usado = True
                                    
                                        ##Colocar como usadas las armas de perfiles opcionales
                                        if 'Perfil' in miembro.rango[indice].claves.keys():
                                            for arma in miembro.rango:
                                                if 'Perfil' in arma.claves.keys():
                                                    arma.usado = True
                                            
                                        impact = Dados(n, 6, False) if isinstance(miembro.rango[indice].stats.get("No. de Ataques"), int) else AtkDmg_Rand(n)
                                        
                                    ##Golpes sostenidos
                                    if 'Golpes Sostenidos' in miembro.mele[indice].claves.keys():
                                        nGS = miembro.mele[indice].claves.get('Golpes Sostenidos')
                                        nAd = 0
                                        print(term.springgreen4_on_black(f"El arma {miembro.mele[indice].nombre} hace golpes sostenidos"))
                                        for dado in impact:
                                            if dado == 6:
                                                nAd += nGS if isinstance(nGS, int) else AtkDmg_Rand(nGS, False)
                                        print(term.springgreen4_on_black(f"Se produjeron {nAd} impactos adicionales")) 
                                        impact += [6] * nAd
                                                
                                
                                    ##Impactos letales
                                    elif 'Impactos Letales' in miembro.mele[indice].claves.keys():
                                        print(term.springgreen4_on_black(f"El arma {miembro.mele[indice].nombre} causa impactos letales"))
                                        seis = [dado for dado in impact if dado == 6]
                                        impact = [dado for dado in impact if dado != 6]
                                        print(term.springgreen4_on_black(f"{len(seis)} impactos fueron letales"))
                                        m = miembro.mele[indice].stats.get("Daño")
                                        dano = 0
                                        for d in seis:
                                            dano += m if isinstance(m, int) else AtkDmg_Rand(m, True)
                                        RepDmg(term, blanco, dano)

                                    ##Regla Pesada
                                    elif 'Pesado' in miembro.rango[indice].claves.keys() and unidad.mov == 3:
                                        print(term.springgreen4_on_black(f"{unidad.nombre} no se movió en este turno y se beneficia de ello"))
                                        impact = [dado+1 for dado in impact]

                                    elif ('Monstruo' in unidad.claves or 'Vehiculo' in unidad.claves) and unidad.engaged == True:
                                        print(term.springgreen4_on_black(f"{unidad.nombre} ha tenido problemas para apuntar por estar muy cerca de otro enemigo"))
                                        impact = [dado for dado in impact if dado > 1]
                                        impact = [dado-1 for dado in impact]
                                        print(term.springgreen4_on_black("Presiona cualquier tecla para continuar"))

                                    elif 'Sigilo' in blanco.habilidades.keys():
                                        print(term.springgreen4_on_black(f"{blanco.nombre} es sigiloso y ha sido dificil impactarle!"))
                                        impact = [dado for dado in impact if dado > 1]
                                        impact = [dado-1 for dado in impact]
                                        print(term.springgreen4_on_black("Presiona cualquier tecla para continuar"))
                                        term.inkey()
                                        
                                    print(term.springgreen4_on_black(f"Se han lanzado {len(impact)} ataques"))
                                    impact = [dado for dado in impact if dado >= miembro.rango[indice].stats.get("Habilidad")]
                                    print(term.springgreen4_on_black("Las tiradas para impactar exitosas:"))
                                    print(term.springgreen4_on_black(f"{impact}"))
                                    print(term.springgreen4_on_black("Presione cualquier tecla para continuar"))
                                    term.inkey()
                                    if len(impact) == 0:
                                        break
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
                                                print(term.black_on_springgreen4(f"{blanco.nombre} ha sufrido heridas devastadoras"))
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

                                                print(term.black_on_springgreen4(f"A que miniatura se le asignarán {salvar} heridas?"))
                                                print(term.springgreen4_on_black("Presione cualquier tecla para continuar"))
                                                term.inkey()

                                                RepDmg(term, blanco, salvar)
                                    
                                        print(term.springgreen4_on_black("Las tiradas que han herido:"))
                                        print(term.springgreen4_on_black(f"{herir}\n"))

                                        ##Palabra clave acoplado
                                        if 'Acoplado' in miembro.rango[indice].claves:
                                            t = f"{miembro.rango[indice].nombre} es un arma acoplada, ¿Desea repetir la tirada para herir?"
                                            r, c = term.get_location()
                                            if Selec_SN(term, r, c, t):
                                                herir = RepFallos(lista_dados=herir, val=obj, DX=6)

                                                herir = [dado for dado in herir if dado >= obj]
                                            
                                                print(term.springgreen4_on_black("Las tiradas que han herido:"))
                                                print(term.springgreen4_on_black(f"{herir}\n"))
                                                if len(herir) == 0:
                                                    print(term.springgreen4_on_black("Presione cualquier tecla para continuar"))
                                                    term.inkey()
                                                    break
                                            
                                        if len(herir) == 0:
                                            print(term.springgreen4_on_black("Presione cualquier tecla para continuar"))
                                            term.inkey()
                                            break

                                        ##Regla anti
                                        if 'Anti' in miembro.rango[indice].claves.keys():
                                            if miembro.rango[indice].claves.get('Anti')[0] in blanco.claves:
                                                a = 0
                                                for i in herir:
                                                    if i >= miembro.rango[indice].claves.get('Anti')[1]:
                                                        a += 1
                                                if a:
                                                    print(term.black_on_springgreen4(f"{blanco.nombre} ha sufrido heridas mortales!"))
                                                    print(term.black_on_springgreen4(f"A que miniatura se le asignarán las heridas?"))
                                                    m = miembro.rango[indice].stats.get("Daño")
                                                    if isinstance(m, str):
                                                        dano_azar = []
                                                        for x in range(0, a):
                                                            dano_azar.append(AtkDmg_Rand(m, True) )
                                                        dano = sum(dano_azar)
                                                    else:
                                                        dano = int(m)
                                                        dano*=a

                                                    print(term.springgreen4_on_black("Presione cualquier tecla para continuar"))
                                                    term.inkey()

                                                    RepDmg(term, blanco, dano)
                                                    


                                        print(term.springgreen4_on_black(f"A continuación, permita al oponente usar la terminal"))
                                        print(term.springgreen4_on_black("Presione cualquier tecla para continuar"))
                                        term.inkey()

                                        if len(blanco.miembros) == 0:
                                            continue

                                        index = 0
                                        while True:
                                            print(term.home + term.clear)
                                            print(term.springgreen4_on_black(f"Es momento de las tiradas de salvación de {blanco.nombre}"))
                                            print(term.springgreen4_on_black(f"El factor de perforación del arma atacante es -{miembro.rango[indice].stats.get("Perforación")}"))
                                        
                                            salvacion = blanco.miembros[0].stats.get("Salvación")
                                            if miembro.rango[indice].stats.get("Perforación") > 0:
                                                print(term.springgreen4_on_black(f"La salvación requerida sube a {blanco.miembros[0].stats.get("Salvación") + miembro.rango[indice].stats.get("Perforación")}"))
                                                salvacion += miembro.rango[indice].stats.get("Perforación")

                                            if 'Invulnerable' in blanco.habilidades.keys():
                                                print(term.springgreen4_on_black(f"\nLa unidad atacada tiene una salvación invulnerable de {blanco.habilidades.get('Invulnerable')}"))
                                                print(term.springgreen4_on_black(f"¿Que perfil desea usar?\n"))

                                                S = [f"Salvación regular: {blanco.miembros[0].stats.get('Salvación') + miembro.rango[indice].stats.get('Perforación')}+",
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
                                                        salvacion = blanco.miembros[0].stats.get("Salvación") + miembro.rango[indice].stats.get("Perforación")
                                                        break
                                                    elif index == 1:
                                                        salvacion = blanco.habilidades.get('Invulnerable')
                                                        break
                                        
                                            if not 'Invulnerable' in blanco.habilidades.keys():
                                                print(term.springgreen4_on_black("Presione cualquier tecla para continuar"))
                                                term.inkey()
                                                break
                                        
                                        salvar = Dados(len(herir), 6, False)
                                        salvar = [dado for dado in salvar if dado >= salvacion]
                                        print(term.home + term.clear)
                                        print(term.black_on_springgreen4(f"Se han salvado {len(salvar)} de {len(herir)} ataques"))

                                        if len(herir) > len(salvar):
                                            salvar = len(herir) - len(salvar)
                                            m = miembro.rango[indice].stats.get("Daño")
                                            
                                            ##Regla Melta (fusion)
                                            Dmg_Melta = 0
                                            if 'Fusion' in miembro.rango[indice].claves.keys() and dist <= miembro.rango[indice].stats.get('Alcance'):
                                                Dmg_Melta = miembro.rango[indice].claves.get('Fusion')
                                                print(term.springgreen4_on_black(f"El arma {miembro.rango[indice].nombre} es un arma de fusión y hace {Dmg_Melta} mas de daño"))
                                                

                                            
                                            if isinstance(m, str):
                                                dano_azar = []
                                                for x in range(0, salvar):
                                                    dano_azar.append(AtkDmg_Rand(m, True)+Dmg_Melta)
                                                salvar = sum(dano_azar)
                                            else:
                                                dano = int(m) + Dmg_Melta
                                                salvar*=dano

                                            print(term.black_on_springgreen4(f"A que miniatura se le asignarán {salvar} heridas?"))
                                            print(term.springgreen4_on_black("Presione cualquier tecla para elegir"))
                                            term.inkey()

                                            RepDmg(term, blanco, salvar)

                                        else:
                                            print(term.springgreen4_on_black("Presione cualquier tecla para continuar"))
                                            term.inkey()
                                            continue

                                    ##Prueba de riesgo
                                    if 'Riesgoso' in miembro.rango[indice].claves.keys():
                                        print(term.home + term.clear)
                                        print(term.black_on_springgreen(f"Es hora de tomar una prueba de riesgo"))
                                        d = Dados(1, 6, True)
                                        print(term.black_on_springgreen(f"1D6: {d}"))
                                        lista_blanca = ['Personaje', 'Vehiculo', 'Monstruo']

                                        dano = 0

                                        if any(set(unidad.claves)&set(lista_blanca)) and d == 1:
                                            dano = 3
                                        elif not any(set(unidad.claves)&set(lista_blanca)) and d == 1:
                                            dano = miembro.stats.get("Heridas") - miembro.dmg
                                        elif d != 1:
                                            print(term.black_on_springgreen(f"{miembro.nombre} ha pasado la prueba de riesgo"))
                                            print(term.black_on_springgreen(f"Presione cualquier tecla para continuar"))
                                            term.inkey()
                                            continue
                                        print(term.springgreen4_on_black(miembro.recibir_dano(dano, unidad.habilidades)))
                                        print(term.black_on_springgreen(f"Presione cualquier tecla para continuar"))
                                        term.inkey()
                                        continue
                
                        else:
                            print("El arma ya fue usada")
                            print(term.home + term.clear)
                            continue      
                
                    else:
                        print(term.springgreen4_on_black(f"\nLa tecla presionada '{tecla}' es invalida"))
                        term.inkey()
                        continue

        unidad.atk -= 1
        return

##Funcion de combate cuerpo a cuerpo
def Combate(term, unidad, Ejer_Enem):
    with term.fullscreen(), term.cbreak(), term.hidden_cursor():
        print(term.home + term.clear)
        
        ##Verificar que la unidad no haya retrocedido
        if unidad.atk <= 1:
            print(term.springgreen4_on_black(f"{unidad.nombre} ya no puede combatir en este turno"))
            print(term.springgreen4_on_black("Presiona cualquier tecla para continuar"))
            term.inkey()
            print(term.home + term.clear)
            return   
        
        ##Verificar que la unidad esté en zona de amenaza
        if not unidad.engaged:
            print(term.springgreen4_on_black(f"{unidad.nombre} no puede combatir, está demasiado lejos de un enemigo"))
            print(term.springgreen4_on_black("Presiona cualquier tecla para continuar"))
            term.inkey()
            print(term.home + term.clear)
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

                    print(term.home + term.clear)
                    print(term.springgreen4_on_black(f"Elija un arma para combatir con {miembro.nombre}:"))

                    ##Construir menú

                    for i, arma in enumerate(miembro.mele):
                        if i == indice:
                            print(term.black_on_springgreen4(f"{i+1}. {arma.nombre}"))
                        else:
                            print(term.springgreen4_on_black(f"{i+1}. {arma.nombre}"))

                    tecla = term.inkey()

                    if tecla.name in ("KEY_UP", "KEY_LEFT"):
                        indice = (indice - 1 + len(miembro.mele)) % len(miembro.mele)
                        continue
        
                    elif tecla.name in ("KEY_DOWN", "KEY_RIGHT"):
                        indice = (indice + 1 + len(miembro.mele)) % len(miembro.mele)
                        continue
            
                    elif tecla.name == "KEY_ENTER" or tecla == '\n':
                        if not miembro.mele[indice].usado:

                            ##Si no se ha usado el arma elegida, seguir proceso
                            print(term.springgreen4_on_black(f"\nElegiste: {miembro.mele[indice].nombre}"))                            
                            print(term.home + term.clear)

                            ##Elegir un blanco y recuperar sus claves si es valido
                            blanco = Selec_Blanco(term=term, unidad=unidad, accion='Combatir', Ejer_Enem=Ejer_Enem)
                            if blanco is None:
                                print(term.springgreen4_on_black(f"\nCombatir no es una opción, ¡Lanzate a la batalla!"))
                                term.inkey()                            
                                continue
                            else:
                                ##Tirada para impactar
                                print(term.home + term.clear)

                                n = miembro.mele[indice].stats.get("No. de Ataques")
                                
                                ##Si se repite el arma usar Tirada rapida
                                impact = []
                                nAI = Repetida(miembro.mele[indice], unidad)
                                if nAI > 1:
                                    t = f"\nMultiples miniaturas en {unidad.nombre} usan {miembro.mele[indice].nombre}\nDesea hacer una tirada rápida para combatirlas todas contra {blanco.nombre}?"
                                    r, c = term.get_location()
                                    if Selec_SN(term, r, c, t):
                                        for m in unidad.miembros:
                                            for a in m.mele:
                                                if miembro.mele[indice].nombre == a.nombre and not a.usado:
                                                    impact += Dados(n, 6, False) if isinstance(miembro.mele[indice].stats.get("No. de Ataques"), int) else AtkDmg_Rand(n)
                                                    a.usado = True
                                                    if 'Perfil' in miembro.mele[indice].claves.keys():
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
                                    if 'Perfil' in miembro.mele[indice].claves.keys():
                                        for arma in miembro.mele:
                                            if 'Perfil' in arma.claves.keys():
                                                arma.usado = True
                                            
                                    impact = Dados(n, 6, False) if isinstance(miembro.mele[indice].stats.get("No. de Ataques"), int) else AtkDmg_Rand(n)
                                        
                                print(term.springgreen4_on_black(f"Se han lanzado {len(impact)} ataques"))
                                impact = [dado for dado in impact if dado >= miembro.mele[indice].stats.get("Habilidad")]
                                print(term.springgreen4_on_black("Las tiradas para impactar exitosas:"))
                                print(term.springgreen4_on_black(f"{impact}"))
                                print(term.springgreen4_on_black("Presione cualquier tecla para continuar"))
                                term.inkey()
                                if len(impact) == 0:
                                    break
                                else:
                                    
                                    ##Golpes sostenidos
                                    if 'Golpes Sostenidos' in miembro.mele[indice].claves.keys():
                                        nGS = miembro.mele[indice].claves.get('Golpes Sostenidos')
                                        nAd = 0
                                        print(term.springgreen4_on_black(f"El arma {miembro.mele[indice].nombre} hace golpes sostenidos"))
                                        for dado in impact:
                                            if dado == 6:
                                                nAd += nGS if isinstance(nGS, int) else AtkDmg_Rand(nGS, False)
                                        print(term.springgreen4_on_black(f"Se produjeron {nAd} impactos adicionales")) 
                                        impact += [6] * nAd
                                                
                                
                                    ##Impactos letales
                                    elif 'Impactos Letales' in miembro.mele[indice].claves.keys():
                                        print(term.springgreen4_on_black(f"El arma {miembro.mele[indice].nombre} causa impactos letales"))
                                        seis = [dado for dado in impact if dado == 6]
                                        impact = [dado for dado in impact if dado != 6]
                                        print(term.springgreen4_on_black(f"{len(seis)} impactos fueron letales"))
                                        m = miembro.mele[indice].stats.get("Daño")
                                        for d in seis:
                                            dano += m if isinstance(m, int) else AtkDmg_Rand(m, True)
                                        RepDmg(term, blanco, dano)
                                    
                                    ##Regla Pesada
                                    elif 'Pesado' in miembro.rango[indice].claves.keys() and unidad.mov == 3:
                                        print(term.springgreen4_on_black(f"{unidad.nombre} no se movió en este turno y se beneficia de ello"))
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
                                    if 'Lanza' in miembro.mele[indice].claves.keys() and 'Tem Pelea Primero' in unidad.habilidades.keys():
                                        herir = [dado+1 for dado in herir]
                                    
                                    ##Regla Heridas devastadoras
                                    elif 'Heridas devastadoras' in miembro.mele[indice].claves.keys():
                                        dev = [dado for dado in herir if dado == 6]
                                        herir = [dado for dado in herir if dado != 6]
                                        
                                        if len(dev) != 0:
                                            print(term.black_on_springgreen4(f"{blanco.nombre} ha sufrido heridas devastadoras"))
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

                                            print(term.black_on_springgreen4(f"A que miniatura se le asignarán {salvar} heridas?"))
                                            print(term.springgreen4_on_black("Presione cualquier tecla para continuar"))
                                            term.inkey()

                                            RepDmg(term, blanco, salvar)
                                    
                                    print(term.springgreen4_on_black("Las tiradas que han herido:"))
                                    print(term.springgreen4_on_black(f"{herir}\n"))
                                            
                                    if len(herir) == 0:
                                        print(term.springgreen4_on_black("Presione cualquier tecla para continuar"))
                                        term.inkey()
                                        break

                                    ##Regla anti
                                    if 'Anti' in miembro.mele[indice].claves.keys():
                                        if miembro.mele[indice].claves.get('Anti')[0] in blanco.claves:
                                            a = 0
                                            for i in herir:
                                                if i >= miembro.mele[indice].claves.get('Anti')[1]:
                                                    a += 1
                                            if a:
                                                print(term.black_on_springgreen4(f"{blanco.nombre} ha sufrido heridas mortales!"))
                                                print(term.black_on_springgreen4(f"A que miniatura se le asignarán las heridas?"))
                                                m = miembro.mele[indice].stats.get("Daño")
                                                if isinstance(m, str):
                                                    dano_azar = []
                                                    for x in range(0, a):
                                                        dano_azar.append(AtkDmg_Rand(m, True) )
                                                    dano = sum(dano_azar)
                                                else:
                                                    dano = int(m)
                                                    dano*=a

                                                print(term.springgreen4_on_black("Presione cualquier tecla para continuar"))
                                                term.inkey()

                                                RepDmg(term, blanco, dano)
                                                    


                                    print(term.springgreen4_on_black(f"A continuación, permita al oponente usar la terminal"))
                                    print(term.springgreen4_on_black("Presione cualquier tecla para continuar"))
                                    term.inkey()

                                    if len(blanco.miembros)==0:
                                        continue

                                    index = 0
                                    while True:
                                        print(term.home + term.clear)
                                        print(term.springgreen4_on_black(f"Es momento de las tiradas de salvación de {blanco.nombre}"))
                                        print(term.springgreen4_on_black(f"El factor de perforación del arma atacante es -{miembro.mele[indice].stats.get("Perforación")}"))
                                        
                                        salvacion = blanco.miembros[0].stats.get("Salvación")
                                        if miembro.mele[indice].stats.get("Perforación") > 0:
                                            print(term.springgreen4_on_black(f"La salvación requerida sube a {blanco.miembros[0].stats.get("Salvación") + miembro.mele[indice].stats.get("Perforación")}"))
                                            salvacion += miembro.mele[indice].stats.get("Perforación")

                                        if 'Invulnerable' in blanco.habilidades.keys():
                                            print(term.springgreen4_on_black(f"\nLa unidad atacada tiene una salvación invulnerable de {blanco.habilidades.get('Invulnerable')}"))
                                            print(term.springgreen4_on_black(f"¿Que perfil desea usar?\n"))

                                            S = [f"Salvación regular: {blanco.miembros[0].stats.get('Salvación') + miembro.mele[indice].stats.get('Perforación')}+",
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
                                                    salvacion = blanco.miembros[0].stats.get("Salvación") + miembro.mele[indice].stats.get("Perforación")
                                                    break
                                                elif index == 1:
                                                    salvacion = blanco.habilidades.get('Invulnerable')
                                                    break
                                        
                                        if not 'Invulnerable' in blanco.habilidades.keys():
                                            print(term.springgreen4_on_black("Presione cualquier tecla para continuar"))
                                            term.inkey()
                                            break
                                        
                                    salvar = Dados(len(herir), 6, False)
                                    salvar = [dado for dado in salvar if dado >= salvacion]
                                    print(term.home + term.clear)
                                    print(term.black_on_springgreen4(f"Se han salvado {len(salvar)} de {len(herir)} ataques"))

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

                                        print(term.black_on_springgreen4(f"A que miniatura se le asignarán {salvar} heridas?"))
                                        print(term.springgreen4_on_black("Presione cualquier tecla para elegir"))
                                        term.inkey()

                                        RepDmg(term, blanco, salvar)

                                    else:
                                        print(term.springgreen4_on_black("Presione cualquier tecla para continuar"))
                                        term.inkey()
                                        continue

                                ##Prueba de riesgo
                                if 'Riesgoso' in miembro.mele[indice].claves.keys():
                                    print(term.home + term.clear)
                                    print(term.black_on_springgreen(f"Es hora de tomar una prueba de riesgo"))
                                    d = Dados(1, 6, True)
                                    print(term.black_on_springgreen(f"1D6: {d}"))
                                    lista_blanca = ['Personaje', 'Vehiculo', 'Monstruo']

                                    dano = 0

                                    if any(set(unidad.claves)&set(lista_blanca)) and d == 1:
                                        dano = 3
                                    elif not any(set(unidad.claves)&set(lista_blanca)) and d == 1:
                                        dano = miembro.stats.get("Heridas") - miembro.dmg
                                    elif d != 1:
                                        print(term.black_on_springgreen(f"{miembro.nombre} ha pasado la prueba de riesgo"))
                                        print(term.black_on_springgreen(f"Presione cualquier tecla para continuar"))
                                        term.inkey()
                                        continue
                                    print(term.springgreen4_on_black(miembro.recibir_dano(dano, unidad.habilidades)))
                                    print(term.black_on_springgreen(f"Presione cualquier tecla para continuar"))
                                    term.inkey()
                                    continue
            
                        else:
                            print("El arma ya fue usada")
                            print(term.home + term.clear)
                            continue      
            
                    else:
                        print(term.springgreen4_on_black(f"\nLa tecla presionada '{tecla}' es invalida"))
                        term.inkey()
                        continue

        unidad.atk -= 1
        return


##Reglas de movimiento

##Añadir comprobación de cobertura

##Permanecer estatico
def Estatico(term, unidad, p3 = None):
    while True:
        with term.fullscreen(), term.cbreak(), term.hidden_cursor():
            print(term.springgreen4_on_black(f"La unidad {unidad.nombre} se quedara estatica"))
            print(term.springgreen4_on_black("Presiona cualquier tecla para continuar"))
            term.inkey()
            break
    return
    
##Movimiento normal
def Normal(term, unidad, p3 = None):
    with term.fullscreen(), term.cbreak(), term.hidden_cursor():
        if unidad.mov >= 1:
            print(term.springgreen4_on_black(f"La unidad se moverá hasta {unidad.miembros[0].stats["Movimiento"]} pulgadas"))
            unidad.mov = 1
            print(term.springgreen4_on_black(f"Presione cualquier tecla para continuar"))
            term.inkey()
            return
        else:
            print(term.springgreen4_on_black(f"Esta unidad no se puede mover mas"))
            print(term.springgreen4_on_black(f"Presione cualquier tecla para continuar"))
            term.inkey()
            return
        
##Movimiento de avance
def Avance(term, unidad, p3 = None):
    with term.fullscreen(), term.cbreak(), term.hidden_cursor():
        if unidad.mov >= 2:
            temp = Dados(1, 6)
            print(term.springgreen4_on_black(f"1D6: {temp}"))
            print(term.springgreen4_on_black(f"La unidad avanzará hasta {unidad.miembros[0].stats["Movimiento"]}'' + {temp}'' "))
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

##Movimiento de retroceder/Huida
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
                    if indice == None:
                        break
                    print(term.springgreen4_on_black(unidad.miembros[indice].recibir_dano(unidad.miembros.stats["Heridas"])))
                    unidad.eliminar_muertos()
            print("La huida desesperada ha terminado")
            print("Presione cualquier tecla para continuar")
            term.inkey()
            unidad.mov = 0
            unidad.atk = 0
            unidad.engaged = False
            return
        
        else:
            print(term.springreen4_on_black(f"La unidad retrocederá hasta {unidad.miembros[0].stats.get("Movimiento")}'' "))
            print(term.springreen4_on_black("Recuerde que las miniaturas no pueden terminar este movimiento en zona de amenaza de una unidad enemiga"))
            print(term.springreen4_on_black("\nPresione cualquier tecla para continuar"))
            term.inkey()
            unidad.mov = 0
            unidad.atk = 0
            unidad.engaged = False
            return

##Cargar
def Carga(term, unidad, blanco):
    CadenaIngreso = ''
    while True:
        with term.fullscreen(), term.cbreak(), term.hidden_cursor():
            if blanco is not None:
                print(term.home + term.clear)
                print(term.on_black)
                print(term.springgreen4_on_black(f"Ingrese la distancia entre {unidad.nombre} y {blanco.nombre}"))
                print(term.springgreen4_on_black(CadenaIngreso))
        
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
                            unidad.habilidades.update({"Tem Pelea Primero": None})
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
def ReRoll(Ej, Lista_D, val, DX):
    if Ej.pc:
        Ej.pc -= 1
        for j in Lista_D:
            if j < val:
                Lista_D.pop(j)
                Lista_D.append(Dados(1, DX))
                break

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
def FinViol(term, dic_habs, nombre, Ejers):
    indice = 0
    while True:
        with term.fullscreen(), term.cbreak(), term.hidden_cursor():
            
            n_heridas = dic_habs.get('Final Violento') if isinstance(dic_habs.get('Final Violento'), int) else AtkDmg_Rand(dic_habs.get('Final Violento'), True)
            
            print(term.home + term.clear)
            print(term.on_black)
            print(term.springgreen4_on_black(f"{nombre} ha muerto con un final violento"))
            print(term.springgreen4_on_black(f"Todas las unidades a 6'' o menos sufrirán {n_heridas}\n"))
            print(term.springgreen4_on_black("Seleccionelas a continuación:"))

            All_u = []
            for e in Ejers:
                All_u += e.unidades
    
            for i, opcion in enumerate(All_u + ["Terminar"]):    #Crear lista de opciones
                if i == indice:
                    print(term.black_on_springgreen4(f"{i+1}. {opcion.nombre if isinstance(opcion, Unidad) else opcion}"))
                else:
                    print(term.springgreen4_on_black(f"{i+1}. {opcion.nombre if isinstance(opcion, Unidad) else opcion}"))
    
            tecla = term.inkey()
    
            if tecla.name in ("KEY_UP", "KEY_LEFT"):
                indice = (indice - 1 + len(All_u + ["Terminar"])) % len(All_u + ["Terminar"])
        
            elif tecla.name in ("KEY_DOWN", "KEY_RIGHT"):
                indice = (indice + 1 + len(All_u + ["Terminar"])) % len(All_u + ["Terminar"])
            
            elif tecla.name == "KEY_ENTER" or tecla == '\n':
                if indice > len(All_u)-1:
                    print(term.springgreen4_on_black(f"\nElegiste: Terminar"))
                    return
                else:
                    print(term.springgreen4_on_black(f"\nElegiste: {All_u[indice].nombre}"))
                    print(term.springgreen4_on_black(f"Presione cualquier tecla para continuar"))

                    term.inkey()
                    
                    RepDmg(term, All_u[indice], n_heridas)
                    continue 
                    
            else:
                print(term.springgreen4_on_black(f"\nLa tecla presionada '{tecla}' es invalida"))
                term.inkey()

##Regla empeorar stats si hay daños
def Danado(term, unidad):
    ## 1 a 4 heridas -> resta 1 a tirada para herir
    ## 1 a 5 heridas -> resta 1 "
    
    return

##Funciones GUI
##Elegir ejercitos
def Elegir_Ejs(term):
    ##Función menu
    Ejercitos_diccionarios = [] #Diccionarios provenientes de los JSON
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
                            filepath = Path(__file__).parent / "Ejercitos/Ty_patrol.json"
                            with open(filepath, 'r') as file:
                                Ejercitos_diccionarios.append(json.load(file))
                            if len(Ejercitos_diccionarios) == 2:
                                break
                            else: term.inkey()
                    
                        case 1:
                            filepath = Path(__file__).parent / "Ejercitos/Ty_Tyrannofex.json"
                            with open(filepath, 'r') as file:
                                Ejercitos_diccionarios.append(json.load(file))
                            if len(Ejercitos_diccionarios) == 2:
                                break
                            else: term.inkey()
                    
                        case 2:
                            filepath = Path(__file__).parent / "Ejercitos/UM_patrol.json"
                            with open(filepath, 'r') as file:
                                Ejercitos_diccionarios.append(json.load(file))
                            if len(Ejercitos_diccionarios)  == 2:
                                break
                            else: term.inkey()
                    
                        case 3:
                            filepath = Path(__file__).parent / "Ejercitos/UM_Lancer.json"
                            with open(filepath, 'r') as file:
                                Ejercitos_diccionarios.append(json.load(file))
                            if len(Ejercitos_diccionarios) == 2:
                                break
                            else: term.inkey()
                        
                        case 4:
                            filepath = Path(__file__).parent / "Ejercitos/Debug_army.json"
                            with open(filepath, 'r') as file:
                                Ejercitos_diccionarios.append(json.load(file))
                            if len(Ejercitos_diccionarios) == 2:
                                break
                            else: term.inkey()

            else:
                print(term.springgreen4_on_black(f"\nLa tecla presionada '{tecla}' es invalida"))
                term.inkey()
        
        return Ejercitos_diccionarios

##Construir ejercitos
def Build_Armies(Dics):
    i = 0
    for d in Dics:    #iterar por lista de diccionarios
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

##Función menu
def Menu(term, unidad, TXT:list, FUN:list, par = None):
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
def Conf_usr(term, lista_F:list, lista_T:list, indice_F:int, p1, p2 = None):     ##Enviar terminal, lista de funciones, el indice de la lista y al menos un parametro
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
def Selec_Blanco(term, unidad, accion:str, Ejer_Enem):   ##Accion debe ser una cadena: 'cargar', 'disparar', 'combatir'
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

##Funcion seleccionar miniatura Devuelve indice que la miniatura ocupa en la unidad
def Selec_mini(term, unidad, Precision = False):
    indice = 0
    while True:
        with term.fullscreen(), term.cbreak(), term.hidden_cursor():
            if len(unidad.miembros) == 0:
                print(term.springgreen4_on_black(f"Ya no quedan miembros de {unidad.nombre}"))
                print(term.springgreen4_on_black(f"Presiona cualquier tecla para continuar"))
                term.inkey()
                return None
                
            else:
                
                print(term.springgreen4_on_black(f"Elige una miniatura de {unidad.nombre} para recibir daño"))
                if Precision:
                    print(term.black_on_springgreen4(f"El arma utilizada es de Precision, el atacante puede elegir un Personaje para recibir el daño! (si es visible)"))

                for i, opcion in enumerate(unidad.miembros):    #Crear lista de opciones
                    if i == indice:
                        print(term.black_on_springgreen4(f"{i+1}. {opcion.nombre}   {('(' + opcion.dmg + ')') if opcion.dmg != 0 else ''}"))
                    else:
                        print(term.springgreen4_on_black(f"{i+1}. {opcion.nombre}   {('(' + opcion.dmg + ')') if opcion.dmg != 0 else ''}"))
            
                tecla = term.inkey()

                if tecla.name in ("KEY_UP", "KEY_LEFT"):
                    indice = (indice - 1 + len(unidad.miembros)) % len(unidad.miembros)
        
                elif tecla.name in ("KEY_DOWN", "KEY_RIGHT"):
                    indice = (indice + 1 + len(unidad.miembros)) % len(unidad.miembros)
            
                elif tecla.name == "KEY_ENTER" or tecla == '\n':
                    return indice
                    
                else:
                    print(term.springgreen4_on_black(f"\nLa tecla presionada '{tecla}' es invalida"))
                    term.inkey()

##Eleccion Si NO
def Selec_SN(term, row, col, text):
    indice = 0
    ops = ['Si', 'No']
    while True:
        with term.fullscreen(), term.cbreak(), term.location(row, col), term.hidden_cursor():
            print(term.home + term.clear)
            print(term.springgreen4_on_black(text))
            

            for i, opcion in enumerate(ops):    #Crear lista de opciones
                if i == indice:
                    print(term.black_on_springgreen4(f"{i+1}. {opcion}"))
                else:
                    print(term.springgreen4_on_black(f"{i+1}. {opcion}"))
            
            tecla = term.inkey()

            if tecla.name in ("KEY_UP", "KEY_LEFT"):
                indice = (indice - 1 + len(ops)) % len(ops)
        
            elif tecla.name in ("KEY_DOWN", "KEY_RIGHT"):
                indice = (indice + 1 + len(ops)) % len(ops)
            
            elif tecla.name == "KEY_ENTER" or tecla == '\n':
                return True if indice == 0 else False
                    
            else:
                print(term.springgreen4_on_black(f"\nLa tecla presionada '{tecla}' es invalida"))
                term.inkey()