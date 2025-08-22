"""Tests for dictionary generation (makepy9 module)."""

import pytest
from pathlib import Path
from py9 import makepy9


def get_test_wordlists():
    """Get all .txt files from test data directory."""
    test_data_dir = Path(__file__).parent.parent / "data"
    return [f.name for f in test_data_dir.glob("*.txt")]


@pytest.mark.parametrize("wordlist_file", get_test_wordlists())
def test_makedict_creates_file(test_data_dir, tmpdir, wordlist_file):
    """Test that makedict creates a dictionary file for each test wordlist."""
    wordlist_path = test_data_dir / wordlist_file
    dict_path = tmpdir.join(f"{Path(wordlist_file).stem}.dict")

    makepy9.makedict(str(wordlist_path), str(dict_path), "Test Language", "Test dictionary")

    assert dict_path.exists()
    assert dict_path.size() > 0
