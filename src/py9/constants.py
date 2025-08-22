"""Constants for PY9 T9 text input system."""

from enum import IntEnum

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


class Key(IntEnum):
    """T9 input keys."""

    KEY_0 = 0
    KEY_1 = 1
    KEY_2 = 2
    KEY_3 = 3
    KEY_4 = 4
    KEY_5 = 5
    KEY_6 = 6
    KEY_7 = 7
    KEY_8 = 8
    KEY_9 = 9
    MODE = 10  # Mode switch (was S)
    UP = 11  # Up/Previous word (was U)
    DOWN = 12  # Down/Delete/Backspace (was D)
    LEFT = 13  # Left/Back (was L)
    RIGHT = 14  # Right/Forward (was R)
