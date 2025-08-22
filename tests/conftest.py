"""Pytest configuration and fixtures for PY9 tests."""

import pytest
from pathlib import Path


@pytest.fixture
def test_data_dir():
    """Get the test data directory path."""
    return Path(__file__).parent / "data"
