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
