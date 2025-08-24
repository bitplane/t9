"""Constants for PY9 T9 text input system."""

from enum import Enum

# Key to letter mapping for T9 input
# Index 0 = key 0, index 1 = key 1, etc.
# Key 1 is for punctuation and symbols
ALLKEYS = [
    " ",  # Key 0: space
    ".,!?\"'():;=+-/@|£$%*<>[]\\^_{}~#",  # Key 1: punctuation/symbols
    "ABCÀÂÄÅÁÆßÇ",  # Key 2: ABC + accented chars
    "DEFÐÈÉÊ",  # Key 3: DEF + accented chars
    "GHIÎÏÍ",  # Key 4: GHI + accented chars
    "JKL",  # Key 5: JKL
    "MNOÓÖÔØÑ",  # Key 6: MNO + accented chars
    "PQRS",  # Key 7: PQRS
    "TUVÚÜ",  # Key 8: TUV + accented chars
    "WXYZÝ",  # Key 9: WXYZ + accented chars
]


class Key(Enum):
    """T9 input keys - string values match the actual key characters used."""

    NUM_0 = "0"
    NUM_1 = "1"
    NUM_2 = "2"
    NUM_3 = "3"
    NUM_4 = "4"
    NUM_5 = "5"
    NUM_6 = "6"
    NUM_7 = "7"
    NUM_8 = "8"
    NUM_9 = "9"
    SELECT = "S"  # Mode switch/Select
    UP = "U"  # Up/Previous word
    DOWN = "D"  # Down/Delete/Backspace
    LEFT = "L"  # Left/Back
    RIGHT = "R"  # Right/Forward
