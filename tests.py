from Automata import Automata

t = Automata()

current_automata = "B4-0.txt"
t.populate_from_file(current_automata)
print(repr(t))
