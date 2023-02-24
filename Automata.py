import graphviz
import string
from copy import deepcopy
import tabulate

class Automata:
    def __init__(self, path="automata"):
        self.entrees: list[str] = []
        self.exits: list[str] = []
        self.transitions: dict[str, list[list[str, str]]] = {}
        self.alphabet: list[str] = []
        self.path = path

    def __str__(self):
        headers = [
            "E/S",
            "État",
        ]
        headers += self.alphabet
        table = []

        for k, v in self.transitions.items():
            table.append([self.__state_is_e_s(k)] + [k] + [self.__fetch_transition(k, x) for x in self.alphabet])

        return tabulate.tabulate(table, headers, tablefmt="rounded_grid")

    def __repr__(self):
        graphviz.Source(str(self)).view(filename=self.path)
        return self.to_dot_format()

    def __eq__(self, other):
        return self.transitions == other.transitions \
            and self.entrees == other.entrees \
            and self.exits == other.exists

    def __state_is_e_s(self, state: str):
        res = " "

        if state in self.entrees:
            res += "E "

        if state in self.exits:
            res += "S"

        return res

    def __fetch_transition(self, start_state: str, trans: str):
        res = "."
        for transition in self.transitions[start_state]:
            if transition[0] == trans:
                res = transition[1]
                break
        return res

    def to_dot_format(self):
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

    def populate_from_file(self, path: str = "test_automata.txt"):
        with open(path, 'r') as f:
            fa_data = f.readlines()

            self.alphabet = list(string.ascii_lowercase[:int(fa_data[0])])

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

        standard = deepcopy(self)
        new_start_trans = []

        for i in [standard.transitions[x] for x in standard.entrees]:
            for j in i:
                new_start_trans.append(j)

        standard.entrees = ['I']

        standard.transitions['I'] = new_start_trans
        return standard


    def is_complete(self):
        pass
        # TODO

    def complete(self):
        return self
        # TODO

    def is_determinate(self):
        pass
        # TODO

    def determinize(self):
        return self
        # TODO

    def is_miniminized(self):
        pass
        # TODO

    def miniminize(self):
        return self
        # TODO