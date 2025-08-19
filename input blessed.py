import blessed

term = blessed.Terminal()
textString = ''

print(term.home + term.clear)
print(term.underline('Ingrese el limite de rondas'))

while True:
    with term.cbreak(), term.hidden_cursor():
        
        keyInput = term.inkey()
        
        if keyInput and (keyInput.is_sequence == False):
            textString += keyInput
            print(term.move_x(0), end='')
            print(f"{textString}", end='', flush=True)
            continue
        
        elif keyInput.name == "KEY_ENTER":
            print(f"\nIngresaste: {textString}")
            print("\nPresiona ENTER para continuar")
            print("\nPresiona cualquier tecla para reintentar")
            
            keyInput = term.inkey()
            
            if keyInput.name == "KEY_ENTER" or keyInput == '\n':
                break
            else:
                textString = ''
                print(term.home + term.clear)
                print(term.underline('Ingrese el limite de rondas'))
                continue