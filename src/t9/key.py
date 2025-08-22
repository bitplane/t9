"""Dictionary node class for PY9 T9 text input system."""

import struct
import logging
from enum import IntEnum

logger = logging.getLogger(__name__)


class SaveState(IntEnum):
    """Node save state for dictionary file operations."""

    UNCHANGED = -1  # Node doesn't need any file operation
    UPDATE = 1  # Existing node needs reference update
    NEW = 2  # New node needs full save to file


class T9Key:
    """Dictionary node for file-based keypress dictionary storage."""

    def __init__(self):
        self.refs = [None, None, None, None, None, None, None, None, None]
        self.words = []
        self.fpos = 0
        self.needsave = SaveState.UNCHANGED
        self.last = -1

    def save(self, f):
        """
        Save the node and all child nodes to file f.
        Used when creating dictionary file.
        """
        # recurse save children first so self.ref[x].fpos is always set
        for i in self.refs:
            if i:
                i.save(f)
        # now get position in file
        self.fpos = f.tell()

        # write flags (2 bytes)
        flags = 0
        for i in range(1, 10):
            if self.refs[i - 1] is not None:
                flags = 2**i | flags
        f.write(struct.pack("!h", flags))

        # write positions of children (4 bytes each)
        for i in self.refs:
            if i:
                f.write(struct.pack("!i", i.fpos))

        # write number of words
        f.write(struct.pack("!h", len(self.words)))

        # write list of words
        for word in self.words:
            f.write(("%s\n" % word).encode("utf-8"))

    def savenode(self, f):
        """
        Save just this node to the file.
        Used to add or overwrite a node.
        """
        # get position in file
        self.fpos = f.tell()

        # write flags (2 bytes)
        flags = 0
        for i in range(1, 10):
            if self.refs[i - 1] is not None:
                flags = 2**i | flags
        logger.debug("writing flags %s %s %s", self.words, flags, self.refs)

        f.write(struct.pack("!h", flags))

        # write positions of children (4 bytes each)
        logger.debug("saving children")
        for i in self.refs:
            if i:
                logger.debug("saving child %s", i)
                f.write(struct.pack("!i", i))

        logger.debug("... done saving children")

        # write number of words
        f.write(struct.pack("!h", len(self.words)))

        # write list of words
        for word in self.words:
            f.write(("%s\n" % word).encode("utf-8"))

    def loadnode(self, f):
        """
        Load a node from an open file object.
        """
        self.fpos = f.tell()
        # read flags (2 bytes)
        (flags,) = struct.unpack("!h", f.read(2))
        c = 0
        # loop through flags
        for i in range(1, 10):
            if 2**i & flags != 0:
                f.seek(self.fpos + 2 + c * 4)
                c += 1
                (self.refs[i - 1],) = struct.unpack("!L", f.read(4))

        # read word count
        (wc,) = struct.unpack("!h", f.read(2))
        self.words = []
        for n in range(0, wc):
            self.words.append(f.readline().decode("utf-8").rstrip("\n\r"))

        logger.debug("loaded node: refs=%s words=%s", self.refs, self.words)
