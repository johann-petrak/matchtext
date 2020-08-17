# -*- coding: utf-8 -*-
"""
Match tokens or token sequences: here, the minimal element we match is a "token" and each entry
in the gazetteer is seen as a sequence of one or more tokens and the text where we match is also seen as a sequence
of one or more tokens.

For both the text and a mather entry, if we have a string, that string is first converted to
a list of tokens. If we do not have a string, it should be an iterable of string or an iterable where
the string corresponding to each element can be retrieved via some getter function.

For each sequence, there can be only one entry/match, but the add method can be made to store a list of
data and append on each add for the same sequence instead of overwriting existing data with the "append=True"
parameter.
"""

import sys
from collections import defaultdict
from matchtext.utils import thisorthat
from dataclasses import dataclass
from matchtext.runutils import ensurelogger, set_logger


@dataclass(unsafe_hash=True, order=True)
class Match:
    __slots__ = ("start", "end", "match", "entrydata", "matcherdata")
    start: int
    end: int
    match: list
    entrydata: object
    matcherdata: object


class Node(object):
    """
    Represent an entry in the hash map of entry first tokens.
    If is_match is True, that token is already a match and data contains the entry data.
    The continuations attribute contains None or a list of multi token matches that
    start with the first token and the entry data if we have a match (all tokens match).
    """
    __slots__ = ("is_match", "data", "nodes")

    def __init__(self, is_match=None, data=None, nodes=None):
        """

        :param is_match: this node is a match
        :param data: data associated with the match
        :param nodes:
        """
        self.is_match = is_match
        self.data = data
        self.nodes = nodes

    @staticmethod
    def dict_repr(nodes):
        if nodes is not None:
            return str([(t, n) for t, n in nodes.items()])

    def __repr__(self):
        nodes = Node.dict_repr(self.nodes)
        return f"Node(is_match={self.is_match},data={self.data},nodes={nodes})"


class TokenMatcher:

    def __init__(self, ignorefunc=None, mapfunc=None, matcherdata=None, defaultdata=None):
        """
        Create a TokenMatcher.
        :param ignorefunc: a predicate that returns True for any token that should be ignored.
        :param mapfunc: a function that returns the string to use for each token.
        :param matcherdata: data to add to all matches in the matcherdata field
        :param defaultdata: data to add to matches when the entry data is None
        """
        self.nodes = defaultdict(Node)
        self.ignorefunc = ignorefunc
        self.mapfunc = mapfunc
        self.defaultdata = defaultdata
        self.matcherdata = matcherdata

    def add(self, entry, data=None, append=False, listdata=None):
        """
        Add a gazetteer entry. If the same entry already exsists, the data is replaced with the new data.
        If all elements of the entry are ignored, nothing is done.

        :param entry: a string or iterable of string.
        :param data: the data to add for that gazetteer entry.
        :param append: if true and data is not None, store data in a list and append any new data
        :param listdata: list data for the gazetteer entry
        :return:
        """
        if isinstance(entry, str):
            entry = [entry]
        node = None
        i = 0
        for token in entry:
            if self.mapfunc is not None:
                token = self.mapfunc(token)
            if self.ignorefunc is not None and self.ignorefunc(token):
                continue
            if i == 0:
                node = self.nodes[token]
            else:
                if node.nodes is None:
                    node.nodes = defaultdict(Node)
                    tmpnode = Node()
                    node.nodes[token] = tmpnode
                    node = tmpnode
                else:
                    node = node.nodes[token]
            i += 1
        if append and data is not None:
            if node.data:
                node.data.append(data)
            else:
                node.data = [data]
                node.is_match = True
        else:
            node.data = data
            node.is_match = True

    def find(self, tokens, all=False, skip=True, fromidx=None, toidx=None, getter=None, matchmaker=None):
        """
        Find gazetteer entries in text. Text is either a string or an iterable of strings or
        an iterable of elements where a string can be retrieved using the getter.
        Note: if fromidx or toidx are bigger than the length of the tokens allows, this is silently
        ignored.
        :param tokens: iterable of tokens (string or something where getter retrieves a string)
        :param all: return all matches, if False only return longest match
        :param skip: skip forward over longest match (do not return contained/overlapping matches)
        :param fromidx: index where to start finding in tokens
        :param toidx: index where to stop finding in tokens (this is the last index actually used)
        :param getter: get the string from a token object, if None, assumes each token already is a string
        :return: an iterable of Match. The start/end fields of each Match are the character offsets if
        text is a string, otherwise are the token offsets.
        """
        logger = ensurelogger()
        logger.debug("CALL")
        matches = []
        l = len(tokens)
        if fromidx is None:
            fromidx = 0
        if toidx is None:
            toidx = l-1
        if fromidx >= l:
            return matches
        if toidx >= l:
            toidx = l-1
        if fromidx > toidx:
            return matches
        i = fromidx
        logger.debug(f"From index {i} to index {toidx} for {tokens}")
        while i <= toidx:
            token_obj = tokens[i]
            if getter:
                token = getter(token_obj)
            else:
                token = token_obj
            logger.debug(f"Check token {i}={token}")
            if self.mapfunc:
                token = self.mapfunc(token)
            if token in self.nodes:  # only possible if the token was not ignored!
                longest = 0
                node = self.nodes[token]
                logger.debug(f"Got a first token match for {token}")
                thismatches = []
                thistokens = [token]
                if node.is_match:
                    logger.debug(f"First token match is also entry match")
                    longest = 1
                    if matchmaker:
                        match = matchmaker(i, i+1, thistokens.copy(), thisorthat(node.data, self.defaultdata), self.matcherdata)
                    else:
                        match = Match(i, i+1, thistokens.copy(), thisorthat(node.data, self.defaultdata), self.matcherdata)
                    thismatches.append(match)
                j = i+1  # index into text tokens
                nignored = 0
                while j <= toidx:
                    logger.debug(f"j={j}")
                    if node.nodes:
                        tok = tokens[j]
                        if self.mapfunc:
                            tok = self.mapfunc(tok)
                        if self.ignorefunc and self.ignorefunc(tok):
                            j += 1
                            nignored += 1
                            continue
                        if tok in node.nodes:
                            logger.debug(f"Found token {tok}")
                            node = node.nodes[tok]
                            thistokens.append(tok)
                            if node.is_match:
                                logger.debug(f"Also is entry match")
                                if matchmaker:
                                    match = matchmaker(i, i + len(thistokens)+nignored,
                                          thistokens.copy(),
                                          thisorthat(node.data, self.defaultdata), self.matcherdata)
                                else:
                                    match = Match(i, i + len(thistokens)+nignored,
                                          thistokens.copy(),
                                          thisorthat(node.data, self.defaultdata), self.matcherdata)
                                # TODO: should LONGEST get calculated including ignored tokens or not?
                                if all:
                                    thismatches.append(match)
                                    if len(thistokens) > longest:
                                        longest = len(thistokens)
                                else:
                                    if len(thistokens) > longest:
                                        thismatches = [match]
                                        longest = len(thistokens)
                            j += 1
                            continue
                        else:
                            logger.debug(f"Breaking: {tok} does not match, j={j}")
                            break
                    else:
                        logger.debug("Breaking: no nodes")
                        break
                logger.debug(f"Going through thismatches: {thismatches}")
                for m in thismatches:
                    matches.append(m)
                if thismatches and skip:
                    i += longest - 1  # we will increment by 1 right after!
            i += 1
            logger.debug(f"Incremented i to {i}")
        return matches

    def replace(self,  tokens, fromidx=None, toidx=None, getter=None, replacer=None, matchmaker=None):
        """
        Replace any longest sequence of tokens we find. By default the data found for the match is
        used as is.

        The getter function is used for finding matching to access the string from an individuak token object.

        The replacer parameter can be used to specify a function that takes the
        match and returns a list of replacement tokens. If the replacer is a list, that list is always used
        as a replacement. If the replacer is a string, it is used as a single token string that is always used.

        :param tokens: the sequence of tokens where to find and replace matches. The parameter is left unchanged.
        :param fromidx:
        :param toidx:
        :param getter: a function that takes a token from tokens and returns the corresponding string
        :param replacer: a function that takes a match and returns a list of tokens to replace the matched tokens with
        :param matchmaker: a function to create a match object, passed on to the finder.
        :return: the tokens with all replacements carried out
        """
        tokens = tokens.copy()
        matches = self.find(tokens, fromidx=fromidx, toidx=toidx, all=False, skip=True, getter=getter, matchmaker=matchmaker)
        # to make it easier to replace slices in the tokens, replace from the end
        matches = sorted(matches, key=lambda x: x.start, reverse=True)
        for match in matches:
            if replacer:
                rep = replacer(match)
            else:
                rep = [match.entrydata]
            tokens[match.start:match.end] = rep
        return tokens
