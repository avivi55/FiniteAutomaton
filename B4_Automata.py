from __future__ import annotations
import graphviz
import tabulate
import string
import os
from copy import deepcopy
import sys
import subprocess
from pathlib import Path

global MAX_HEIGHT
MAX_HEIGHT = 45

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


class Automata(object):
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

    def __init__(self, source_file="", output_file="", out_type="gif"):
        """
        :param source_file: Populate the automata from a file
        :param output_file: Name the output file
        :param out_type: Set the format of the output file
        :return: Nothing
        """
        self.entrees: list[str] = []
        self.exits: list[str] = []
        self.transitions: dict[str, dict[str, list[str]]] = {}
        self.alphabet: list[str] = []

        self.source: str = source_file
        self.output: str = output_file
        self.format: str = out_type

        if source_file:
            self.__populate_from_file(self.source)

        if self.__is_e_nfa():
            self.alphabet += 'ε'

    def __cut_in_half(self, table: list[list[str]], headers: list[str]):
        """
        Takes a table and cuts it in half, then
        recombines the two halves by alternating lines. This is useful for
        displaying tables that are too wide to fit on the screen.

        :param table: list[list[str]]: Store the table that is being printed
        :param headers: list[str]: Specify the headers for the table
        :return: A string that is the table cut in half
        """
        idx = len(table) // 2

        tb1 = table[:idx]
        tb2 = table[idx:]

        if len(tb2) > len(tb1):
            tb1.append(tb2.pop(0))

        res1 = tabulate.tabulate(tb1, headers, tablefmt="simple_grid").split('\n')
        res2 = tabulate.tabulate(tb2, headers, tablefmt="simple_grid").split('\n')[::-1]
        i = 0
        while res2:
            cur = res2.pop().strip('\n')
            res1[i].strip('\n')
            res1[i] += f" {cur}"
            i += 1
        return '\n'.join(res1)

    def __str__(self) -> str:
        """
        :return: A table of the automaton
        """
        headers = ["E/S", "État"] + self.alphabet
        table = [
            [
                self.__give_state_behaviour(k),
                k,
            ] + [','.join(self.__fetch_transition(k, x)) for x in self.alphabet]
            for k in self]

        res = tabulate.tabulate(table, headers, tablefmt="simple_grid")
        
        if len(res.split('\n')) > MAX_HEIGHT:
            res = self.__cut_in_half(table, headers)

        return res

    def __repr__(self) -> str:
        """
        :return: A string
        """
        try:
            os.mkdir("out")
        except OSError:
            pass
        else:
            pass

        graphviz.Source(self.to_dot_format()) \
            .render(filename=Path(f'out/{self.output}.dot'), outfile=Path(f'out/{self.output}.{self.format}'), view=False)

        os.remove(Path(f'out/{self.output}.dot'))

        open_image(Path(f'out/{self.output}.{self.format}'))

        return ''

    def __eq__(self, other) -> bool:
        """
        :param other: Compare the current object with another
        :return: True if the two states are equal and false otherwise
        """
        return self.transitions == other.transitions \
            and self.entrees == other.entrees \
            and self.exits == other.exists

    def __len__(self) -> int:
        """
        :return: The number of states in the mdp
        """
        return len(self.__get_states())

    def __setitem__(self, key, value):
        """
        :param key: Determine the state that is being changed
        :param value: Set the value of a key in the dictionary
        :return: None
        """
        self.transitions[key] = value

    def __contains__(self, item):
        """
        :param item: Check if the item is in the list of states
        :return: True if the item is in the list of states, and false otherwise
        """
        return item in self.__get_states()

    def __getitem__(self, key):
        """
        :param key: Access the value in a dictionary
        :return: The value associated with the key
        """
        return self.transitions.get(key)

    def __iter__(self):
        """
        :return: An iterator over the states in the list
        """
        return iter(self.__get_states())

    def __give_state_behaviour(self, state: str, arrows: bool = True) -> str:
        """
        Returns an indication of the initial or/and terminal behaviour of a state.
        
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

    def __fetch_transition(self, state: str, letter: str) -> list[str]:
        """
        Returns the list of states that are in the transition dict for a given state and letter.
        If there is no such state, it will return an empty list.
        
        :param state: str: The state
        :param letter: str: Get the letter that is being used to transition from one state to another
        :return: A list of states the state is going to with the letter
        """
        if (t := self.transitions.get(state)) and (t := t.get(letter)):
            return t.copy()

        return []

    def __populate_from_file(self, path: str) -> dict[str, dict[str, list[str]]]:
        """
        Fills the transition dict with a .txt file.
        
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

                if self[state]:
                    if self.__fetch_transition(state, line[pos]):
                        self[state][line[pos]].append(line[pos + 1:])
                        self[state][line[pos]].sort()
                    else:
                        self[state][line[pos]] = [line[pos + 1:]]
                else:
                    self[state] = {line[pos]: [line[pos + 1:]]}

        # if I modify self.transitions directly it changes the size of the iter and breaks
        # it is equivalent ot a temp variable
        i_dont_want_to_break_things: dict[str, dict[str, list[str]]] = {}

        for i in self.entrees:
            if i not in self:
                i_dont_want_to_break_things[i] = {letter: [] for letter in self.alphabet}

        for i in self.exits:
            if i not in self:
                i_dont_want_to_break_things[i] = {letter: [] for letter in self.alphabet}

        for state, transitions in self.transitions.items():
            for letter, states in transitions.items():
                for i in states:
                    if i not in self:
                        i_dont_want_to_break_things[i] = {letter: [] for letter in self.alphabet}

        self.transitions |= i_dont_want_to_break_things

        return self.transitions

    def __different_transitions_dict(self) -> dict[str, dict[str, list]]:
        """
        Takes the transitions dictionary and reorganizes it.
        The original transitions dictionary has the following structure:
        {
            'state' : {
                'letter' : [ 'state', ... ],  # The list of states can be empty, but there will always be at least one letter key.
                ...                           # There may also be multiple letters for each state in this list.  This is why we need to reorganize it!
        
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

    def __is_state_empty(self, state: str, letter: str) -> bool:
        """
        Checks if a state is empty.

        
        :param state: str: Determine the state that is being checked
        :param letter: str: Check if the transition is empty
        :return: True if the state is empty
        """
        return not self.__fetch_transition(state, letter) \
            or self.__fetch_transition(state, letter) == ['']

    def __get_states(self) -> list[str]:
        """
        Returns a list of all the states in the DFA.

        :return: A list of all the states in a given fsa
        """
        return list(self.transitions.keys())

    def get_info(self):
        """
        Returns a string containing the following information:
            - The number of transitions in the automaton.
            - Whether it is standard, determinate and complete.
            - The alphabet used by the automaton.
        
        :return: A string containing the information of the automaton
        """
        headers = ["Standard", "Déterministe", "Complet", "Transitions", "n°Entrée", "n°Sortie"]
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

    def __is_e_nfa(self) -> bool:
        """
        Checks if the NFA is an epsilon-NFA.
        
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

        for state, transitions in self.__different_transitions_dict().items():
            for k, v in transitions.items():
                if k:
                    to_dot += f"\t\"{state}\" -> \"{k}\" [label=\"{str(', '.join(v))}\"] \n"

        to_dot += "}"
        return to_dot

    def is_standard(self) -> bool:
        """
        Checks if the automaton is standard.
        
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
        
        :return: A standard automaton
        """
        if self.is_standard():
            return self

        standard = deepcopy(self)
        dic = {}
        for i in [standard[x] for x in standard.entrees]:
            for k, v in i.items():
                if dic.get(k):
                    dic[k] += v
                else:
                    dic[k] = v
                dic[k] = list(set(dic[k]))

        standard['I'] = dic
        standard.entrees = ['I']

        return standard

    def is_complete(self) -> bool:
        """
        Checks if the automata is complete.
        
        :return: A boolean value
        """
        for state in self:
            for letter in self.alphabet:
                if self.__is_state_empty(state, letter):
                    return False
        return True

    def get_complete(self) -> Automata:
        """
        Takes an automata and returns a complete version of it.
            If the automata is already complete, then it will return itself.
        
        :return: A complete automata
        """
        if self.is_complete():
            return self

        complete = deepcopy(self)
        #garbage = {letter: ['P'] for letter in self.alphabet}

        complete['P'] = {letter: ['P'] for letter in self.alphabet}

        for state in self:
            for letter in self.alphabet:
                if self.__is_state_empty(state, letter):
                    complete[state][letter] = ['P']

        return complete

    def is_determinate(self) -> bool:
        """
        Checks if the automaton is determinate.
        
        :return: A boolean value that indicates whether the automaton is determinate
        """
        if len(self.entrees) != 1:
            return False

        for transition in self.transitions.values():
            for states in transition.values():
                if len(states) > 1:
                    return False

        return True

    def __get_state_e_closure(self, state: str, letter: str = '') -> list[str]:
        """
        Returns a list of states that can be reached from the given state
        by following epsilon transitions. If a letter is provided, then only those states reachable by an
        epsilon transition followed by the given letter are returned.

        :param state: str: Represent the state that we want to get the e-closure of
        :param letter: str: Should we use letter mode
        :return: A list of states that can be reached from the current state using ε-transitions
        """
        if not self.__is_e_nfa():
            return []

        transitions: list[str] = self.__fetch_transition(state, 'ε')

        letter_transitions: list[str] = []

        if letter:
            letter_transitions: list[str] = self.__fetch_transition(state, letter)

        e_closure: list[str] = letter_transitions if letter else [state]

        if transitions:
            for i in transitions:
                e_closure += self.__get_state_e_closure(i, letter=letter)

        return e_closure

    def get_simplified(self):
        """
        Takes an automata and returns a new one with the same alphabet, entrees,
        exits and transitions but with states renamed to be more readable.

        :return: A simplified version of the automata
        """
        simplified = Automata()
        simplified.alphabet = self.alphabet.copy()
        new_states = {}

        for i, v in enumerate(self):
            new_states[v] = v if v in string.ascii_letters else str(i)

        simplified.exits = [new_states.get(state) for state in self.exits]
        simplified.entrees = [new_states.get(state) for state in self.entrees]

        for state, new_state in new_states.items():
            simplified[new_state] = {}
            for letter in self.alphabet:
                simplified[new_state][letter] = []
                for i in self[state][letter]:
                    simplified[new_state][letter] += [new_states.get(i)] or []

        return simplified

    def __get_e_determinized(self, step: bool = False):
        """
        Converts an E-NFA into a DFA.

        :return: The determinized version of the automata
        """
        if not self.__is_e_nfa():
            raise TypeError("Not an E-NFA!!")

        determinate = Automata()
        determinate.alphabet = self.alphabet.copy()[:-1]  # we remove the epsilon
        # we assume that the automata only has one accepting state

        determinate.entrees = self.entrees.copy()

        entree = determinate.entrees[0]

        determinate[entree] = {letter: ['-'.join(self.__get_state_e_closure(entree, letter=letter))] for letter in determinate.alphabet}

        if self.exits[0] in self.__get_state_e_closure(entree):
            determinate.exits.append(entree)

        buffer: list[str] = []

        for letter in determinate.alphabet:
            buffer += determinate.__fetch_transition(entree, letter) or []

        while buffer:
            cur_state = buffer.pop().strip()

            if not cur_state or cur_state in determinate:
                continue

            determinate[cur_state] = {}

            for letter in determinate.alphabet:
                if cur_state in self:
                    determinate[cur_state][letter] = ['-'.join(self.__get_state_e_closure(cur_state, letter=letter))]

                    if self.exits[0] in self.__get_state_e_closure(cur_state):
                        determinate.exits.append(cur_state)
                else:
                    determinate[cur_state][letter] = []
                    for state in cur_state.strip().split('-'):
                        if cloture := self.__get_state_e_closure(state, letter=letter):
                            determinate[cur_state][letter] += ['-'.join(cloture)]

                        if self.exits[0] in self.__get_state_e_closure(state):
                            determinate.exits.append(cur_state)

                determinate[cur_state][letter] = ['-'.join(determinate[cur_state][letter])]

            for v in determinate[cur_state].values():
                buffer += v if v != [''] else []

        return determinate.get_complete()

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


        :param step: bool: Determine if the function should return a list of automatas or just one
        :return: A list of automata objects if step is true, otherwise it returns a single automata object
        """
        if self.__is_e_nfa():
            return self.__get_e_determinized(step=step)

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
            for letter in self[state]:
                if n_e := new_entree.get(letter):
                    n_e += self.__fetch_transition(state, letter).copy()
                else:
                    new_entree[letter] = self.__fetch_transition(state, letter).copy()

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

            if trans := self[cur_state]:
                for letter, to_state in trans.items():
                    det_tr[cur_state][letter] = ['-'.join(to_state)]

                if cur_state in self.exits:
                    determinate.exits.append(cur_state)

            elif not det_tr.get(cur_state):
                composing_states = list(set(cur_state.split('-')))

                for receiving_state in composing_states:
                    if receiving_state in self.exits:
                        determinate.exits.append(cur_state)

                for letter in determinate.alphabet:
                    det_tr[cur_state][letter] = []

                for state in composing_states:
                    for letter, to_state in self[state].items():
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

        
        :param word: Test the word on the automaton
        :return: True if the word is accepted by the automaton and false otherwise
        """
        if False in [letter in self.alphabet + ['E', 'ε'] for letter in word]:
            return False

        if not self.is_determinate():
            return False

        cur_state = self.entrees[0]

        for i, letter in enumerate(word):
            next_state = self.__fetch_transition(cur_state, letter)[0]

            cur_state = next_state

        if cur_state in self.exits:
            return True

        return False

    def get_minimized(self):
        """
        Minimizes the given automaton using the Moore's algorithm.
        
        :return: A new minimized automata object
        """
        # Step 1: Convert the automaton to a determinate one

        if self.__is_e_nfa():
            return self

        minimized = Automata()
        minimized['0'] = {letter: ['0'] for letter in self.alphabet}
        minimized.alphabet = self.alphabet.copy()
        minimized.entrees = ['0']

        if not len(self.exits):
            return minimized
        elif len(self.entrees) == len(self):
            minimized.exits = ['0']
            return minimized

        del minimized

        if not self.is_determinate():
            determinized = deepcopy((self.get_determinized()))
        else:
            determinized = deepcopy(self)

        # Step 2: Create initial partition
        accepting_states = determinized.exits.copy()
        non_accepting_states = [state for state in determinized.transitions.keys() if state not in self.exits]
        partition = [accepting_states, non_accepting_states]

        # Step 3: Initialize queue
        queue = partition.copy()

        # Step 4: Split states until no more splits possible
        while queue:
            group = queue.pop(0)
            for letter in determinized.alphabet:
                transitions = {}
                for state in group:
                    for to_state in determinized.__fetch_transition(state, letter):
                        for i, part in enumerate(partition):
                            if to_state in part:
                                transitions.setdefault(i, []).append(state)
                                break

                if len(transitions) <= 1:
                    continue

                # Split the group
                new_partition = []
                for i in sorted(transitions):
                    states = transitions[i]
                    if len(states) == 1:
                        new_partition.append(states)
                    else:
                        new_partition.extend([states[j:j + 1] for j in range(0, len(states), 1)])
                try:
                    partition.remove(group)
                except ValueError:
                    for i in group:
                        if [i] in partition:
                            partition.remove([i])

                partition.extend(new_partition)
                queue.extend(new_partition)

        minimized = Automata()
        minimized.alphabet = determinized.alphabet.copy()

        partition = ['_'.join(states) for states in partition]

        for i in partition:
            ...

        minimized.transitions = {states: {letter: [] for letter in self.alphabet} for states in partition}

        for state in partition:
            split_states = state.split('_')

            for i in split_states:
                if i in determinized.exits:
                    minimized.exits.append(state)
                if i in determinized.entrees:
                    minimized.entrees.append(state)
                minimized[state] |= determinized[i]

        minimized.exits = list(set(minimized.exits))
        minimized.entrees = list(set(minimized.entrees))

        # print(determinized.transitions)
        # print(minimized.transitions)

        return minimized

    def get_complementary(self):
        """
        Returns a new DFA that accepts the complement of the language accepted by this DFA.
        The complement is defined as all strings not in the language.
        
        :return: The complementary of the automaton
        """
        complementary = deepcopy(self.get_determinized())

        non_exits = [state for state in complementary.transitions.keys() if state not in complementary.exits]

        complementary.exits = non_exits.copy()

        return complementary
