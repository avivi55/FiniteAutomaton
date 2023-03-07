import curses
from curses.textpad import Textbox, rectangle
import Automata
import AutomataAnimation
import time

class Application:
    def __init__(self):
        curses.wrapper(Application.main_page)

    @staticmethod
    def get_middle(text, width):
        return int((width // 2) - (len(text) // 2) - len(text) % 2)


    @staticmethod
    def automata_page(stdscr, n_automata):
        k = 0
        cursor_x = 0
        cursor_y = 0

        stdscr.clear()
        stdscr.refresh()

        # Start colors in curses
        curses.start_color()
        curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE)

        automata = Automata.Automata(source_file=f"automaton/B4-{n_automata}.txt")

        while k != ord('q'):

            # Initialization
            stdscr.clear()
            height, width = stdscr.getmaxyx()

            cursor_x = max(0, cursor_x)
            cursor_x = min(width - 1, cursor_x)

            cursor_y = max(0, cursor_y)
            cursor_y = min(height - 1, cursor_y)

            statusbarstr = f"Press 'q' to exit | F1 : | "

            stdscr.addstr(height - 1, 0, statusbarstr, curses.color_pair(3))



            stdscr.refresh()

            k = stdscr.getch()
        Application.main_page(stdscr)


    @staticmethod
    def main_page(stdscr):
        stdscr.clear()
        stdscr.refresh()

        curses.start_color()
        curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE)

        height, width = stdscr.getmaxyx()

        title = "Projet Automate Finis"[:width - 1]
        subtitle = "L2 EFREI"[:width - 1]
        statusbarstr = "Ctrl + C Pour QUITTER"

        start_y = int((height // 2) - 2)

        stdscr.addstr(0, 0, f"Debug : Width: {width}, Height: {height}", curses.color_pair(1))

        stdscr.addstr(start_y, Application.get_middle(title, width), title, curses.color_pair(2) | curses.A_BOLD)

        stdscr.addstr(start_y + 1, Application.get_middle(subtitle, width), subtitle)

        stdscr.addstr(start_y + 3, (width // 2) - 2, '----')

        stdscr.addstr(height - 1, 0, statusbarstr, curses.color_pair(3))

        prompt = "entrez de numéro de l'automate : "
        stdscr.addstr(start_y + 5, Application.get_middle(prompt, width), prompt)


        win_x = Application.get_middle(4 * " ", width)
        win = curses.newwin(1, 4, start_y + 7, win_x)
        box = Textbox(win)
        rectangle(stdscr, start_y + 6, win_x - 1, start_y + 8, win_x + 4,)

        stdscr.refresh()

        automata = 'd'
        while (not automata.isdigit()) or int(automata) >= 44:
            box.edit()
            automata = box.gather().strip()

        Application.automata_page(stdscr, automata)


