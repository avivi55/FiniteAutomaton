import graphviz
import tabulate
import string
import os
from copy import deepcopy


class Automata:
    def __init__(self, source_file="", output_file="automata", out_type="gif"):
        self.entrees: list[str] = []
        self.exits: list[str] = []
        self.transitions: dict[str, dict[str, list[str]]] = {}
        self.alphabet: list[str] = []
        self.source = source_file
        self.output = output_file
        self.format = out_type

        self.alt_trans = {}

        if source_file:
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

    def __populate_from_file__(self, path: str):
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

                if self.transitions.get(state):
                    if self.transitions.get(state).get(line[pos]):
                        self.transitions[state][line[pos]].append(line[pos + 1:])
                        self.transitions[state][line[pos]].sort()
                    else:
                        self.transitions[state][line[pos]] = [line[pos + 1:]]
                else:
                    self.transitions[state] = {line[pos]: [line[pos + 1:]]}

        if not len(self.transitions):
            if len(self.entrees):
                for i in self.entrees:
                    self.transitions[i] = {}

        if not len(self.transitions):
            if len(self.exits):
                for i in self.exits:
                    self.transitions[i] = {}

        return self.transitions

    def __different_transitions_dict__(self):
        dic = {}
        for state, transitions in self.transitions.items():
            dic[state] = {}
            for k, v in transitions.items():
                for i in v:
                    if dic[state].get(i):
                        dic[state][i].append(k)
                    else:
                        dic[state][i] = [k]
        return dic

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
            to_dot += f"\t{''.join(exit_.split('-'))}\n"

        to_dot += '\n'

        to_dot += "\tnode [shape=circle]\n"
        for idx, entree in enumerate(self.entrees):
            to_dot += f"\tfake{str(idx)} [style=invisible]\n\tfake{str(idx)} -> {''.join(entree.split('-'))}\n"

        to_dot += '\n'

        for state, transitions in self.__different_transitions_dict__().items():
            for k, v in transitions.items():
                to_dot += f"\t{''.join(state.split('-'))} -> {''.join(k.split('-'))} [label=\"{str(', '.join(v))}\"] \n"

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
        garbage = {'a': ['P'],
                   'b': ['P']}

        complete.transitions['P'] = garbage

        for state in self.transitions.keys():
            for letter in self.alphabet:
                if not self.__fetch_transition__(state, letter):
                    complete.transitions[state][letter] = ['P']

        return complete

    def is_determinate(self):
        if len(self.entrees) != 1:
            return False

        for transition in self.transitions.values():
            for label, states in transition.items():
                if len(states) > 1:
                    return False

        return True

    def determinize(self, print_steps=False):
        if self.is_determinate():
            if self.complete():
                return self
            else:
                return self.complete()

        determinate = Automata()
        determinate.alphabet = self.alphabet.copy()

        # unite the entrees
        new_entree = {}
        for i in self.entrees:
            for k in self.transitions.get(i):
                if new_entree.get(k):
                    new_entree[k] += self.transitions.get(i).get(k).copy()
                else:
                    new_entree[k] = self.transitions.get(i).get(k).copy()

                new_entree[k] = sorted(list(set(new_entree[k])))

        for k, v in new_entree.items():
            new_entree[k] = ['-'.join(v)]

        new_entree = {'-'.join(self.entrees): new_entree}

        ###

        # populate the transitions dict
        determinate.entrees = list(new_entree.keys())
        determinate.exits = []

        for i in self.entrees:
            if i in self.exits:
                determinate.exits.append('-'.join(self.entrees))

        determinate.transitions = deepcopy(new_entree)

        state_buffer = []
        for x in new_entree.values():
            for y in x.values():
                state_buffer += y

        state_buffer = list(set(state_buffer))

        while state_buffer:
            cur_state = state_buffer.pop()

            det_tr = determinate.transitions

            det_tr[cur_state] = {}

            if self.transitions.get(cur_state):
                for k, v in self.transitions.get(cur_state).items():
                    det_tr[cur_state][k] = ['-'.join(v)]

                if cur_state in self.exits:
                    determinate.exits.append(cur_state)

            elif not det_tr.get(cur_state):
                states = list(set(cur_state.split('-')))

                for letter in determinate.alphabet:
                    det_tr.get(cur_state)[letter] = []

                for i in states:
                    for k, v in self.transitions.get(i).items():
                        temp = det_tr.get(cur_state)[k]
                        temp += v
                        det_tr.get(cur_state)[k] = list(set(temp))
                        for j in det_tr.get(cur_state)[k]:
                            if j in self.exits:
                                determinate.exits.append(cur_state)

            for x in det_tr.get(cur_state).values():
                y = '-'.join(x)
                if y and (y not in det_tr.keys()) and y not in state_buffer:
                    state_buffer.append(y)

            for k, v in det_tr.get(cur_state).items():
                det_tr.get(cur_state)[k] = ['-'.join(v)]

        return determinate

    def test_word(self, word):
        if False in [letter in self.alphabet + ['E', 'ε'] for letter in word]:
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
