"""Utility functions for PY9 T9 text input system."""

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


def str2digits(word):
    """Convert a word to T9 keypress sequence (alias for getkey)."""
    return getkey(word)
