"""Input modes for PY9 T9 text input system."""

from enum import IntEnum


class InputMode(IntEnum):
    """Available input modes."""

    NAVIGATE = 0  # Navigate/predictive mode
    EDIT_WORD = 1  # Edit complete word mode
    EDIT_CHAR = 2  # Edit individual characters mode
    TEXT_LOWER = 3  # Lowercase text entry mode
    TEXT_UPPER = 4  # Uppercase text entry mode
    NUMERIC = 5  # Numeric entry mode


# Display labels for each mode
MODE_LABELS = {
    InputMode.NAVIGATE: "Abc...",
    InputMode.EDIT_WORD: "[Abc]",
    InputMode.EDIT_CHAR: "[a..]",
    InputMode.TEXT_LOWER: "abc",
    InputMode.TEXT_UPPER: "ABC",
    InputMode.NUMERIC: "123",
}

# Key help text for each mode
MODE_KEY_HELP = {
    InputMode.NAVIGATE: "0=Space, 1-9=Abc..., D=DEL, ULR=Navigate, S:abc",
    InputMode.EDIT_WORD: "0=Save/Space, 1-9=[Abc], D=DEL, U=Change, LR=Navigate, S:123",
    InputMode.EDIT_CHAR: "0=Save/Reset, 1-9=[a..], D=DEL, U=Change, LR=Navigate/Save, S:[A..]",
    InputMode.TEXT_LOWER: "0=Space, 1-9=abc, D=DEL, ULR=Navigate, S:Abc...",
    InputMode.TEXT_UPPER: "0-Space, 1-9=ABC, D=DEL, ULR=Navigate, S:123",
    InputMode.NUMERIC: "0-9=123, D=DEL, ULR=Navigate, S:Abc...",
}


def get_label(mode):
    """Get the display label for a mode."""
    return MODE_LABELS.get(InputMode(mode), "Unknown")


def get_help(mode):
    """Get the key help text for a mode."""
    return MODE_KEY_HELP.get(InputMode(mode), "Unknown mode")
