"""Input parser class for PY9 T9 text input system."""

import time
import logging

from .constants import ALLKEYS, Key
from .dict import T9Dict
from .mode import InputMode
from .utils import getkey

logger = logging.getLogger(__name__)


class T9Input:
    """T9 input parser that handles keypresses and text manipulation.

    Send keypresses with sendkeys(), retrieve display text with gettext(),
    get raw text with text().
    """

    def __init__(self, dict_file, defaulttxt="", defaultmode=0, keydelay=0.5, numeric=False):
        """Create a new input parser.

        dict_file: dictionary file name
        defaulttxt: text to start with
        defaultmode: mode to start in (NAVIGATE=Predictive, TEXT_LOWER, TEXT_UPPER, NUMERIC)
        keydelay: key timeout in TXT mode
        numeric: NOT IMPLEMENTED YET
        """
        self.dict = T9Dict(dict_file)  # dict for lookups
        self.mode = defaultmode  # InputMode: NAVIGATE, EDIT_WORD, EDIT_CHAR, TEXT_LOWER, TEXT_UPPER, NUMERIC
        self.pos = 0  # cursor position (edit chars)
        self.keys = ""  # keys typed (edit word)
        self.word = ""  # word displayed (edit word/chars)
        self.words = []  # possible words (edit word)
        self.textbefore = defaulttxt  # before the cursor
        self.textafter = ""  # after the cursor
        self.lastkeypress = ""  # last key pressed (txt input)
        self.lastkeytime = time.perf_counter()  # time from last key (txt input)
        self.keydelay = keydelay  # time to change char (txt input)
        self.numeric = numeric  # True if this is numbers only

    def gettext(self):
        """Get current text including cursor for display.
        For raw text use .text()
        """
        if self.mode == InputMode.NAVIGATE:
            return self.textbefore + "|" + self.textafter
        elif self.mode == InputMode.EDIT_WORD:
            return self.textbefore + "[" + self.word + "]" + self.textafter
        elif self.mode == InputMode.EDIT_CHAR:
            return self.textbefore + '"' + self.posword() + '"?' + self.textafter
        elif self.mode == InputMode.TEXT_LOWER:
            return self.textbefore + "()" + self.textafter
        elif self.mode == InputMode.TEXT_UPPER:
            return self.textbefore + "[]" + self.textafter
        elif self.mode == InputMode.NUMERIC:
            return self.textbefore + "#" + self.textafter

    def text(self):
        """Get text buffer without cursor."""
        if self.mode == InputMode.EDIT_CHAR or self.mode == InputMode.EDIT_WORD:
            return self.textbefore + self.word + self.textafter
        else:
            return self.textbefore + self.textafter

    def posword(self):
        """Get word with position marker."""
        return "%s|%c|%s" % (self.word[0 : self.pos], self.word[self.pos], self.word[self.pos + 1 : len(self.word)])

    def setword(self):
        """Change current word to first valid match."""
        if len(self.keys) == 0:
            self.mode = InputMode.NAVIGATE
            return

        self.pos = 0
        self.words = self.dict.getwords(self.keys)
        if len(self.words) == 0:
            self.word = "." * len(self.keys)
        else:
            wl = len(self.words[0])
            kl = len(self.keys)
            if wl == kl:
                # same length
                self.word = self.words[0]
                self.mode = InputMode.EDIT_WORD
            elif wl > kl:
                # long
                self.word = self.words[0][0:kl]
                self.mode = InputMode.EDIT_CHAR
            else:
                # short
                self.word = self.words[0] + "." * (kl - wl)
                self.mode = InputMode.EDIT_CHAR

    def nextword(self):
        """In edit mode 1, move to next word if possible."""
        if self.word in self.words:
            # enter manual edit if we run out of words
            i = self.words.index(self.word)
            if i == len(self.words) - 1:
                self.mode = InputMode.EDIT_CHAR
                self.pos = 0
            else:
                self.mode = InputMode.EDIT_WORD
                self.word = self.words[i + 1]
        else:
            # the word was not found
            self.setword()

    def nextchar(self):
        """In edit mode 2, select next letter in the group."""
        c = self.word[self.pos]
        lc = c == c.lower()
        c = c.upper()
        key = int(self.keys[self.pos])
        if c not in ALLKEYS[key]:
            c = ALLKEYS[key][0]
        else:
            i = ALLKEYS[key].find(c) + 1
            if i < len(ALLKEYS[key]):
                c = ALLKEYS[key][i]
            else:
                c = ALLKEYS[key][0]
        if lc:
            c = c.lower()
        self.word = "%s%c%s" % (self.word[0 : self.pos], c, self.word[self.pos + 1 : len(self.word)])

    def addkeypress(self, key):
        """Add a keypress to current input."""
        if key == Key.NUM_1.value and self.keys[0] != Key.NUM_1.value:
            if self.keys[-1] == Key.NUM_1.value:
                # this is punctuation only - skip the word (no save)
                self.textbefore += self.word[0:-1]
                self.keys = self.keys[-1]
                self.keys += key
                self.setword()
            else:
                self.keys += key
                self.words = self.dict.getwords(self.keys)
                self.word += "'"
        else:
            self.keys += key
            # reset text
            self.setword()

    def sendkeys(self, keys):
        """Send action keys (0-9, U/D/L/R/S).

        UDLRS = UP, DOWN, LEFT, RIGHT, SELECT

        Navigation mode:
            0-9: start new word
            ULR: navigate cursor
            D: backspace
            S: switch to text mode

        Edit mode (1+2):
            0-9: append keystroke
            Complete word (mode 1):
                LR: accept word
                U: change word
                D: backspace
                S: character edit mode
            Incomplete word (mode 2):
                L: back letter
                R: confirm letter
                U: change letter
                D: delete char
                S: change case

        Text modes (3+4):
            0-9: character input
            ULR: navigate
            D: backspace
            S: cycle modes

        Number mode (5):
            0-9: numbers
            ULR: navigate
            D: backspace
            S: back to navigation
        """
        for key in keys:
            if self.mode == InputMode.NAVIGATE:
                self._handle_navigate_key(key)
            elif self.mode < InputMode.TEXT_LOWER:
                self._handle_edit_key(key)
            elif self.mode < InputMode.NUMERIC:
                self._handle_text_key(key)
            elif self.mode == InputMode.NUMERIC:
                self._handle_numeric_key(key)

    def _handle_navigate_key(self, key):
        """Handle key in navigation mode."""
        if key in [
            Key.NUM_1.value,
            Key.NUM_2.value,
            Key.NUM_3.value,
            Key.NUM_4.value,
            Key.NUM_5.value,
            Key.NUM_6.value,
            Key.NUM_7.value,
            Key.NUM_8.value,
            Key.NUM_9.value,
        ]:
            # starting a new word - edit mode
            self.mode = InputMode.EDIT_WORD
            self.keys = key
            self.words = self.dict.getwords(key)
            self.setword()

        elif key == Key.NUM_0.value:
            # insert a space
            self.textbefore = self.textbefore + " "

        elif key == Key.DOWN.value:
            # delete a char
            if self.textbefore == "":
                return
            if int(getkey(self.textbefore[-1])) < 2:
                self.textbefore = self.textbefore[:-1]
            else:
                # edit word
                self.mode = InputMode.EDIT_WORD
                # move in to edit buffer
                self.word = self.textbefore.split(" ")[-1]
                self.textbefore = self.textbefore[0 : self.textbefore.rfind(" ") + 1]
                if self.word == "":
                    self.mode = InputMode.NAVIGATE
                else:
                    self.keys = getkey(self.word)
                    self.words = self.dict.getwords(self.keys)

        elif key == Key.SELECT.value:
            self.mode = InputMode.TEXT_LOWER

        elif key in [Key.UP.value, Key.LEFT.value]:
            if self.textbefore == "":
                return
            # left a char
            if int(getkey(self.textbefore[-1])) < 2:
                # move one char
                self.textafter = self.textbefore[-1] + self.textafter
                self.textbefore = self.textbefore[:-1]
            else:
                # edit word
                self.mode = InputMode.EDIT_WORD
                # move to edit buffer
                t = self.textbefore.split(" ")
                self.word = t[-1]
                self.textbefore = self.textbefore[0 : self.textbefore.rfind(" ") + 1]
                self.keys = getkey(self.word)
                self.words = self.dict.getwords(self.keys)

        elif key == Key.RIGHT.value:
            # right a char
            if self.textafter == "":
                return
            if int(getkey(self.textafter[0])) < 2:
                # move one char
                self.textbefore = self.textbefore + self.textafter[0]
                self.textafter = self.textafter[1:]
            else:
                # edit word
                self.mode = InputMode.EDIT_WORD
                # move to edit buffer
                t = self.textafter.split(" ")
                self.word = t[0]
                self.textafter = self.textafter[len(t[0]) : len(self.textafter)]
                self.keys = getkey(self.word)
                self.words = self.dict.getwords(self.keys)

    def _handle_edit_key(self, key):
        """Handle key in edit modes (word and character)."""
        if key == Key.DOWN.value:
            # down key = delete 1 char
            self.keys = self.keys[:-1]
            # reset text
            self.setword()

        if self.mode == InputMode.EDIT_WORD:
            self._handle_edit_word_key(key)
        else:
            self._handle_edit_char_key(key)

    def _handle_edit_word_key(self, key):
        """Handle key in edit word mode."""
        if key in [
            Key.NUM_1.value,
            Key.NUM_2.value,
            Key.NUM_3.value,
            Key.NUM_4.value,
            Key.NUM_5.value,
            Key.NUM_6.value,
            Key.NUM_7.value,
            Key.NUM_8.value,
            Key.NUM_9.value,
        ]:
            # add keypress
            self.addkeypress(key)

        elif key in [Key.NUM_0.value, Key.RIGHT.value]:
            # save this word?
            if self.word not in self.words:
                # save it
                logger.info("saving word: %s", self.word)
                self.dict.addword(self.word)

            # return to navigate mode.
            self.mode = InputMode.NAVIGATE
            self.textbefore += self.word
            if key == Key.NUM_0.value:
                self.textbefore += " "
        elif key == Key.LEFT.value:
            # save this word?
            if self.word not in self.words:
                # save it
                logger.info("saving word: %s", self.word)
                self.dict.addword(self.word)

            # return to navigate mode.
            self.mode = InputMode.NAVIGATE
            self.textafter = self.word + self.textafter
        elif key == Key.UP.value:
            # up is navigate to next word
            self.nextword()

    def _handle_edit_char_key(self, key):
        """Handle key in edit character mode."""
        if key in [
            Key.NUM_1.value,
            Key.NUM_2.value,
            Key.NUM_3.value,
            Key.NUM_4.value,
            Key.NUM_5.value,
            Key.NUM_6.value,
            Key.NUM_7.value,
            Key.NUM_8.value,
            Key.NUM_9.value,
        ]:
            # add keypress
            self.addkeypress(key)

        if key == Key.NUM_0.value:
            # only move on if we are at the end
            if self.pos == len(self.word) - 1:
                # save this word?
                if self.word not in self.words:
                    logger.info("saving word: %s", self.word)
                    self.dict.addword(self.word)

                # return to navigate mode.
                self.mode = InputMode.NAVIGATE
                self.textbefore += self.word + " "
            else:
                # reset the text.
                self.setword()
        elif key == Key.UP.value:
            # up is navigate to next char
            self.nextchar()
        elif key == Key.SELECT.value:
            # change the case of current letter
            c = self.word[self.pos]
            if c.upper() == c:
                self.word = self.word[0 : self.pos] + c.lower() + self.word[self.pos + 1 : len(self.word)]
            else:
                self.word = self.word[0 : self.pos] + c.upper() + self.word[self.pos + 1 : len(self.word)]
        elif key == Key.LEFT.value:
            # move back one char
            if self.pos > 0:
                self.pos -= 1
        elif key == Key.RIGHT.value:
            # move forward one char
            k = ALLKEYS[int(self.keys[self.pos])]
            if self.word[self.pos].upper() in k:
                if self.pos == len(self.word) - 1:
                    # save this word?
                    if self.word not in self.words:
                        logger.info("saving word: %s", self.word)
                        self.dict.addword(self.word)

                    # return to navigate mode.
                    self.mode = InputMode.NAVIGATE
                    self.textbefore += self.word
                else:
                    self.pos += 1

    def _handle_text_key(self, key):
        """Handle key in text input modes."""
        if key in [
            Key.NUM_1.value,
            Key.NUM_2.value,
            Key.NUM_3.value,
            Key.NUM_4.value,
            Key.NUM_5.value,
            Key.NUM_6.value,
            Key.NUM_7.value,
            Key.NUM_8.value,
            Key.NUM_9.value,
        ]:
            # text entry mode 3 (boring way)
            if self.lastkeytime + self.keydelay > time.perf_counter() and key == self.lastkeypress:
                # edit char
                c = self.textbefore[-1].upper()
                print(ALLKEYS[int(key)].find(c), int(key), ALLKEYS[int(key)], c)
                i = ALLKEYS[int(key)].find(c)
                if i != -1:
                    if i == len(ALLKEYS[int(key)]) - 1:
                        c = ALLKEYS[int(key)][0]
                    else:
                        c = ALLKEYS[int(key)][i + 1]
                    print(self.mode)
                    if self.mode == InputMode.TEXT_LOWER:
                        # lower case in mode 4
                        c = c.lower()

                    self.textbefore = self.textbefore[:-1] + c

            else:
                # new char
                c = ALLKEYS[int(key)][0]
                if self.mode == InputMode.TEXT_LOWER:
                    # lower case in mode 4
                    c = c.lower()
                self.textbefore += c

            self.lastkeypress = key
            self.lastkeytime = time.perf_counter()
        else:
            self.lastkeytime = 0

        if key == Key.NUM_0.value:
            # space
            self.textbefore += " "
        elif key == Key.DOWN.value:
            # delete
            if self.textbefore != "":
                self.textbefore = self.textbefore[:-1]
        elif key in [Key.LEFT.value, Key.UP.value]:
            if self.textbefore != "":
                self.textafter = self.textbefore[-1] + self.textafter
                self.textbefore = self.textbefore[:-1]
        elif key == Key.RIGHT.value:
            if self.textafter != "":
                self.textbefore = self.textbefore + self.textafter[0]
                self.textafter = self.textafter[1:]
        elif key == Key.SELECT.value:
            self.mode += 1

    def _handle_numeric_key(self, key):
        """Handle key in numeric mode."""
        if key in [
            Key.NUM_0.value,
            Key.NUM_1.value,
            Key.NUM_2.value,
            Key.NUM_3.value,
            Key.NUM_4.value,
            Key.NUM_5.value,
            Key.NUM_6.value,
            Key.NUM_7.value,
            Key.NUM_8.value,
            Key.NUM_9.value,
        ]:
            self.textbefore += key
        elif key == Key.DOWN.value:
            # delete
            if self.textbefore != "":
                self.textbefore = self.textbefore[:-1]
        elif key in [Key.LEFT.value, Key.UP.value]:
            if self.textbefore != "":
                self.textafter = self.textbefore[-1] + self.textafter
                self.textbefore = self.textbefore[:-1]
        elif key == Key.RIGHT.value:
            if self.textafter != "":
                self.textbefore = self.textbefore + self.textafter[0]
                self.textafter = self.textafter[1:]
        elif key == Key.SELECT.value:
            self.mode = InputMode.NAVIGATE
