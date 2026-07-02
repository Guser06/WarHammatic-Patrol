from WHmmatic_lib import Elegir_Ejs, Build_Armies

ejs_dicts = Elegir_Ejs()

ejs_objs = Build_Armies(ejs_dicts)

for e in ejs_objs:
    print(e.id)
    for u in e.unidades:
        print(u.id)
        
        for m in u.miembros:
            print(m.id)
        print()
    print("--------------------")