"""Dictionary class for PY9 T9 text input system."""

import struct
import os
import logging

from .key import T9Key, SaveState
from .utils import getkey

logger = logging.getLogger(__name__)


class T9Dict:
    """T9 dictionary for word lookups and modifications."""

    def __init__(self, dict_file):
        """Create a T9 dictionary class and load file header info.

        dict_file: path to dictionary file

        File format:
        - word count (4 bytes)
        - root node pos (4 bytes)
        - language string (variable)
        - comment string (variable)
        """
        self.file = dict_file
        f = open(dict_file, "rb")
        f.seek(8)
        self.wordcount, self.rootpos = struct.unpack("!LL", f.read(8))
        self.language = f.readline().decode("utf-8").rstrip("\n\r")
        self.comment = f.readline().decode("utf-8").rstrip("\n\r")
        f.close()

    def getwords(self, digits):
        """Get possible words for a T9 digit sequence.

        Returns:
        - If len(result[0]) == len(digits): exact match found
        - If len(result[0]) > len(digits): lookahead used
        - If len(result[0]) < len(digits): lookbehind used
        """
        f = open(self.file, "rb")
        k = T9Key()
        oldlist = []
        p = self.rootpos
        logger.debug("root position: %s", p)

        # process each digit
        for c in digits:
            f.seek(p)
            k.__init__()
            k.loadnode(f)

            if k.refs[int(c) - 1] is not None:
                # the next node is available
                p = k.refs[int(c) - 1]
                if len(k.words) > 0:
                    # save the top word
                    oldlist = [k.words[0]]
            else:
                # didn't find the word - return short word
                f.close()
                del k
                return oldlist

        # reset node, load node
        k.__init__()
        f.seek(p)
        k.loadnode(f)
        if len(k.words) == 0:
            # couldn't find word
            if digits[-1] == "1":
                f.close()
                del k
                return oldlist
            else:
                while len(k.words) == 0:
                    p = 0
                    for i in k.refs:
                        if i is not None:
                            p = i
                            break
                    # Note: p should never be 0 with properly constructed dictionaries
                    # as makedict ensures all paths terminate in words
                    f.seek(p)
                    k.__init__()
                    k.loadnode(f)

            f.close()
            return k.words
        else:
            return k.words

    def addword(self, word):
        """Add a word to the dictionary.
        Raises KeyError if word already exists.
        """
        logger.debug("root position: %s", self.rootpos)
        key = getkey(word)

        f = open(self.file, "rb")

        nodes = []
        nodes.append(T9Key())
        f.seek(self.rootpos)
        nodes[0].loadnode(f)
        p = 0

        # process each digit
        for c in key:
            logger.debug("processing node %s", nodes[p].last)

            # is it referenced?
            if nodes[p].refs[int(c) - 1] is not None:
                # load it
                nodes.append(T9Key())
                f.seek(nodes[p].refs[int(c) - 1])
                p += 1
                nodes[p].loadnode(f)
            else:
                # create it
                p += 1
                nodes.append(T9Key())
                # node needs a save
                nodes[p].needsave = SaveState.NEW

            logger.debug("last node ref: %s", nodes[p - 1].refs[int(key[p - 1]) - 1])

            if nodes[p - 1].refs[int(key[p - 1]) - 1] is None:
                logger.debug("last node was new")
                # previous node is also new
                nodes[p - 1].needsave = SaveState.NEW
                if p - 2 >= 0:
                    if nodes[p - 2].refs[int(key[p - 2]) - 1] is None:
                        logger.debug("nested new node")
                        nodes[p - 2].needsave = SaveState.NEW
                    else:
                        nodes[p - 2].needsave = SaveState.UPDATE
            else:
                # previous node is old - update
                if nodes[p - 1].needsave != SaveState.NEW:
                    nodes[p - 1].needsave = SaveState.UPDATE

        f.close()

        # let's not add dupes
        for q in nodes[p].words:
            if q.lower() == word.lower():
                del nodes
                raise KeyError("Word '" + word + "' is already in dictionary '" + self.file + "' at position " + key)

        # sort out the last ones
        for n in range(1, len(nodes)):
            nodes[n].last = int(key[n - 1]) - 1

        # add the word to the list
        nodes[p].words.append(word)
        nodes[p].needsave = SaveState.NEW
        if nodes[p - 1].fpos != 0:
            nodes[p].last = int(c) - 1

        # now work from the last digit back saving each one
        for n in range(len(nodes) - 1, -1, -1):
            if nodes[n].needsave == SaveState.NEW:
                logger.debug("node %s needs save", n)

                # are we moving the root node?
                movert = self.rootpos == nodes[n].fpos

                f = open(self.file, "r+b")

                f.seek(os.stat(self.file)[6])
                logger.debug("processing node %s of %s", n, len(nodes))
                if n < len(nodes) - 1:
                    logger.debug("next node %s at position %s", nodes[n + 1].last, nodes[n + 1].fpos)
                    if nodes[n + 1].last != -1:
                        logger.debug("new file position for node %s: %s", n, nodes[n + 1].fpos)
                        nodes[n].refs[nodes[n + 1].last] = nodes[n + 1].fpos
                nodes[n].savenode(f)
                logger.debug("saved node %s at position %s", n, nodes[n].fpos)
                f.close()
                if movert:
                    self.rootpos = nodes[n].fpos

            elif nodes[n].needsave == SaveState.UPDATE:
                logger.debug("node %s needs update at position %s", n, nodes[n].fpos)
                f = open(self.file, "r+b")

                logger.debug("updating node %s with position %s", n, nodes[n + 1].fpos)
                nodes[n].refs[nodes[n + 1].last] = nodes[n + 1].fpos

                f.seek(nodes[n].fpos)
                nodes[n].savenode(f)
                f.close()
            # else: node doesn't need saving

        self.wordcount += 1
        f = open(self.file, "r+b")
        f.seek(8)
        f.write(struct.pack("!LL", self.wordcount, self.rootpos))
        f.close()
        logger.debug("root position: %s", self.rootpos)
        del nodes

    def delword(self, word):
        """
        Delete a word from the dictionary.
        Not implemented yet.
        """
        logger.error("T9Dict.delword() NOT IMPLEMENTED")
        raise NotImplementedError()
