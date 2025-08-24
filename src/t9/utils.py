"""Utility functions for PY9 T9 text input system."""

import gzip
import os
import tempfile
import platform
from pathlib import Path
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


def read_wordlist(filename):
    """Read lines from a wordlist file, handling both plain and gzipped files.

    Yields stripped non-empty lines from the file.

    Args:
        filename: Path to the wordlist file (.txt or .txt.gz)

    Yields:
        str: Each non-empty line from the file, stripped of whitespace
    """
    if str(filename).endswith(".gz"):
        with gzip.open(filename, "rt", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    yield line
    else:
        with open(filename, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    yield line


def get_wordlists_dir():
    """Get the path to the wordlists directory."""
    return Path(__file__).parent / "wordlists"


def get_cache_dir():
    """Get the path to the cache directory for dictionaries."""
    if platform.system() == "Windows":
        # Try LOCALAPPDATA first, then APPDATA
        cache_base = os.environ.get("LOCALAPPDATA") or os.environ.get("APPDATA")
        if cache_base:
            cache_dir = Path(cache_base) / "t9"
        else:
            # Fallback to temp directory
            cache_dir = Path(tempfile.gettempdir()) / "t9"
    else:
        # Linux/Mac: use XDG cache directory
        cache_base = os.environ.get("XDG_CACHE_HOME")
        if cache_base:
            cache_dir = Path(cache_base) / "t9"
        else:
            # Default to ~/.cache/t9
            cache_dir = Path.home() / ".cache" / "t9"

    # Create directory if it doesn't exist
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir


def get_locale():
    """Get user's locale as (language, region) tuple.

    Returns:
        tuple: (language, region) or (None, None) if not found
    """
    # Check environment variables in order of preference
    for env_var in ["LANG", "LC_ALL", "LC_MESSAGES"]:
        locale_str = os.environ.get(env_var)
        if locale_str:
            # Parse formats like "en_GB.UTF-8" or "en_GB"
            parts = locale_str.split(".")
            locale_part = parts[0]  # Remove encoding if present

            if "_" in locale_part:
                language, region = locale_part.split("_", 1)
                return (language.lower(), region.upper())
            else:
                # Just language, no region
                return (locale_part.lower(), None)

    return (None, None)


def find_wordlist(language, region=None):
    """Find wordlist file for given language and region.

    Args:
        language: Language code (e.g., "en")
        region: Region code (e.g., "GB") or None

    Returns:
        Path to wordlist file if found, None otherwise
    """
    wordlists_dir = get_wordlists_dir()

    # Try with region first if provided
    if region:
        for ext in [".words.gz", ".words"]:
            wordlist_path = wordlists_dir / f"{language}-{region}{ext}"
            if wordlist_path.exists():
                return wordlist_path

    # Try language only
    for ext in [".words.gz", ".words"]:
        wordlist_path = wordlists_dir / f"{language}{ext}"
        if wordlist_path.exists():
            return wordlist_path

    return None


def get_system_wordlist():
    """Get system dictionary file, resolving symlinks.

    Returns:
        Path to system wordlist if found, None otherwise
    """
    if platform.system() == "Windows":
        # Windows doesn't typically have system word lists
        return None

    # Common Unix locations
    for dict_path in ["/usr/share/dict/words", "/usr/dict/words"]:
        path = Path(dict_path)
        if path.exists():
            # Resolve symlinks
            return path.resolve()

    return None


def find_or_generate_dict(language=None, region=None):
    """Find or generate dictionary file using fallback chain.

    Args:
        language: Language code or None to auto-detect
        region: Region code or None to auto-detect

    Returns:
        Path to dictionary file if found/generated, None if failed
    """
    # Auto-detect locale if not provided
    if language is None:
        detected_lang, detected_region = get_locale()
        language = detected_lang
        if region is None:
            region = detected_region

    # If still no language, give up
    if not language:
        return None

    cache_dir = get_cache_dir()

    # Construct cache filename
    if region:
        cache_name = f"{language}-{region}.dict"
    else:
        cache_name = f"{language}.dict"

    cache_path = cache_dir / cache_name

    # Check if cached dict exists
    if cache_path.exists():
        return cache_path

    # Try to generate from package wordlist
    wordlist_path = find_wordlist(language, region)
    if wordlist_path:
        from . import maket9

        try:
            lang_desc = f"{language.upper()}"
            if region:
                lang_desc += f"-{region}"
            maket9.makedict(str(wordlist_path), str(cache_path), lang_desc, "Generated from package wordlist")
            return cache_path
        except Exception:
            # Generation failed, continue to next fallback
            pass

    # Try system wordlist as fallback
    system_wordlist = get_system_wordlist()
    if system_wordlist:
        from . import maket9

        try:
            lang_desc = f"{language.upper()}"
            if region:
                lang_desc += f"-{region}"
            maket9.makedict(str(system_wordlist), str(cache_path), lang_desc, "Generated from system wordlist")
            return cache_path
        except Exception:
            # Generation failed
            pass

    return None


def draw_keypad():
    """Draw a T9 keypad layout for reference."""
    print("  1    2    3")
    print(" .?!  abc  def")
    print()
    print("  4    5    6")
    print(" ghi  jkl  mno")
    print()
    print("  7    8    9")
    print("pqrs  tuv  wxyz")
    print()
    print("       0")
