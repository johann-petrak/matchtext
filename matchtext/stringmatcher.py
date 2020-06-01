# -*- coding: utf-8 -*-
"""
Match strings by character: match entries character by character, optionally only at word boundaries at
the start and/or the end of an entry.
"""

from collections import namedtuple, defaultdict
from .utils import thisorthat

Match = namedtuple("Match", ["match", "start", "end", "entrydata", "matcherdata"])


class StringMatcher:

    def __init__(self, ignorefunc=None, mapfunc=None, matcherdata=None, defaultdata=None):
        """
        Create a TokenMatcher.
        :param ignorefunc: a predicate that returns True for any token that should be ignored.
        :param mapfunc: a function that returns the string to use for each token.
        :param matcherdata: data to add to all matches in the matcherdata field
        :param defaultdata: data to add to matches when the entry data is None
        """
        # TODO: need to figure out how to handle word boundaries
        # self.nodes = defaultdict(Node)
        self.ignorefunc = ignorefunc
        self.mapfunc = mapfunc
        self.defaultdata = defaultdata
        self.matcherdata = matcherdata

    def add(self, entry, data=None, append=False):
        """
        Add a gazetteer entry. If the same entry already exsits, the data is replaced with the new data.
        If all elements of the entry are ignored, nothing is done.
        :param entry: a string
        :param data: the data to add for that gazetteer entry.
        :param append: if true and data is not None, store data in a list and append any new data
        :return:
        """
        raise Exception("Not yet implemented")

    def find(self, text, all=False, skip=True, fromidx=None, toidx=None):
        """
        Find gazetteer entries in text.
        ignored.
        :param text: string to search
        :param all: return all matches, if False only return longest match
        :param skip: skip forward over longest match (do not return contained/overlapping matches)
        :param fromidx: index where to start finding in tokens
        :param toidx: index where to stop finding in tokens (this is the last index actually used)
        :return: an iterable of Match. The start/end fields of each Match are the character offsets if
        text is a string, otherwise are the token offsets.
        """
        raise Exception("Not yet implemented")

