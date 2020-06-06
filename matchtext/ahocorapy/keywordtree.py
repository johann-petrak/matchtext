'''
This is a modified version of the code in the ahocorapy library by Frederik Peterson
under the MIT license (see comment below).
See https://github.com/abusix/ahocorapy.

This is the original header of the file:
====
Ahocorasick implementation entirely written in python.
Supports unicode.

Quite optimized, the code may not be as beautiful as you like,
since inlining and so on was necessary

Created on Jan 5, 2016

@author: Frederik Petersen (fp@abusix.com)
'''

# MIT License
#
# Copyright (c) 2018 Abusix, Inc.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from builtins import object


class State(object):
    __slots__ = ['identifier', 'symbol', 'data', 'transitions', 'parent',
                 'matched_keyword', 'longest_strict_suffix']

    def __init__(self, identifier, symbol=None,  parent=None, data=None):
        self.symbol = symbol
        self.identifier = identifier
        self.transitions = {}
        self.parent = parent
        self.data = data
        self.matched_keyword = None
        self.longest_strict_suffix = None

    def __str__(self):
        transitions_as_string = ','.join(
            ['{0} -> {1}'.format(key, value.identifier) for key, value in self.transitions.items()])
        return "State {0}. Transitions: {1}".format(self.identifier, transitions_as_string)


class KeywordTree(object):

    def __init__(self, case_insensitive=False):
        '''
        @param case_insensitive: If true, case will be ignored when searching.
                                 Setting this to true will have a positive
                                 impact on performance.
                                 Defaults to false.
        '''
        self._zero_state = State(0)
        self._counter = 1
        self._finalized = False
        self._case_insensitive = case_insensitive

    def add(self, keyword, data=True):
        '''
        Add a keyword to the tree.
        Can only be used before finalize() has been called.
        Keyword should be str or unicode.
        '''
        if self._finalized:
            raise ValueError('KeywordTree has been finalized.' +
                             ' No more keyword additions allowed')
        original_keyword = keyword
        if self._case_insensitive:
            keyword = keyword.lower()
        if len(keyword) <= 0:
            return
        current_state = self._zero_state
        for char in keyword:
            try:
                current_state = current_state.transitions[char]
            except KeyError:
                next_state = State(self._counter, parent=current_state,
                                   symbol=char)
                self._counter += 1
                current_state.transitions[char] = next_state
                current_state = next_state
        current_state.data = data
        current_state.matched_keyword = original_keyword

    def find_one(self, text):
        '''
        Search a text for any occurence of any added keyword.
        Returns when one keyword has been found.
        Can only be called after finalized() has been called.
        O(n) with n = len(text)
        @return: 2-Tuple with keyword and startindex in text.
                 Or None if no keyword was found in the text.
        '''
        result_gen = self.find_all(text)
        try:
            return next(result_gen)
        except StopIteration:
            return None

    def find(self, text, all=False, skip=True):
        '''
        Search a text for all occurences of the added keywords.
        Can only be called after finalized() has been called.
        @param text: the text to search.
        @param all: all matches should be found, if False, only longest one
        @param skip: if True, skip to position after last match found, otherwise try from next.
        @return:
        '''
        if not self._finalized:
            raise ValueError('KeywordTree has not been finalized.' +
                             ' No search allowed. Call finalize() first.')
        if self._case_insensitive:
            text = text.lower()
        current_state = self._zero_state
        # TODO: implement all, skip and limiting to matches after/before word boundaries
        # TODO: implement ignore and match functions
        for idx, symbol in enumerate(text):
            current_state = current_state.transitions.get(
                symbol, self._zero_state.transitions.get(symbol,
                                                         self._zero_state))
            state = current_state
            while state != self._zero_state:
                if state.data is not None:
                    keyword = state.matched_keyword
                    # Yield Match object!
                    yield keyword, idx + 1 - len(keyword), state.data
                state = state.longest_strict_suffix

    def get(self, entry, default=None):
        '''
        Lookup the entry in the tree and return the data. If not found, return the default value.
        '''
        if not self._finalized:
            raise ValueError('KeywordTree has not been finalized.' +
                             ' No search allowed. Call finalize() first.')
        if not entry:
            return default
        if len(entry) == 0:
            return default
        if self._case_insensitive:
            entry = entry.lower()
        state = self._zero_state
        symbol = entry[0]
        idx = 0
        state = state.transitions.get(
                symbol, self._zero_state.transitions.get(symbol,
                                                         self._zero_state))
        while state != self._zero_state and idx < len(entry):
            state = state.longest_strict_suffix
        if state.data is not None:
            return state.data
        else:
            return default

    def finalize(self):
        '''
        Needs to be called after all keywords have been added and
        before any searching is performed.
        '''
        if self._finalized:
            raise ValueError('KeywordTree has already been finalized.')
        self._zero_state.longest_strict_suffix = self._zero_state
        self._search_lss_for_children(self._zero_state)
        self._finalized = True

    def _search_lss_for_children(self, zero_state):
        processed = set()
        to_process = [zero_state]
        while to_process:
            state = to_process.pop()
            processed.add(state.identifier)
            for child in state.transitions.values():
                if child.identifier not in processed:
                    self._search_lss(child)
                    to_process.append(child)

    def _search_lss(self, state):
        if state.longest_strict_suffix is None:
            parent = state.parent
            traversed = parent.longest_strict_suffix
            while True:
                if state.symbol in traversed.transitions and\
                        traversed.transitions[state.symbol] != state:
                    state.longest_strict_suffix =\
                        traversed.transitions[state.symbol]
                    break
                elif traversed == self._zero_state:
                    state.longest_strict_suffix = self._zero_state
                    break
                else:
                    traversed = traversed.longest_strict_suffix
            suffix = state.longest_strict_suffix
            if suffix.longest_strict_suffix is None:
                self._search_lss(suffix)
            for symbol, next_state in suffix.transitions.items():
                if (symbol not in state.transitions and
                        suffix != self._zero_state):
                    state.transitions[symbol] = next_state

    def __str__(self):
        return "ahocorapy KeywordTree"

    def __getstate__(self):
        state_list = [None] * self._counter
        todo_list = [self._zero_state]
        while todo_list:
            state = todo_list.pop()
            transitions = {key: value.identifier for key,
                           value in state.transitions.items()}
            state_list[state.identifier] = {
                'symbol': state.symbol,
                'data': state.data,
                'parent':  state.parent.identifier if state.parent is not None else None,
                'matched_keyword': state.matched_keyword,
                'longest_strict_suffix': state.longest_strict_suffix.identifier if state.longest_strict_suffix is not None else None,
                'transitions': transitions
            }
            for child in state.transitions.values():
                if len(state_list) <= child.identifier or not state_list[child.identifier]:
                    todo_list.append(child)

        return {
            'case_insensitive': self._case_insensitive,
            'finalized': self._finalized,
            'counter': self._counter,
            'states': state_list
        }

    def __setstate__(self, state):
        self._case_insensitive = state['case_insensitive']
        self._counter = state['counter']
        self._finalized = state['finalized']
        states = [None] * len(state['states'])
        for idx, serialized_state in enumerate(state['states']):
            deserialized_state = State(idx, serialized_state['symbol'])
            deserialized_state.data = serialized_state['data']
            deserialized_state.matched_keyword = serialized_state['matched_keyword']
            states[idx] = deserialized_state
        for idx, serialized_state in enumerate(state['states']):
            deserialized_state = states[idx]
            if serialized_state['longest_strict_suffix'] is not None:
                deserialized_state.longest_strict_suffix = states[
                    serialized_state['longest_strict_suffix']]
            else:
                deserialized_state.longest_strict_suffix = None
            if serialized_state['parent'] is not None:
                deserialized_state.parent = states[serialized_state['parent']]
            else:
                deserialized_state.parent = None
            deserialized_state.transitions = {
                key: states[value] for key, value in serialized_state['transitions'].items()}
        self._zero_state = states[0]
