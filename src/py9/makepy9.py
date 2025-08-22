#!/usr/bin/env python
"""
Py9.py - a predictive text dictionary in the style of Nokia's T9

File Format...
  Header:
    String[7]     = "PY9DICT:"
    Unsigned Long = Number of words
    Unsigned Long = root node's start position

  Node block:
    Unsigned Long[4] =
"""

import struct


class Py9Key:
    """
    Nodes for creating a browsable dictionary in memory (heavy!)
    """

    def __init__(self):
        self.refs = [None] * 9
        self.words = []
        self.fpos = 0

    def save(self, f):
        # recurse save children first so self.ref[x].fpos is always set
        for i in self.refs:
            if i:
                i.save(f)
        # now get position in file
        self.fpos = f.tell()

        # write flags (2 bytes)
        flags = 0
        for i in range(1, 10):
            if self.refs[i - 1] is not None:
                flags = 2**i | flags
        f.write(struct.pack("!h", flags))

        # write positions of children (4 bytes each)
        for i in self.refs:
            if i:
                f.write(struct.pack("!i", i.fpos))

        # write number of words
        f.write(struct.pack("!h", len(self.words)))

        # write list of words
        for word in self.words:
            f.write(("%s\n" % word).encode("utf-8"))


def makedict(strIn, strOut, language="Unknown", comment=""):
    root = Py9Key()
    count = 0
    f = open(strIn, "rt")
    for line in f:
        count += 1
        line = line[:-1]
        path = str2digits(line)
        r = root
        for c in path:
            if r.refs[int(c) - 1] is None:
                r.refs[int(c) - 1] = Py9Key()
            r = r.refs[int(c) - 1]
        # add the word to this position
        r.words.append(line)

    f.close()

    f = open(strOut, "wb")
    f.write(b"PY9DICT:" + struct.pack("!LL", 0, 0))
    f.write(language.encode("utf-8") + b"\x0a" + comment.encode("utf-8") + b"\x0a")
    root.save(f)
    f.seek(0)
    f.write(b"PY9DICT:" + struct.pack("!LL", count, root.fpos))
    f.close()


def str2digits(word):
    """
    str2digits(string) -> string of digits
    Converts a word to keypresses
    """

    def chr2digit(c):
        for d, s in (
            ("2", "ABCÀÂÄÅÁÆßÇ"),
            ("3", "DEFÐÈÉÊ"),
            ("4", "GHIÎÏÍ"),
            ("5", "JKL"),
            ("6", "MNOÓÖÔØÑ"),
            ("7", "PQRS"),
            ("8", "TUVÚÜ"),
            ("9", "WXYZÝ"),
            ("0", " "),
        ):
            if c in s:
                return d
        # Symbols live here!
        return "1"

    r = ""
    for c in word:
        d = c.upper()
        r = r + chr2digit(d)
    return r
