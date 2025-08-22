#!/usr/bin/env python
"""T9 demo application."""

import time
from pathlib import Path

from .input import Py9Input
from .utils import get_wordlists_dir


def run_demo(dict_file=None):
    """Run the T9 demo application."""
    try:
        from msvcrt import getche
    except ImportError:
        try:
            from getch import getche
        except ImportError:
            print("T9 Demo requires getch for keyboard input.")
            print("On Ubuntu/Debian: apt-get install python3-getch")
            print("Or install via pip: pip install getch")
            return 1

    # Use provided dictionary file or default
    if dict_file:
        dict_path = Path(dict_file)
    else:
        dict_path = get_wordlists_dir() / "en-gb.dict"

    if not dict_path.exists():
        print(f"Dictionary file not found: {dict_path}")
        wordlists_dir = get_wordlists_dir()
        print(f"Generate one with: py9 generate {wordlists_dir}/en-gb.words -o {wordlists_dir}/en-gb.dict")
        return 1

    x = Py9Input(str(dict_path), "any old chunk of text that's worth editing I suppose")

    i = ""
    print("=== PY9 T9 Demo ===")
    print(x.showmode(), "---", x.showkeys())
    print(x.gettext())
    print("? [0-9/UDLR/S/Q] >")

    while i != "Q":
        time.sleep(0.05)
        try:
            i = getche()
        except Exception:
            i = input(">")

        if ord(i) == 255:
            i = input(">")

        if i < "~":
            i = i.upper()
            x.sendkeys(i)
            print("\n\n\n\n\n\n\n\n\n")
            print(x.showmode(), "---", x.showkeys())
            print()
            print(x.gettext())
            print()
            print("? [0-9/UDLR/S/Q]")

    # print the final text
    print("Final text:", x.text())
    return 0


if __name__ == "__main__":
    exit(run_demo())
