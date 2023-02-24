import graphviz
import string


class Automata:
    def __init__(self):
        self.entrees: list[str] = []
        self.exits: list[str] = []
        self.transitions: dict[str, list[list[str, str]]] = {}
        self.alphabet: list[str] = []

    def __str__(self):
        to_dot = "digraph finite_state_machine { rankdir=LR\n"

        to_dot += "\tnode [shape=doublecircle]\n"
        for exit_ in self.exits:
            to_dot += f"\t{str(exit_)}\n"

        to_dot += '\n'

        for idx, entree in enumerate(self.entrees):
            to_dot += f"\tfake{str(idx)} [style=invisible]\n\tfake{str(idx)} -> {str(entree)} [shape=circle]\n"

        to_dot += '\n'

        to_dot += "\tnode [shape=circle]\n"
        for state, transitions in self.transitions.items():
            for other_state in transitions:
                to_dot += f"\t{str(state)} -> {str(other_state[1])} [label=\"{str(other_state[0])}\"] \n"

        to_dot += "}"
        return to_dot

    def __repr__(self):
        graphviz.Source(str(self)).view()
        return str(self)

    def __eq__(self, other):
        return self.transitions == other.transitions \
            and self.entrees == other.entrees \
            and self.exits == other.exists

    def populate_from_file(self, path: str = "test_automata.txt"):
        with open(path, 'r') as f:
            fa_data = f.readlines()

            self.alphabet = string.ascii_lowercase[:int(fa_data[0])]

            self.entrees = fa_data[2][:-1].split(' ')[1:]
            self.exits = fa_data[3][:-1].split(' ')[1:]

            for line in fa_data[5:]:
                try:
                    lst = [int(trans[1]) for trans in self.transitions[str(line[0])] if trans[1] == line[2]]
                    if len(lst):
                        for transition in lst:
                            self.transitions[str(line[0])][transition][0] += f", {line[1]}"
                    else:
                        self.transitions[str(line[0])] += [[line[1], line[2]]]
                except:
                    self.transitions[str(line[0])] = [[line[1], line[2]]]

    def is_standard(self):
        if len(self.entrees) != 1:
            return False

        for transitions in self.transitions.values():
            for transition in transitions:
                if self.entrees[0] in transition:
                    return False

        return True

    def standardize(self):
        if self.is_standard():
            return self

        new_start_trans = []

        for i in [self.transitions[x] for x in self.entrees]:
            for j in i:
                new_start_trans.append(j)

        self.entrees = ['I']

        self.transitions['I'] = new_start_trans
        return self

