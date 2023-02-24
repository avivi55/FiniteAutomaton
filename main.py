from Automata import Automata
import time

t = Automata()

current_automata = "B4-0.txt"

choices = [
    f"Afficher l'automate dans <{current_automata}>",
    f"Afficher les informations de l'automate dans <{current_automata}>",
    f"Standardiser et afficher l'automate dans <{current_automata}>",
    f"Déterminiser et afficher l'automate dans <{current_automata}>",
    f"Minimiser et afficher l'automate dans <{current_automata}>",
    f"Testage de reconnaissance mots de l'automate dans <{current_automata}>",
    f"Afficher l'automate reconnaissant le langage complémentaire de l'automate dans <{current_automata}>",
]


def aff():
    print(repr(t))


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
    current_automata = f"B4-{input('Choisir le fichier de l automate')}.txt"
    print(current_automata)
    t.populate_from_file(current_automata)
    for i, choice in enumerate(choices):
        print(f"{i}. {choice}")
    user_choice = int(input("Choix : "))

    choice_fun[user_choice]()

    time.sleep(1)


