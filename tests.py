from Automata import Automata



for i in range(45):
    t = Automata()
    current_automata = f"automaton/B4-{i}.txt"
    t.path = f"B4-{i}"
    t.populate_from_file(current_automata)
    repr(t)
