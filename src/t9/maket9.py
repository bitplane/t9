"""
T9.py - a predictive text dictionary in the style of Nokia's T9

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
from .utils import getkey, read_wordlist


def makedict(strIn, strOut, language="Unknown", comment=""):
    root = T9Key()
    count = 0

    for word in read_wordlist(strIn):
        count += 1
        path = getkey(word)
        r = root
        for c in path:
            if r.refs[int(c) - 1] is None:
                r.refs[int(c) - 1] = T9Key()
            r = r.refs[int(c) - 1]
        # add the word to this position
        r.words.append(word)

    f = open(strOut, "wb")
    f.write(b"PY9DICT:" + struct.pack("!LL", 0, 0))
    f.write(language.encode("utf-8") + b"\x0a" + comment.encode("utf-8") + b"\x0a")
    root.save(f)
    f.seek(0)
    f.write(b"PY9DICT:" + struct.pack("!LL", count, root.fpos))
    f.close()
