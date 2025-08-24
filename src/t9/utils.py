"""Utility functions for PY9 T9 text input system."""

import gzip
from pathlib import Path
from .constants import ALLKEYS


def getkey(word):
    """Convert a word to T9 keypress sequence.

    Example: "hello" -> "43556"
    """
    result = ""
    for char in word:
        digit = "1"  # Default to punctuation key
        char_upper = char.upper()

        for key_num in range(len(ALLKEYS)):
            if char_upper in ALLKEYS[key_num]:
                digit = str(key_num)
                break

        result += digit
    return result


def read_wordlist(filename):
    """Read lines from a wordlist file, handling both plain and gzipped files.

    Yields stripped non-empty lines from the file.

    Args:
        filename: Path to the wordlist file (.txt or .txt.gz)

    Yields:
        str: Each non-empty line from the file, stripped of whitespace
    """
    if str(filename).endswith(".gz"):
        with gzip.open(filename, "rt", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    yield line
    else:
        with open(filename, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    yield line


def get_wordlists_dir():
    """Get the path to the wordlists directory."""
    return Path(__file__).parent / "wordlists"


def draw_keypad():
    """Draw a T9 keypad layout for reference."""
    print("  1    2    3")
    print(" .?!  abc  def")
    print()
    print("  4    5    6")
    print(" ghi  jkl  mno")
    print()
    print("  7    8    9")
    print("pqrs  tuv  wxyz")
    print()
    print("       0")
