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
from .key import T9Key
from .utils import getkey


def makedict(strIn, strOut, language="Unknown", comment=""):
    root = T9Key()
    count = 0
    f = open(strIn, "rt")
    for line in f:
        count += 1
        line = line.rstrip("\n\r")
        if not line:  # Skip empty lines
            count -= 1
            continue
        path = getkey(line)
        r = root
        for c in path:
            if r.refs[int(c) - 1] is None:
                r.refs[int(c) - 1] = T9Key()
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
