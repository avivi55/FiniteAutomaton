import graphviz
import tabulate
import string
import os
from copy import deepcopy


class Automata:
    def __init__(self, source_file="automaton/B0-0.txt", output_file="automata", out_type="gif"):
        self.entrees: list[str] = []
        self.exits: list[str] = []
        self.transitions: dict[str, dict[str, list[str]]] = {}
        self.alphabet: list[str] = []
        self.source = source_file
        self.output = output_file
        self.format = out_type

        self.alt_trans = {}
        self.__populate_from_file__(self.source)

    def __str__(self):
        headers = ["E/S", "État"] + self.alphabet
        table = [
            [
                self.__give_state_behaviour__(k),
                k,
            ] + [','.join(self.__fetch_transition__(k, x)) for x in self.alphabet]
            for k in self.transitions.keys()
        ]

        return tabulate.tabulate(table, headers, tablefmt="rounded_grid")

    def __repr__(self):
        try:
            os.mkdir("out")
            os.mkdir("dot")
        except:
            pass

        graphviz.Source(self.to_dot_format()) \
            .render(filename=f'dot/{self.output}.dot', outfile=f'out/{self.output}.{self.format}', view=True)
        return str(self)

    def __eq__(self, other):
        return self.transitions == other.transitions \
            and self.entrees == other.entrees \
            and self.exits == other.exists

    def __give_state_behaviour__(self, state: str):
        res = ""

        if state in self.entrees:
            res += "E "

        if state in self.exits:
            res += "S"

        return res

    def __fetch_transition__(self, state: str, trans: str):
        return self.transitions.get(state).get(trans) or []

    def __populate_from_file__(self, path: str = "B4-0.txt"):
        with open(path, 'r') as f:
            fa_data = f.readlines()

            self.alphabet = list(string.ascii_lowercase[:int(fa_data[0])])

            self.entrees = fa_data[2][:-1].split(' ')[1:]
            self.exits = fa_data[3][:-1].split(' ')[1:]

            for line in fa_data[5:]:
                line = line[:-1] if line[-1] == '\n' else line
                state = ''
                pos = 0
                for i, val in enumerate(line):
                    if val in string.ascii_letters + 'ε':
                        pos = i
                        break
                    state += val

                if self.transitions.get(str(state)):
                    if self.transitions.get(str(state)).get(str(line[pos])):
                        self.transitions[str(state)][line[pos]].append(line[pos + 1:])
                    else:
                        self.transitions[str(state)][line[pos]] = [line[pos + 1:]]
                else:
                    self.transitions[str(state)] = {line[pos]: [line[pos + 1:]]}

        if not len(self.transitions):
            if len(self.entrees):
                for i in self.entrees:
                    self.transitions[i] = {}

        if not len(self.transitions):
            if len(self.exits):
                for i in self.exits:
                    self.transitions[i] = {}

        return self.transitions

    def is_e_nfa(self):
        for state, transitions in self.transitions.items():
            for trans in transitions:
                if 'E' or 'ε' in trans:
                    return True

        return False

    def to_dot_format(self):
        to_dot = "digraph finite_state_machine { rankdir=LR\n"

        to_dot += "\tnode [shape=doublecircle]\n"
        for exit_ in self.exits:
            to_dot += f"\t{str(exit_)}\n"

        to_dot += '\n'

        to_dot += "\tnode [shape=circle]\n"
        for idx, entree in enumerate(self.entrees):
            to_dot += f"\tfake{str(idx)} [style=invisible]\n\tfake{str(idx)} -> {str(entree)}\n"

        to_dot += '\n'

        dic = {}
        for state, transitions in self.transitions.items():
            dic[state] = {}
            for k, v in transitions.items():
                for i in v:
                    if dic[state].get(i):
                        dic[state][i].append(k)
                    else:
                        dic[state][i] = [k]

        print(dic)

        for state, transitions in dic.items():
            for k, v in transitions.items():
                to_dot += f"\t{str(state)} -> {str(k)} [label=\"{str(', '.join(v))}\"] \n"

        to_dot += "}"
        return to_dot

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
        dic = {}
        for i in [standard.transitions.get(x) for x in standard.entrees]:
            for k, v in i.items():
                if dic.get(k):
                    dic[k] += v
                else:
                    dic[k] = v
                dic[k] = list(set(dic[k]))

        standard.transitions["I"] = dic
        standard.entrees = ['I']

        return standard

    def is_complete(self):
        for state in self.transitions.keys():
            for letter in self.alphabet:
                if not self.__fetch_transition__(state, letter):
                    return False
        return True

    def complete(self):
        if self.is_complete():
            return self

        complete = deepcopy(self)
        garbage = [['a', 'P'], ['b', 'P']]

        complete.transitions['P'] = garbage

        for state in self.transitions.keys():
            for letter in self.alphabet:
                if not self.__fetch_transition__(state, letter):
                    complete.transitions[state].append([letter, 'P'])

        return complete

    def is_determinate(self):
        if len(self.entrees) != 1:
            return False

        for x in self.transitions.values():
            lst = []
            for y in x:
                if len(y) >= 2:
                    lst.append(y[0])

            s = list(set(lst))
            if len(s) != len(lst):
                return False

        return True

    def determinize(self):
        if self.is_determinate():
            if self.complete():
                return self
            else:
                return self.complete()

        determinate = deepcopy(self)

        return determinate

    def test_word(self, word):
        if False in [letter in self.alphabet + ['E'] for letter in word]:
            return False

        if not self.is_determinate():
            return False

        cur_state = self.entrees[0]

        for i, letter in enumerate(word):
            next_state = self.__fetch_transition__(cur_state, letter)

            cur_state = next_state

    def is_miniminized(self):
        pass
        # TODO

    def miniminize(self):
        return self
        # TODO
