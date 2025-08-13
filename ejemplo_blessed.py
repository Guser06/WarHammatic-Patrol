from blessed import Terminal

term = Terminal()

MENU_OPTIONS = [
    'Option 1',
    'Option 2',
    'Option 3',
    'Exit',
]

def display_menu():
    selectedIndex = 0

    with term.fullscreen(), term.cbreak(), term.hidden_cursor():
        while True:
            print(term.home + term.clear)  # Limpia pantalla
            print(term.underline("Pick an option:\n"))

            for i, option in enumerate(MENU_OPTIONS):
                if i == selectedIndex:
                    print(term.black_on_white(f"{i+1}. {option}"))
                else:
                    print(term.white_on_black(f"{i+1}. {option}"))

            key = term.inkey()

            if key.name in ("KEY_UP", "KEY_LEFT"):
                selectedIndex = (selectedIndex - 1) % len(MENU_OPTIONS)

            elif key.name in ("KEY_DOWN", "KEY_RIGHT"):
                selectedIndex = (selectedIndex + 1) % len(MENU_OPTIONS)

            elif key.name == "KEY_ENTER" or key == '\n':
                if selectedIndex == len(MENU_OPTIONS) - 1:
                    break
                print(f"\nYou chose {MENU_OPTIONS[selectedIndex]}")
                term.inkey()  # Espera tecla

            else:
                print(f"\nThe pressed key '{key}' is not associated with a menu function.")
                term.inkey()  # Espera tecla


if __name__ == '__main__':
    display_menu()
