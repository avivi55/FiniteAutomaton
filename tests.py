from Automata import Automata
from AutomataAnimation import AutomataAnimation


for i in range(3):
    current_automata = f"automaton/B4-{i}.txt"
    t = Automata(source_file=current_automata, output_file=f"B4-{i}")
    #print(repr(t))#.standardize().to_dot_format())
    AutomataAnimation.standardize_animation(t)
    # print(f"{i} :")
    # print(repr(t))

