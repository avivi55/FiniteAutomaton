from Automata import Automata

t = Automata()
t.populate_from_file()


repr(t.is_standard())
repr(t.standardize())
