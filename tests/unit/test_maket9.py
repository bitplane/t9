"""Tests for dictionary generation (maket9 module)."""

import pytest
from pathlib import Path
from t9 import maket9
from t9.dict import T9Dict
from t9.utils import getkey


def get_test_wordlists():
    """Get all .txt files from test data directory."""
    test_data_dir = Path(__file__).parent.parent / "data"
    return [f.name for f in test_data_dir.glob("*.txt")]


@pytest.mark.parametrize("wordlist_file", get_test_wordlists())
def test_makedict_creates_file(test_data_dir, tmpdir, wordlist_file):
    """Test that makedict creates a dictionary file for each test wordlist."""
    wordlist_path = test_data_dir / wordlist_file
    dict_path = tmpdir.join(f"{Path(wordlist_file).stem}.dict")

    maket9.makedict(str(wordlist_path), str(dict_path), "Test Language", "Test dictionary")

    assert dict_path.exists()
    assert dict_path.size() > 0


@pytest.mark.parametrize("wordlist_file", get_test_wordlists())
def test_makedict_all_words_retrievable(test_data_dir, tmp_path, wordlist_file):
    """Test that all words from input file are retrievable from the dictionary."""
    wordlist_path = test_data_dir / wordlist_file
    dict_path = tmp_path / f"{Path(wordlist_file).stem}.dict"

    # Read input words
    with open(wordlist_path) as f:
        input_words = [line.strip() for line in f if line.strip()]

    # Create dictionary
    maket9.makedict(str(wordlist_path), str(dict_path), "Test", "Test")
    d = T9Dict(str(dict_path))

    # Verify each word can be retrieved
    for word in input_words:
        key = getkey(word)
        result = d.getwords(key)
        assert word in result, f"Word '{word}' (key {key}) not found in dictionary results {result}"
