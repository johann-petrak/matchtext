# python-matchtext
Library for fast text matching and replacing.

This library implements two fast approaches for matching keywords/gazetteer entries:
* TokenMatcher: keywords/gazetteer entries are sequences of tokens, optionally associated with some data and 
  the matcher tries to match any of those in a given sequence of tokens. 
* StringMatcher: keywords/gazetter entries are strings, optionally associated with some data and 
  the matcher tries to match any of those in a given string, optionally only at non-word boundaries.

The matchers are implemented to be fast and memory-efficient: TokenMatcher is a hash tree, StringMatcher uses an efficient 
character trie implementation underneath. Both matchers implement additional features often required in NLP:
* mapfunc: tokens/characters can be mapped to some canonical form that is used for matching
* ignorefunc: some tokens/characters can be entirely ignored for matching
* match all/longest: only match the longest entry versus all entries
* skip/noskip: if any match is found, continue matching after the longest match versus at the next position


## Tests

To run the tests manually and get any print output on the console:
```
PYTHONPATH=`pwd` pytest -s 
```
