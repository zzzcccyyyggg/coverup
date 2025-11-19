# file: src/click/src/click/termui.py:76-80
# asked: {"lines": [76, 77, 78, 80], "branches": [[77, 78], [77, 80]]}
# gained: {"lines": [76, 77, 78, 80], "branches": [[77, 78], [77, 80]]}

import io
import os
import tempfile
import pytest
import typing as t
from click.utils import LazyFile
from click.termui import _format_default


def test_format_default_with_io_base_with_name():
    """Test _format_default with io.IOBase object that has name attribute."""
    class MockIO(io.IOBase):
        def __init__(self, name):
            self.name = name
    
    mock_file = MockIO("test.txt")
    result = _format_default(mock_file)
    assert result == "test.txt"


def test_format_default_with_lazyfile():
    """Test _format_default with LazyFile object."""
    # Create a temporary file for reading
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp:
        tmp.write("test content")
        tmp_path = tmp.name
    
    try:
        lazy_file = LazyFile(tmp_path, "r")
        result = _format_default(lazy_file)
        assert result == tmp_path
    finally:
        # Clean up the temporary file
        os.unlink(tmp_path)


def test_format_default_with_lazyfile_write_mode():
    """Test _format_default with LazyFile object in write mode."""
    # For write mode, no file needs to exist
    lazy_file = LazyFile("output.txt", "w")
    result = _format_default(lazy_file)
    assert result == "output.txt"


def test_format_default_with_io_base_without_name():
    """Test _format_default with io.IOBase object without name attribute."""
    class MockIOWithoutName(io.IOBase):
        pass
    
    mock_file = MockIOWithoutName()
    result = _format_default(mock_file)
    assert result is mock_file


def test_format_default_with_other_types():
    """Test _format_default with other data types."""
    # Test with string
    assert _format_default("hello") == "hello"
    
    # Test with integer
    assert _format_default(42) == 42
    
    # Test with list
    test_list = [1, 2, 3]
    assert _format_default(test_list) is test_list
    
    # Test with None
    assert _format_default(None) is None
