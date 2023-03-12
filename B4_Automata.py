from __future__ import annotations
import graphviz
import tabulate
import string
import os
from copy import deepcopy
import sys
import subprocess
from pathlib import Path


def open_image(path):
    """
    Opens an image in the default viewer for the operating system.

    :param path: Specify the path to the image file
    :return: Nothing, it just opens the image in your default browser
    """
    command = {'linux': 'xdg-open',
               'win32': 'explorer',
               'darwin': 'open'}[sys.platform]
    subprocess.Popen([command, Path(path)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


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
            .render(filename=Path(f'dot/{self.output}.dot'), outfile=Path(f'out/{self.output}.{self.format}'), view=False)

        open_image(Path(f'out/{self.output}.{self.format}'))

        return ''

    def __eq__(self, other):
        return self.transitions == other.transitions \
            and self.entrees == other.entrees \
            and self.exits == other.exists

    def __len__(self):
        return len(self.transitions.keys())

    def _give_state_behaviour_(self, state: str, arrows: bool = True) -> str:
        """
        Returns an indication of the initial or/and terminal behaviour of a state.

        :param self: Refer to the object itself
        :param state: str: Indicate the state to analyse
        :param arrows: bool: Indicate whether the fancy notation or with letters should be used
        :return: An indication of initial or/and terminal behaviour of the state
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
        Returns the list of states that are in the transition dict for a given state and letter.
        If there is no such state, it will return an empty list.

        :param self: Represent the instance of the class
        :param state: str: The state
        :param letter: str: Get the letter that is being used to transition from one state to another
        :return: A list of states the state is going to with the letter
        """
        return self.transitions.get(state).get(letter) or []

    def _populate_from_file_(self, path: str) -> dict[str, dict[str, list[str]]]:
        """
        Fills the transition dict with a .txt file.

        :param self: Refer to the object itself
        :param path: str: Get the path of the file
        :return: The `self.transitions` dict
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

        for i in self.entrees:
            if i not in self.transitions.keys():
                i_dont_want_to_break_things[i] = {letter: [] for letter in self.alphabet}

        for i in self.exits:
            if i not in self.transitions.keys():
                i_dont_want_to_break_things[i] = {letter: [] for letter in self.alphabet}

        for state, transitions in self.transitions.items():
            for letter, states in transitions.items():
                for i in states:
                    if i not in self.transitions.keys():
                        i_dont_want_to_break_things[i] = {letter: [] for letter in self.alphabet}

        self.transitions |= i_dont_want_to_break_things

        return self.transitions

    def _different_transitions_dict_(self) -> dict[str, dict[str, list]]:
        """
        Takes the transitions dictionary and reorganizes it.
        The original transitions dictionary has the following structure:
        {
            'state' : {
                'letter' : [ 'state', ... ],  # The list of states can be empty, but there will always be at least one letter key.
                ...                           # There may also be multiple letters for each state in this list.  This is why we need to reorganize it!

        :param self: Access the attributes of the class
        :return: A dictionary with the states as keys and a dictionary of transitions from that state as values
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
        """
        Checks if a state is empty.

        :param self: Access the attributes of the class
        :param state: str: Determine the state that is being checked
        :param letter: str: Check if the transition is empty
        :return: True if the state is empty
        """
        return not self._fetch_transition_(state, letter) \
            or self._fetch_transition_(state, letter) == ['']

    def get_info(self):
        """
        Returns a string containing the following information:
            - The number of transitions in the automaton.
            - Whether it is standard, determinate and complete.
            - The alphabet used by the automaton.

        :param self: Refer to the current object
        :return: A string containing the information of the automaton
        """
        headers = ["Standard", "Détérminé", "Complet", "transitions", "n°entrée", "n°sortie"]
        table = [[
            str(self.is_standard()),
            str(self.is_determinate()),
            str(self.is_complete()),
            str(len(self)),
            str(len(self.entrees)),
            str(len(self.exits))
        ]]

        return f"{tabulate.tabulate(table, headers, tablefmt='rounded_grid')}\n" \
               f"{tabulate.tabulate([['{' + ', '.join(self.alphabet) + '}']], ['Alphabet'], tablefmt='rounded_grid')}"

    def is_e_nfa(self) -> bool:
        """
        Checks if the NFA is an epsilon-NFA.

        :param self: Access the attributes of the class
        :return: True if the machine has an epsilon transition
        """
        for state, transitions in self.transitions.items():
            for trans in transitions:
                if 'E' in trans or 'ε' in trans:
                    return True

        return False

    def to_dot_format(self) -> str:
        """
        Converts the finite state machine into a dot format.

        :param self: Refer to the current instance of a class
        :return: A string in the dot format, which can be used to display the automaton graphically
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
        """
        Checks if the automaton is standard.

        :param self: Refer to the object itself
        :return: True if the automaton is standard, and false otherwise
        """
        if len(self.entrees) != 1:
            return False

        for transitions in self.transitions.values():
            for transition in transitions:
                if self.entrees[0] in transition:
                    return False

        return True

    def get_standard(self) -> Automata:
        """
        Transforms a non-standard automata into a standard one.

        :param self: Refer to the instance of the class
        :return: A standard automaton
        """
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

        standard.transitions['I'] = dic
        standard.entrees = ['I']

        return standard

    def is_complete(self) -> bool:
        """
        Checks if the automata is complete.

        :param self: Represent the instance of the class
        :return: A boolean value
        """
        for state in self.transitions.keys():
            for letter in self.alphabet:
                if self._state_is_empty_(state, letter):
                    return False
        return True

    def get_complete(self) -> Automata:
        """
        Takes an automata and returns a complete version of it.
            If the automata is already complete, then it will return itself.

        :param self: Refer to the current object
        :return: A complete automata
        """
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
        """
        Checks if the automaton is determinate.

        :param self: Refer to the object itself
        :return: A boolean value that indicates whether the automaton is determinate
        """
        if len(self.entrees) != 1:
            return False

        for transition in self.transitions.values():
            for states in transition.values():
                if len(states) > 1:
                    return False

        return True

    def get_determinized(self, step: bool = False) -> Automata | list[Automata]:
        """
        Takes an automata and returns a new automata that is equivalent to the original but is determinate.

        Clarifications :
        This function works by first creating a new automata with the same alphabet as the original,
        and then adding all the states from the original to this new one.
        The transitions are then added in such a way that they are deterministic
        (i.e., there can only be one transition for each letter).

        If there were multiple possible transitions for any given letter,
        these transitions will be combined into one state which contains all of them.

        :param self: Access the attributes of the class
        :param step: bool: Determine if the function should return a list of automatas or just one
        :return: A list of automata objects if step is true, otherwise it returns a single automata object
        """
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

        steps: list[Automata] = []

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

    # BONUS #

    def test_word(self, word) -> bool:
        """
        Takes a word as an argument and returns True if the word is accepted by the automaton, and False otherwise.

        :param self: Bind the method to an object
        :param word: Test the word on the automaton
        :return: True if the word is accepted by the automaton and false otherwise
        """
        if False in [letter in self.alphabet + ['E', 'ε'] for letter in word]:
            return False

        if not self.is_determinate():
            return False

        cur_state = self.entrees[0]

        for i, letter in enumerate(word):
            # print(cur_state)
            next_state = self._fetch_transition_(cur_state, letter)[0]

            cur_state = next_state

        if cur_state in self.exits:
            return True

        return False

    def get_minimized(self):
        ...

    def get_complementary(self):
        """
        Returns a new DFA that accepts the complement of the language accepted by this DFA.
        The complement is defined as all strings not in the language.


        :param self: Access the attributes of the class
        :return: The complementary of the automaton
        """
        complementary = deepcopy(self.get_determinized())

        non_exits = [state for state in complementary.transitions.keys() if state not in complementary.exits]

        complementary.exits = non_exits.copy()

        return complementary
