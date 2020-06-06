#!/usr/bin/env python
"""
Language specific case conversion. Python 3 implements the "default" case conversion strategy defined by Unicode
for the str.upper() str.title() and str.lower() methods. For example, "ß".upper() is correctly converted to
"SS" and  "ς".upper() is mapped to "Σ", while "Σ".lower() is mapped to "σ".
However, there are a few exceptions: in the Turkish and Azeri languages, the uppercase of "i" should be
"İ", not "I" and the lowercase of "I" should be "ı" not "i".

This module provides case mappers for the two languages described in the "Special Casing" Unicode
documentation: https://www.unicode.org/Public/UNIDATA/SpecialCasing.txt

NOTE: this does not implement title() as title-case conversion is more subtle anyway (e.g.
no upper case after an apostrophe inside a word except it is part of a proper name).

NOTE: another way to do this is by using the PyICU package:
```
from icu import UnicodeString, Locale
str(UnicodeString("i").toUpper(Locale("TR")))
str(UnicodeString("i").toUpper(Locale("EN")))
```
"""

CC_OGONEK = "\u0328"
CC_GRAVE = "\u0300"
CC_ACUTE = "\u0301"
CC_TILDE = "\u0303"
CC_DOT_ABOVE = "\u0307"

I_UPPER_OGONEK = "\u012E"
I_LOWER_OGONEK = "\u012F"

I_UPPER_GRAVE = "\u00CC"
I_UPPER_ACUTE = "\u00CD"
I_UPPER_TILDE = "\u0128"


class CaseMapperTrAz:

    TABLE_TOLOWER = str.maketrans("İI", "iı")
    TABLE_TOUPPER = str.maketrans("iı", "İI")

    @staticmethod
    def lower(s):
        """
        A copy of the string s converted to lowercase according to Turkish/Azeri language rules.
        :param string: string to lower case
        :return: lower-case version of the string
        """
        # if there is "dot_above" after an "I", remove it since that produces lower case dotted i
        s = s.replace("I\u0307", "I")
        return s.translate(CaseMapperTrAz.TABLE_TOLOWER).lower()

    @staticmethod
    def upper(s):
        return s.translate(CaseMapperTrAz.TABLE_TOUPPER).upper()


class CaseMapperLi:

    MAP_TOLOWER = {
        # uppercase I,J, followed by CC grave/acute/tilde/ogonek: add dot above
        "I"+CC_ACUTE: "i"+CC_DOT_ABOVE+CC_ACUTE,
        "J"+CC_ACUTE: "j"+CC_DOT_ABOVE+CC_ACUTE,
        I_UPPER_OGONEK+CC_ACUTE: I_LOWER_OGONEK+CC_DOT_ABOVE+CC_ACUTE,

        "I"+CC_GRAVE: "i"+CC_DOT_ABOVE+CC_GRAVE,
        "J"+CC_GRAVE: "j"+CC_DOT_ABOVE+CC_GRAVE,
        I_UPPER_OGONEK+CC_GRAVE: I_LOWER_OGONEK+CC_DOT_ABOVE+CC_GRAVE,

        "I"+CC_TILDE: "i"+CC_DOT_ABOVE+CC_TILDE,
        "J"+CC_TILDE: "j"+CC_DOT_ABOVE+CC_TILDE,
        I_UPPER_OGONEK+CC_TILDE: I_LOWER_OGONEK+CC_DOT_ABOVE+CC_TILDE,

        I_UPPER_ACUTE: "i"+CC_DOT_ABOVE+CC_ACUTE,
        I_UPPER_GRAVE: "i"+CC_DOT_ABOVE+CC_GRAVE,
        I_UPPER_TILDE: "i"+CC_DOT_ABOVE+CC_TILDE
    }

    @staticmethod
    def lower(s):
        s = s.replace("I", "\u0069\u0307")
        for u,l in CaseMapperLi.MAP_TOLOWER.items():
            s = s.replace(u,l)
        return s.lower()

    @staticmethod
    def upper(s):
        return s.upper()
