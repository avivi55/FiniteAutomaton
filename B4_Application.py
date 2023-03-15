import curses
from curses.textpad import Textbox, rectangle
import threading
import types
import B4_Automata
from B4_AutomataAnimation import AutomataAnimation as Anim


def get_middle(text, width):
    """
    Returns the middle of the text, based on the width given.
    If there is no exact middle (i.e., if it's an even number), then return the left middle.

    :param text: Specify what text to print in the middle of the box
    :param width: Determine the width of the box
    :return: The middle of the text
    """
    return int((width // 2) - (len(text) // 2) - len(text) % 2)


def erase_warning(window, warning, x, y):
    window.addstr(y, x, ' ' * len(warning))
    window.move(0, 0)
    window.refresh()


def get_guide(guide, width):
    """
    Takes in a dictionary of keybindings and returns a list of string that are formatted to be printed out as the guide.

    :param guide: Get the keybindings for each category
    :param width: Determine the width of the guide
    :return: A list of strings that are the keybindings
    """
    guide_s = []

    for category, keybinds in guide.items():
        keybindings = ""
        for key, binding in keybinds.items():
            keybindings += f"{key} : {binding} | "
        keybindings = keybindings[:-2]

        line = f"{keybindings:^{width - 1}}"

        for i, letter in enumerate(category):
            line = line[0:i] + letter + line[i + 1:]

        if len(line) != width - 1:
            line += ' '

        guide_s.append(line)

    return guide_s


def info_page(window, A: B4_Automata.Automata, func, name):
    window.clear()
    height, width = window.getmaxyx()

    automata = str(A).split('\n')
    det_automata = str(func(A)).split('\n')
    start_y = get_middle(len(automata) * ' ', height)

    if automata == det_automata:
        warning = "L'automate l'est déjà"
        window.addstr(height - 10, get_middle(warning, width), warning)
        threading.Timer(3, erase_warning, [window, warning, get_middle(warning, width), height - 10]).start()
        return False

    if det_automata == ['']:
        return False

    margin = (width - (len(automata[0]) + len(det_automata[0]))) // 3

    x = 2 * margin + len(automata[0])

    window.addstr(start_y - 2, margin, "Base : ")
    window.addstr(start_y - 2, x, f"{name} : ")

    for i, line in enumerate(automata):
        window.addstr(start_y + i, margin, line)

    for i, line in enumerate(det_automata):
        window.addstr(start_y + i, x, line)

    window.refresh()

    return True


def word_test_page(window, automata: B4_Automata.Automata, n_automata):
    window.clear()

    height, width = window.getmaxyx()
    automata = automata.get_determinized()
    automata_lst = str(automata).split('\n')
    start_y = get_middle(len(automata_lst) * ' ', height)

    prompt = "Entrez un mot de test : "
    window.addstr(start_y - 2, get_middle(prompt, width), prompt)

    win_x = get_middle(20 * " ", width)
    win = curses.newwin(1, 20, start_y + 1, win_x)
    box = Textbox(win)
    rectangle(window, start_y, win_x - 1, start_y + 2, win_x + 20)

    guide = {
        " ": {"": ""},
        "": {"M": "Menu de l'automate"},
        "  ": {"": ""},
    }

    guide_s = get_guide(guide, width)

    while True:
        for i, line in enumerate(automata_lst):
            window.addstr(start_y + 10 + i, get_middle(line, width), line)

        for i, line in enumerate(guide_s):
            window.addstr((height - len(guide_s)) + i, 0, line, curses.color_pair(3))

        window.addstr(start_y - 7, get_middle(f"Automate n°{n_automata}", width), f"Automate n°{n_automata}", curses.A_UNDERLINE)

        warning = "L'automate à été automatiquement déterminisé pour faire le test de mot"
        window.addstr(start_y - 5, get_middle(warning, width), warning, curses.A_BOLD)

        window.refresh()
        box.edit()
        word = box.gather().strip()
        answer = str(automata.test_word(word.strip()))

        erase_warning(window, width*' ', 0, start_y + 5)
        window.addstr(start_y + 5, get_middle(f"Mot : '{word}'", width), f"Mot : '{word}'")

        window.addstr(start_y + 7, 0, width * ' ')
        window.addstr(start_y + 7, get_middle(answer, width), answer)

        window.move(0, 0)

        window.refresh()
        k = window.getch()
        if chr(k) == 'm' or chr(k) == 'M':
            return False
        else:
            continue


def automata_page(window, n_automata):
    """
    The automata_page function is the main function of the program.
    It displays an automata and allows you to interact with it.
    You can see its info, standardize it, determinize it, complete it or test words on the automata.
    You can also display a graph of these automata using Graphviz or animate its standardization/determinization.

    :param window: The window
    :param n_automata: Display the number of the automata in the title
    :return: None
    """
    height, width = window.getmaxyx()
    automata = B4_Automata.Automata(source_file=f"automaton/B4-{n_automata}.txt")
    automata_lst = str(automata).split('\n')
    start_y = get_middle(len(automata_lst) * ' ', height)
    no_change: bool = False

    f = types.SimpleNamespace()
    f._1 = 265
    f._2 = 266
    f._3 = 267
    f._4 = 268
    f._5 = 269
    f._6 = 270

    guide = {
        "": {
            "<Space>": "Seulement l'automate"
        },
        "Commandes :": {
            "P": "Page principale",
            "I": "Information",
            "C": "Compléter",
            "S": "Standardiser",
            "D": "Détérminiser",
            "O": "Complémentaire",
            "W": "Test de mots",
            "M": "Minimiser"
        },
        "Rendu graphique simple :": {
            "F1": "Automtate de base",
            "F2": "Standardisé",
            "F3": "Déterministe et Complet",
            "F4": "Complémentaire"
        },
        "Rendu animé (lance .gif) :": {
            "F5": "Standardisé",
            "F6": "Déterministe et Complet",
        }
    }

    guide_s = get_guide(guide, width)
    clear = True
    while True:
        height, width = window.getmaxyx()

        if not no_change:
            if clear:
                window.clear()
                clear = False
            for i, line in enumerate(automata_lst):
                window.addstr(start_y + i, get_middle(line, width), line)
            window.refresh()

        window.addstr(start_y - 7, get_middle(f"Automate n°{n_automata}", width), f"Automate n°{n_automata}", curses.A_UNDERLINE)

        for i, line in enumerate(guide_s):
            window.addstr((height - len(guide_s)) + i, 0, line, curses.color_pair(3))

        k = window.getch()

        match chr(k):
            case 'p' | 'P':
                return
            case 'd' | 'D':
                no_change = info_page(window, automata, lambda x: x.get_determinized(), "Détérminisé et Complet")
            case 'i' | 'I':
                no_change = info_page(window, automata, lambda x: x.get_info(), "Info")
            case 's' | 'S':
                no_change = info_page(window, automata, lambda x: x.get_standard(), "Standard")
            case 'c' | 'C':
                no_change = info_page(window, automata, lambda x: x.get_complete(), "Complet")
            case 'o' | 'O':
                no_change = info_page(window, automata, lambda x: x.get_complementary(),
                                      "Automate langage complémentaire de l'automate déterminisé")
            case 'w' | 'W':
                no_change = word_test_page(window, automata, n_automata)
                clear = True
            case 'm' | 'M':
                no_change = info_page(window, automata, lambda x: x.get_minimized(), "Minime")
            case _:
                match k:
                    case f._1:
                        no_change = info_page(window, automata, lambda x: repr(x), "")
                    case f._2:
                        no_change = info_page(window, automata, lambda x: repr(x.get_standard()), "")
                    case f._3:
                        no_change = info_page(window, automata, lambda x: repr(x.get_determinized()), "")
                    case f._4:
                        no_change = info_page(window, automata, lambda x: repr(x.get_complementary()), "")
                    case f._5:
                        no_change = info_page(window, automata, lambda x: Anim.standardize_animation(x, view=True), "")
                    case f._6:  # F2
                        no_change = info_page(window, automata, lambda x: Anim.determinize_animation(x, view=True), "")
                    case 32: #space
                        no_change = False
                        clear = True
                    case _:
                        no_change = True


def main_page(window):
    """
    The function called when the program starts.
    It displays a title, a subtitle and an input box to enter the number of automata you want to use.
    The user can only enter numbers between 0 and 44 (included).
    If he enters something else, an error message will be displayed.

    :param window: The window
    :return: The automata number
    """
    window.clear()
    window.refresh()

    height, width = window.getmaxyx()

    title = "Projet Automate Finis"[:width - 1]
    subtitle = "L2 EFREI"[:width - 1]
    statusbarstr = "Ctrl + C Pour QUITTER"

    start_y = int((height // 2) - 2)

    window.addstr(0, 0, "Jacques Soghomonyan")
    window.addstr(1, 0, "Nicolas Chalumeau")
    window.addstr(2, 0, "Antoine Ribot")
    window.addstr(3, 0, "Adrien Pouyat")
    window.addstr(start_y, get_middle(title, width), title, curses.color_pair(2) | curses.A_BOLD)
    window.addstr(start_y + 1, get_middle(subtitle, width), subtitle)
    window.addstr(start_y + 3, (width // 2) - 2, '----')

    window.addstr(height - 1, 0, statusbarstr, curses.color_pair(3))

    prompt = "Entrez le numéro de l'automate : "
    window.addstr(start_y + 5, get_middle(prompt, width), prompt)

    win_x = get_middle(4 * " ", width)
    win = curses.newwin(1, 3, start_y + 7, win_x)
    box = Textbox(win)
    rectangle(window, start_y + 6, win_x - 1, start_y + 8, win_x + 4)

    window.refresh()

    while True:
        box.edit()
        automata = box.gather().strip()

        if automata.isdigit() and int(automata) <= 44:
            break
        else:
            warning: str = "Veuillez entrer un numéro entre 0 et 44 !!"
            window.addstr(start_y + 9, get_middle(warning, width), warning, curses.color_pair(1) | curses.A_BOLD)
            window.refresh()

    return automata


def main_loop(window):
    """
    The main function of the program. It handles all
    the curses functionality and calls other functions to display information on
    the screen. The main_loop function also handles user input, which is used to
    determine what page should be displayed next.

    :param window: The window
    :return: None
    """
    try:
        window.clear()
        window.refresh()

        curses.start_color()
        curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_BLUE, curses.COLOR_WHITE)

        while True:
            window.clear()

            num = main_page(window)

            window.clear()

            automata_page(window, num)

            window.addstr(10, 10, str(num))

    except KeyboardInterrupt:
        return


def run():
    curses.wrapper(main_loop)
