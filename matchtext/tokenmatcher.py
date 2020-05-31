# -*- coding: utf-8 -*-
"""
Match tokens or token sequences: here, the minimal element we match is a "token" and each entry
in the gazetteer is seen as a sequence of one or more tokens and the text where we match is also seen as a sequence
of one or more tokens.

For both the text and a gazetteer entry, if we have a string, that string is first converted to
a list of tokens. If we do not have a string, it should be an iterable of string or an iterable where
the string corresponding to each element can be retrieved via some getter function.
"""

import logging
from collections import namedtuple, defaultdict

Match = namedtuple("Match", ["tokens", "start", "end", "data"])


class Node(object):
    """
    Represent an entry in the hash map of entry first tokens.
    If isMatch is True, that token is already a match and data contains the entry data.
    The continuations attribute contains None or a list of multi token matches that
    start with the first token and the entry data if we have a match (all tokens match).
    """
    __slots__ = ("isMatch", "data", "continuations")

    def __init__(self, isMatch=None, data=None, continuations=None):
        self.isMatch = isMatch
        self.data = data
        self.continuations = continuations

    def __repr__(self):
        return f"Node(isMatch={self.isMatch},data={self.data},continuations={self.continuations})"


class Continuation(object):
    __slots__ = ("tokens", "data")

    def __init__(self, tokens=[], data=None):
        self.tokens = tokens
        self.data = data

    def __repr__(self):
        return f"Continuation(tokens={self.tokens},data={self.data})"


class TokenMatcher:

    def __init__(self, ignorefunc=None, mapfunc=None):
        """
        Create a TokenMatcher.
        :param ignorefunc: a predicate that returns True for any token that should be ignored.
        :param mapfunc: a function that returns the string to use for each token.
        """
        # for each gazetteer entry, the key is the mapped string and the value is a list of
        # matches or continuations:
        # a match is a _Match named tuple which contains only the entry data (if any)
        # a continuation is a _Continuation tuple which contains the remaining mapped strings to match and the entry data
        self._dict = defaultdict(Node)
        self.ignorefunc = ignorefunc
        self.mapfunc = mapfunc

    def add(self, entry, data=None):
        """
        Add a gazetteer entry. If the same entry already exsits, the data is replaced with the new data.
        If all elements of the entry are ignored, nothing is done.
        :param entry: a string or iterable of string.
        :param data: the data to add for that gazetteer entry.
        :return:
        """
        if isinstance(entry, str):
            entry = [entry]
        cont = None
        i = 0
        for token in entry:
            if self.mapfunc is not None:
                token = self.mapfunc(token)
            if self.ignorefunc is not None and self.ignorefunc(token):
                continue
            if i == 0:
                node = self._dict[token]
            else:
                if node.continuations is None:
                    conttoks = [token]
                    node.continuations = [Continuation(tokens=conttoks, data=data)]
                else:
                    # if there are already continuations, just add a new one if we have i==1
                    if i == 1:
                        conttoks = [token]
                        node.continuations.append(Continuation(tokens=conttoks, data=data))
                    else:
                        conttoks.append(token)
            i += 1
        if i == 1:
            node.data = data
            node.isMatch = True

    def find(self, tokens, all=True):
        """
        Find gazetteer entries in text. Text is either a string or an iterable of strings or
        an iterable of elements where a string can be retrieved using the getter.
        :param text: iterable of tokens (string or something where getter retrieves a string)
        :param all: return all matches, if False only return all longest matches
        :return: an iterable of Match. The start/end fields of each Match are the character offsets if
        text is a string, otherwise are the token offsets.
        """
        matches = []
        l = len(tokens)
        for i, token in enumerate(tokens):
            if self.mapfunc:
                token = self.mapfunc(token)
            if token in self._dict:  # only possible if the token is not ignored!
                node = self._dict[token]
                thismatches = []
                if node.isMatch:
                    thismatches.append(Match([token], i, i+1, node.data))
                if node.continuations:

                    # for each continuation, check if we can match it and get the match
                    # TODO: add loop and indent below!!
                    # TODO: for testing we just get the first continuation
                    # TODO: matching tokens have to get reset for each continuation
                    cont = node.continuations[0]
                    thistokens = [token]

                    # try to match all tokens in continuations with the next tokens
                    j = i+1   # index into text tokens
                    ctoks = cont.tokens
                    k = 0  # index into continuation tokens
                    while j < l and k < len(ctoks):
                        tok = tokens[j]
                        if self.mapfunc:
                            tok = self.mapfunc(tok)
                        if self.ignorefunc and self.ignorefunc(tok):
                            j += 1
                            continue
                        if tok == ctoks[k]:
                            j += 1
                            k += 1
                            thistokens.append(tok)
                            continue
                        else:
                            break
                    # now if k == len(ctoks) we must have found a match of length k+1
                    if k == len(ctoks):
                        thismatches.append(Match(thistokens, i, i + k + 1, cont.data))
                for m in thismatches:
                    matches.append(m)
        return matches



    def str_debug(self):
        return self._dict


if __name__ == "__main__":
    # quick tests
    entries = ["Some", "word", "to", "add", ["some", "word"]]
    tm = TokenMatcher(mapfunc=str.lower)
    print("Empty: ", tm.str_debug())
    for i, e in enumerate(entries):
        tm.add(e, data=i)
        print(f"After {i}: ", tm.str_debug())

    t1 = ["This", "contains", "Some", "text"]
    print("M1: ", tm.find(t1))
    t2 = ["this", "contains", "some", "word", "of", "text", "to", "add"]
    print("M2: ", tm.find(t2))