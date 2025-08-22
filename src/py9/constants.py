"""Constants for PY9 T9 text input system."""

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
