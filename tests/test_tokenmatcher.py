# -*- coding: utf-8 -*-

from matchtext.tokenmatcher import TokenMatcher

ENTRIES =  ["Some", "word", "to", "add", ["some", "word"], ["some", "word"]]


def test_tm1():
    tm = TokenMatcher()
    for i, e in enumerate(ENTRIES):
        tm.add(e, data=i, append=False)

    t1 = ["This", "contains", "Some", "text"]
    ms1 = tm.find(t1, all=False, skip=True)
    assert len(ms1) == 1
    m1 = ms1[0]
    assert m1.entrydata == 0
    assert m1.start == 2
    assert m1.end == 3
    assert m1.matcherdata is None


def test_m2():
    tm = TokenMatcher(mapfunc=str.lower, matcherdata="x")
    for i, e in enumerate(ENTRIES):
        tm.add(e, data=i, append=True)
    t1 = ["this", "contains", "some", "word", "of", "text", "to", "add"]
    ms = tm.find(t1, all=True, skip=False)
    # print("Matches:", ms)
    assert len(ms) == 5
    m = ms[0]
    assert m.entrydata == [0]
    assert m.start == 2
    assert m.end == 3
    assert m.matcherdata == "x"
    m = ms[1]
    assert m.match == ["some", "word"]
    assert m.entrydata == [4, 5]
    assert m.start == 2
    assert m.end == 4
    assert m.matcherdata == "x"
    m = ms[2]
    assert m.match == ["word"]
    assert m.entrydata == [1]
    assert m.start == 3
    assert m.end == 4
    assert m.matcherdata == "x"

