"""
Python T9 style dictionary by Bitplane feedback@bitplane.net

Classes have been moved to separate modules:
- Py9Key -> key.py
- Py9Dict -> dict.py
- Py9Input -> input.py

Import from those modules directly or use the main package imports.
"""

# Backward compatibility imports
from .key import Py9Key
from .dict import Py9Dict
from .input import Py9Input

__all__ = ["Py9Key", "Py9Dict", "Py9Input"]
