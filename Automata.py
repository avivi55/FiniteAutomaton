import graphviz
import tabulate
import string
import os
from copy import deepcopy


class Automata:
    """
    A class to represent an automata.

    Attributes
    ----------
    entrees
        list of initial states

    exits
        list of terminal states

    alphabet
        list of letter making the alphabet of the automata

    source
        a path for the .txt file the automata will get its transitions

    output
        the name of the output files

    format
        the format output (.gif, .png ...)

    transitions
        the transition dictionary
        it is composed as such:
        {
            'state1' : {
                'letter1' : [ 'state2', 'state1' ],
                'letter2' : [ 'state3' ],
            },
            'state2' : {
                'letter1' : [],
                'letter2' : [ 'state3' ]
            },
            'state3' : {
                'letter1' : [ 'state3' ],
                'letter2' : [],
            },
        }
    """

    def __init__(self, source_file="", output_file="automata", out_type="gif"):
        self.entrees: list[str] = []
        self.exits: list[str] = []
        self.transitions: dict[str, dict[str, list[str]]] = {}
        self.alphabet: list[str] = []

        self.source: str = source_file
        self.output: str = output_file
        self.format: str = out_type

        if source_file:
            self._populate_from_file_(self.source)

    def __str__(self):
        headers = ["E/S", "État"] + self.alphabet
        table = [
            [
                self._give_state_behaviour_(k),
                k,
            ] + [','.join(self._fetch_transition_(k, x)) for x in self.alphabet]
            for k in self.transitions.keys()]

        return tabulate.tabulate(table, headers, tablefmt="rounded_grid")

    def __repr__(self):
        try:
            os.mkdir("out")
            os.mkdir("dot")
        except OSError:
            pass
        else:
            pass

        graphviz.Source(self.to_dot_format()) \
            .render(filename=f'dot/{self.output}.dot', outfile=f'out/{self.output}.{self.format}', view=True)
        return str(self)

    def __eq__(self, other):
        return self.transitions == other.transitions \
            and self.entrees == other.entrees \
            and self.exits == other.exists

    def _give_state_behaviour_(self, state: str, arrows: bool = True) -> str:
        """
        Indicates whether a state is terminal, initial or both

        Parameters
        -------
        state
            The state to analyse
        arrows
            The fancy notation or with letters

        Returns
        -------
        str
            An indication of initial or/and terminal behaviour of the state
        """
        if state in self.entrees and state in self.exits:
            return '<-->' if arrows else 'E S'

        if state in self.entrees:
            return '-->' if arrows else 'E'

        if state in self.exits:
            return '<--' if arrows else 'S'

        return ''

    def _fetch_transition_(self, state: str, letter: str) -> list[str]:
        """
        Gets the list of states the `state` is going to with the letter `letter`

        Parameters
        -------
        state
            The state to get
        letter
            the letter

        Returns
        -------
        list[str]
            the list of states in the transition dict
        """
        return self.transitions.get(state).get(letter) or []

    def _populate_from_file_(self, path: str) -> object:
        """
        Fills the transition dict with a .txt file

        Parameters
        -------
        path
            the path of the .txt file

        Returns
        -------
        object
            self
        """
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
                    if self._fetch_transition_(state, line[pos]):
                        self.transitions[state][line[pos]].append(line[pos + 1:])
                        self.transitions[state][line[pos]].sort()
                    else:
                        self.transitions[state][line[pos]] = [line[pos + 1:]]
                else:
                    self.transitions[state] = {line[pos]: [line[pos + 1:]]}

        # if I modify self.transitions directly it changes the size of the iter and breaks
        # it is equivalent ot a temp variable
        i_dont_want_to_break_things: dict[str, dict[str, list[str]]] = {}

        for state, transitions in self.transitions.items():
            for letter, states in transitions.items():
                for i in states:
                    if i not in self.transitions.keys():
                        i_dont_want_to_break_things[i] = {letter: [] for letter in self.alphabet}

        self.transitions |= i_dont_want_to_break_things

        return self.transitions

    def _different_transitions_dict_(self) -> dict[str, dict[str, list]]:
        """
        Creates a different organization for the transition dict

        Returns
        -------
        dict
            {
                'state1' : {
                    'state1' : [ 'letter1' ],
                    'state2' : [ 'letter1' ],
                    'state3' : [ 'letter2' ],
                },
                ...
            }
        """
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

    def _state_is_empty_(self, state: str, letter: str) -> bool:
        return not self._fetch_transition_(state, letter) \
            or self._fetch_transition_(state, letter) == ['']

    def is_e_nfa(self) -> bool:
        """
        Gives whether the automata hase epsilon transitions

        Returns
        -------
        bool
            has epsilon transition
        """
        for state, transitions in self.transitions.items():
            for trans in transitions:
                if 'E' in trans or 'ε' in trans:
                    return True

        return False

    def to_dot_format(self) -> str:
        """
        Transforms the transition dict to a string in the dot format

        Returns
        -------
        str
            the dot file
        """
        to_dot = "digraph finite_state_machine { rankdir=LR\n"

        to_dot += "\tnode [shape=doublecircle]\n"
        for exit_ in self.exits:
            to_dot += f"\t\"{exit_}\"\n"

        to_dot += '\n'

        to_dot += "\tnode [shape=circle]\n"
        for idx, entree in enumerate(self.entrees):
            to_dot += f"\tfake{str(idx)} [style=invisible]\n\tfake{str(idx)} -> \"{entree}\"\n"

        to_dot += '\n'

        for state, transitions in self._different_transitions_dict_().items():
            for k, v in transitions.items():
                if k:
                    to_dot += f"\t\"{state}\" -> \"{k}\" [label=\"{str(', '.join(v))}\"] \n"

        to_dot += "}"
        return to_dot

    def is_standard(self) -> bool:
        if len(self.entrees) != 1:
            return False

        for transitions in self.transitions.values():
            for transition in transitions:
                if self.entrees[0] in transition:
                    return False

        return True

    def get_standard(self) -> object:
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

    def is_complete(self) -> bool:
        for state in self.transitions.keys():
            for letter in self.alphabet:
                if self._state_is_empty_(state, letter):
                    return False
        return True

    def get_complete(self) -> object:
        if self.is_complete():
            return self

        complete = deepcopy(self)
        garbage = {letter: ['P'] for letter in self.alphabet}

        complete.transitions['P'] = garbage

        for state in self.transitions.keys():
            for letter in self.alphabet:
                if self._state_is_empty_(state, letter):
                    complete.transitions[state][letter] = ['P']

        return complete

    def is_determinate(self) -> bool:
        if len(self.entrees) != 1:
            return False

        for transition in self.transitions.values():
            for states in transition.values():
                if len(states) > 1:
                    return False

        return True

    def get_determinized(self, step: bool = False) -> object | list[object]:
        if self.is_e_nfa():
            return self

        if self.is_determinate():
            if self.is_complete():
                if step:
                    return [self]
                return self
            else:
                if step:
                    return [self.get_complete()]
                return self.get_complete()

        steps: list[Automata | object] = []

        determinate = Automata()
        determinate.alphabet = self.alphabet.copy()

        # unite the entrees
        new_entree = {}
        for state in self.entrees:
            for letter in self.transitions.get(state):
                if new_entree.get(letter):
                    new_entree[letter] += self._fetch_transition_(state, letter).copy()
                else:
                    new_entree[letter] = self._fetch_transition_(state, letter).copy()

                new_entree[letter] = sorted(list(set(new_entree[letter])))

        for letter, to_state in new_entree.items():
            new_entree[letter] = ['-'.join(to_state)]

        new_entree = {'-'.join(self.entrees): new_entree}

        ###

        # populate the transitions dict
        determinate.entrees = list(new_entree.keys())
        determinate.exits = []

        for state in self.entrees:
            if state in self.exits:
                determinate.exits.append('-'.join(self.entrees))

        determinate.transitions = deepcopy(new_entree)

        if step:
            steps.append(deepcopy(determinate))

        state_buffer = []
        for composing_states in new_entree.values():
            for joined_states in composing_states.values():
                state_buffer += joined_states

        state_buffer = list(set(state_buffer))

        while state_buffer:
            cur_state = state_buffer.pop()

            det_tr = determinate.transitions

            det_tr[cur_state] = {}

            if self.transitions.get(cur_state):
                letter: str
                for letter, to_state in self.transitions.get(cur_state).items():
                    det_tr[cur_state][letter] = ['-'.join(to_state)]

                if cur_state in self.exits:
                    determinate.exits.append(cur_state)

            elif not det_tr.get(cur_state):
                composing_states = list(set(cur_state.split('-')))

                for receiving_state in composing_states:
                    if receiving_state in self.exits:
                        determinate.exits.append(cur_state)

                for letter in determinate.alphabet:
                    det_tr.get(cur_state)[letter] = []

                for state in composing_states:
                    for letter, to_state in self.transitions.get(state).items():
                        temp = det_tr.get(cur_state).get(letter)
                        temp += to_state
                        det_tr.get(cur_state)[letter] = list(set(temp))

            for composing_states in det_tr.get(cur_state).values():
                joined_states = '-'.join(sorted(composing_states))
                if joined_states and (joined_states not in det_tr.keys()) and joined_states not in state_buffer:
                    state_buffer.append(joined_states)

            for letter, to_state in det_tr.get(cur_state).items():
                to_state = sorted(list(set(to_state)))
                det_tr.get(cur_state)[letter] = ['-'.join(to_state)]

            if step:
                steps.append(deepcopy(determinate))

        if step:
            return steps + [determinate.get_complete()]

        return determinate.get_complete()

    def test_word(self, word) -> bool:
        if False in [letter in self.alphabet + ['E', 'ε'] for letter in word]:
            return False

        if not self.is_determinate():
            return False

        cur_state = self.entrees[0]

        for i, letter in enumerate(word):
            next_state = self._fetch_transition_(cur_state, letter)

            cur_state = next_state

    def is_miniminized(self) -> bool:
        ...
        # TODO

    def miniminize(self) -> object:
        ...
        # TODO
