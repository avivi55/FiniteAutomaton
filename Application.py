import curses
from curses.textpad import Textbox, rectangle
import threading
import Automata
from typing import Callable
import tabulate
import AutomataAnimation


def get_middle(text, width):
    return int((width // 2) - (len(text) // 2) - len(text) % 2)


def info_page(window, A: Automata.Automata, func: Callable[[Automata.Automata], Automata.Automata | str], name):
    height, width = window.getmaxyx()
    automata = str(A).split('\n')
    det_automata = str(func(A)).split('\n')
    start_y = get_middle(len(automata) * ' ', height)
    margin = (width - (len(automata[0]) + len(det_automata[0])))//3

    x = 2 * margin + len(automata[0])


    window.clear()
    window.addstr(start_y - 2, margin, "Base : ")
    window.addstr(start_y - 2, x, f"{name} : ")
    # window.refresh()
    for i, line in enumerate(automata):
        window.addstr(start_y + i, margin, line)

    for i, line in enumerate(det_automata):
        window.addstr(start_y + i, x, line)

    # window.clear()
    window.refresh()

    return True


def automata_page(window, n_automata):
    height, width = window.getmaxyx()
    A = Automata.Automata(source_file=f"automaton/B4-{n_automata}.txt")
    automata = str(A).split('\n')
    start_y = get_middle(len(automata) * ' ', height)
    change: bool = False

    while True:
        height, width = window.getmaxyx()

        if not change:
            for i, line in enumerate(automata):
                window.addstr(start_y + i, get_middle(line, width), line)

        window.addstr(height - 2, 0, "M Page principal: | I : Info | S : Standardisé | D : Déterminisé | C : Complet \n"
                                     "R : Rendu graphique | A : Rendu animé", curses.color_pair(3))
        k = window.getch()
        if k == ord('m') or k == ord('M'):
            return
        elif k == ord('d') or k == ord('D'):
            change = info_page(window, A, lambda x: x.get_determinized(), "Détérminisé")
        elif k == ord('i') or k == ord('I'):
            change = info_page(window, A, lambda x: x.get_info(), "Info")
        elif k == ord('s') or k == ord('S'):
            change = info_page(window, A, lambda x: x.get_standard(), "Standard")
        elif k == ord('c') or k == ord('C'):
            change = info_page(window, A, lambda x: x.get_complete(), "Complet")

def erase_warning(window, warning, x, y):
    window.addstr(y, x, ' ' * len(warning), curses.color_pair(1) | curses.A_BOLD)
    window.refresh()


def main_page(window):
    window.clear()
    window.refresh()

    height, width = window.getmaxyx()

    title = "Projet Automate Finis"[:width - 1]
    subtitle = "L2 EFREI"[:width - 1]
    statusbarstr = "Ctrl + C Pour QUITTER"

    start_y = int((height // 2) - 2)

    window.addstr(start_y, get_middle(title, width), title, curses.color_pair(2) | curses.A_BOLD)
    window.addstr(start_y + 1, get_middle(subtitle, width), subtitle)
    window.addstr(start_y + 3, (width // 2) - 2, '----')

    window.addstr(height - 1, 0, statusbarstr, curses.color_pair(3))

    prompt = "Entrez de numéro de l'automate : "
    window.addstr(start_y + 5, get_middle(prompt, width), prompt)

    win_x = get_middle(4 * " ", width)
    win = curses.newwin(1, 4, start_y + 7, win_x)
    box = Textbox(win)
    rectangle(window, start_y + 6, win_x - 1, start_y + 8, win_x + 4,)

    window.refresh()

    while True:
        box.edit()
        automata = box.gather().strip()

        if automata.isdigit() and int(automata) <= 44:
            break
        else:
            warning: str = "Veuillez entrer un numéro entre 0 et 44 !!"
            window.addstr(start_y + 9, get_middle(warning, width), warning,  curses.color_pair(1) | curses.A_BOLD)
            window.refresh()

            threading.Timer(3, erase_warning, [window, warning, get_middle(warning, width), start_y + 9]).start()

    return automata


def main_loop(window):
    try:
        window.clear()
        window.refresh()

        curses.start_color()
        curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE)

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
