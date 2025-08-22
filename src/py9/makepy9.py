#!/usr/bin/env python
# -*- coding: utf-8 -*- 

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

import string, struct

class Py9Key:
    """Nodes for creating a browsable dictionary in memory (heavy!)
    """
    def __init__(self):
        self.refs = [None,None,None,None,None,None,None,None,None]
        self.words = []
        self.fpos = 0L

    def save(self,f):
        # recurse save children first so self.ref[x].fpos is always set
        for i in self.refs:
            if i:
                i.save(f)
        # now get position in file
        self.fpos = f.tell()

        # write flags (2 bytes)
        flags = 0
        for i in range(1,10):
            if self.refs[i-1] != None:
                flags = 2 ** i | flags
        f.write(struct.pack("!h",flags))
        
        # write positions of children (4 bytes each)
        for i in self.refs:
            if i:
                f.write(struct.pack("!i",i.fpos))
        
        # write number of words
        f.write( struct.pack("!h",len(self.words)))
        
        # write list of words
        if len(self.words) > 0:
            for l in self.words:
                f.write("%s\n" % l)

def makedict(strIn,strOut,language="Unknown",comment=""):
    root = Py9Key()
    count = 0L
    f = open(strIn,"rt")
    for line in f:
        count += 1
        l = line[:-1]
        path = str2digits(l)
        r = root
        for c in path:
            if r.refs[int(c)-1] == None:
                r.refs[int(c)-1] = Py9Key()
            r = r.refs[int(c)-1]
        # add the word to this position
        r.words.append(l)
        
    f.close()

    f = open(strOut,"wb")
    f.write("PY9DICT:" + struct.pack("!LL",0,0))
    f.writelines([language,"\x0a",comment,"\x0a"])
    root.save(f)
    f.seek(0)
    f.write("PY9DICT:" + struct.pack("!LL",count,root.fpos))
    f.close()

def str2digits(strWord):
    """
        str2digits(string) -> string of digits
        Converts a word to keypresses
    """
    def chr2digit(c):
        for d, s in (('2', 'ABCÀÂÄÅÁÆßÇ'),
                     ('3', 'DEFÐÈÉÊ'),
                     ('4', 'GHIÎÏÍ'),
                     ('5', 'JKL'),
                     ('6', 'MNOÓÖÔØÑ'),
                     ('7', 'PQRS'),
                     ('8', 'TUVÚÜ'),
                     ('9', 'WXYZÝ'),
                     ('0', ' ')):
            if c in s:
                return d
        # Symbols live here!
        return '1'


    r = ""
    for c in strWord:
        d = string.upper(c)
        r = r + chr2digit(d)
    return r


r = makedict("wordlists/en-gb.words",
             "en-gb.dict",
             "English (British)",
             "Bitplane's test language file")
