#!/usr/bin/env python
"""T9 demo application."""

import os
import sys
from pathlib import Path

from .input import T9Input
from .utils import get_wordlists_dir, draw_keypad, getkey
from .mode import get_label
from .constants import Key


def clear_screen():
    """Clear the terminal screen."""
    os.system("cls" if os.name == "nt" else "clear")


def get_input():
    """Get a single character input, handling different platforms."""
    try:
        import termios
        import tty

        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setcbreak(fd)
            char = sys.stdin.read(1)

            # Handle escape sequences (arrow keys)
            if ord(char) == 27:  # ESC
                # Read the next two characters for arrow keys
                seq = sys.stdin.read(2)
                if seq == "[A":
                    return "UP"
                elif seq == "[B":
                    return "DOWN"
                elif seq == "[C":
                    return "RIGHT"
                elif seq == "[D":
                    return "LEFT"
                else:
                    return char  # Unknown escape sequence

        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return char
    except ImportError:
        # Windows fallback
        try:
            import msvcrt

            return msvcrt.getch().decode("utf-8", errors="ignore")
        except ImportError:
            # Final fallback - line input
            return input("> ")


def handle_input(char, input_obj):
    """Handle input character and return True if should exit."""
    if not char:
        return False

    # Handle arrow keys
    if char == "UP":
        input_obj.sendkeys(Key.UP.value)
        return False
    elif char == "DOWN":
        input_obj.sendkeys(Key.DOWN.value)
        return False
    elif char == "LEFT":
        input_obj.sendkeys(Key.LEFT.value)
        return False
    elif char == "RIGHT":
        input_obj.sendkeys(Key.RIGHT.value)
        return False

    # Handle direct T9 keys
    if char in "0123456789":
        input_obj.sendkeys(char)
        return False

    # Handle special control
    if ord(char) == 3:  # Ctrl+C
        return True
    elif char == "\r" or char == "\n":  # Enter -> Right arrow
        input_obj.sendkeys(Key.RIGHT.value)
        return False
    elif char == "\t":  # Tab -> Mode switch
        input_obj.sendkeys(Key.SELECT.value)
        return False
    elif char == "\x7f" or char == "\b":  # Backspace/DEL
        input_obj.sendkeys(Key.DOWN.value)
        return False
    else:
        # Convert text to T9 sequence
        t9_sequence = getkey(char)
        for digit in t9_sequence:
            input_obj.sendkeys(digit)
        return False


def draw_screen(input_obj):
    """Draw the complete T9 interface screen."""
    clear_screen()
    print("=== PY9 T9 Demo ===")
    print(f"Mode: {get_label(input_obj.mode)}")
    print()
    print("Text:")
    print(input_obj.gettext())
    print()
    draw_keypad()
    print()
    print("Controls: 0-9=keys, arrows=navigate, TAB=mode, Ctrl+C=quit")


def run_demo(dict_file=None):
    """Run the T9 demo application."""
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

    x = T9Input(str(dict_path), "any old chunk of text that's worth editing I suppose")

    # Initial screen draw
    draw_screen(x)

    while True:
        try:
            char = get_input()
            if handle_input(char, x):
                break
            draw_screen(x)
        except (KeyboardInterrupt, EOFError):
            print("\nExiting...")
            break

    print("\nFinal text:", x.text())
    return 0


if __name__ == "__main__":
    exit(run_demo())
