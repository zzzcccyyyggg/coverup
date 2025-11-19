# file: src/click/src/click/testing.py:114-128
# asked: {"lines": [114, 115, 118, 119, 120, 122, 123, 124, 126, 127, 128], "branches": []}
# gained: {"lines": [114, 115, 118, 119, 120, 122, 123, 124, 126, 127, 128], "branches": []}

import io
import pytest
from click.testing import _NamedTextIOWrapper

def test_named_text_io_wrapper_initialization():
    """Test that _NamedTextIOWrapper properly initializes with name and mode."""
    buffer = io.BytesIO(b"test data")
    wrapper = _NamedTextIOWrapper(buffer, "test_file.txt", "r")
    
    assert wrapper.name == "test_file.txt"
    assert wrapper.mode == "r"

def test_named_text_io_wrapper_with_kwargs():
    """Test that _NamedTextIOWrapper accepts and passes through kwargs."""
    buffer = io.BytesIO(b"test data")
    wrapper = _NamedTextIOWrapper(buffer, "test_file.txt", "r", encoding="utf-8")
    
    assert wrapper.name == "test_file.txt"
    assert wrapper.mode == "r"

def test_named_text_io_wrapper_properties():
    """Test that name and mode properties return the correct values."""
    buffer = io.BytesIO(b"test data")
    wrapper = _NamedTextIOWrapper(buffer, "different_name.txt", "w")
    
    assert wrapper.name == "different_name.txt"
    assert wrapper.mode == "w"
