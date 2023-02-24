from Automata import Automata
import time

t = Automata()
t.populate_from_file()

print(t)

choices = [
    "Afficher l'automate dans <test_automata.txt>",
    "Afficher les informations de l'automate dans <test_automata.txt>",
    "Standardiser et afficher l'automate dans <test_automata.txt>",
    "Déterminiser et afficher l'automate dans <test_automata.txt>",
    "Minimiser et afficher l'automate dans <test_automata.txt>",
    "Testage de reconnaissance mots de l'automate dans <test_automata.txt>",
    "Afficher l'automate reconnaissant le langage complémentaire de l'automate dans <test_automata.txt>",
]


def aff():
    repr(t)


def info():
    print(f"Standard : {t.is_standard()}\n"
          f"Déterministe : {t.is_determinate()}\n"
          f"Complet : {t.is_complete()}")


def std():
    repr(t.standardize())


def dtm():
    repr(t.determinize())


def mini():
    repr(t.miniminize())


choice_fun = [
    aff,
    info,
    std,
    dtm,
    mini,
]

user_choice = -1

while True:
    break
    for i, choice in enumerate(choices):
        print(f"{i}. {choice}")
    user_choice = int(input("Choix : "))

    choice_fun[user_choice]()

    time.sleep(1)


