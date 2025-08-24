# ☎️  T9

This is a T9 implementation that I wrote a long, long time ago for XBMC
so chat programs could chat via the remote like I could on my Nokia
phone.

The language files are huge, but after generation they're organised so
the number of reads depends on the number of buttons pressed. It's
pretty fast, and uses virtually no RAM or CPU. This is required for
embedded systems, so enjoy! If you're not on an embedded system, you
can test it out like this:

```bash
pipx run t9
```

The reader consists of 3 classes, a database node (T9Key), a database
client (T9Dict), and an input parser (T9Input). As a user you'll only
need to bother with the latter.

## Language files wanted!

* 🇬🇧 en-GB: Downloaded from the web, derived from gnu aspell (iirc)
* 🇺🇸 en-US: From the system american-english wordlist
* 🇳🇱 nl-NL: Thanks to Breght Boschker for submitting these :)

To make your own dictionary, have a read of maket9.py.
Keep your wordlists though - the file format might change in future.

## ⚖️ license

[WTFPL](https://bitplane.net/dev/python/t9/LICENSE)

## 🔗 Links

* [🏠 home](https://bitplane.net/dev/python/t9)
  * [📖 pydoc](https://bitplane.net/dev/python/t9/pydoc)
* [😺 github](https://github.com/bitplane/t9)
* [🐍 pypi](https://pypi.org/project/t9)
