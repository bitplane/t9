#!/usr/bin/env python
# -*- coding: utf-8 -*-

import py9, time, os.path

try:
    from msvcrt import getche
except ImportError:
    try:
        from getch import getche
    except ImportError:
        raise ImportError("Need a source for getche, try 'apt-get install python-getch'")

if not os.path.isfile("wordlists/en-gb.words"):
    print "creating dictionary (1 time only)"
    print "loads of ram required (130mb+)"
    import makepy9

x = py9.Py9Input("en-gb.dict","any old chunk of text that's worth editing I spose")

i = ""
print x.showmode(), "---", x.showkeys()
print x.gettext()
print "? [0-9/UDLR/S/Q] >",
while i != "Q":
    time.sleep(0.05)
    i = getche()
    if ord(i) == 255:
        i = raw_input(">")
    
    if i < "~" :
        i = i.upper()
        x.sendkeys(i)
        print "\n\n\n\n\n\n\n\n\n"
        print x.showmode(), "---", x.showkeys()
        print
        print x.gettext()
        print
        print "? [0-9/UDLR/S/Q]",

# print the text
print x.text()

