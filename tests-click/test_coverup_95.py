# file: src/click/src/click/types.py:806-813
# asked: {"lines": [806, 807, 808, 809, 810, 811, 812, 813], "branches": [[807, 808], [807, 809], [809, 810], [809, 811], [811, 812], [811, 813]]}
# gained: {"lines": [806, 807, 808, 809, 810, 811, 812, 813], "branches": [[807, 808], [807, 809], [809, 810], [809, 811], [811, 812], [811, 813]]}

import pytest
import os
from click.types import File


class TestFileResolveLazyFlag:
    """Test cases for File.resolve_lazy_flag method to achieve full coverage."""
    
    def test_resolve_lazy_flag_lazy_explicitly_set_true(self):
        """Test when lazy is explicitly set to True."""
        file_type = File(lazy=True)
        result = file_type.resolve_lazy_flag("test.txt")
        assert result is True
    
    def test_resolve_lazy_flag_lazy_explicitly_set_false(self):
        """Test when lazy is explicitly set to False."""
        file_type = File(lazy=False)
        result = file_type.resolve_lazy_flag("test.txt")
        assert result is False
    
    def test_resolve_lazy_flag_stdin_stdout(self):
        """Test when value is '-' (stdin/stdout)."""
        file_type = File()
        result = file_type.resolve_lazy_flag("-")
        assert result is False
    
    def test_resolve_lazy_flag_write_mode(self):
        """Test when mode contains 'w' (write mode)."""
        file_type = File(mode="w")
        result = file_type.resolve_lazy_flag("output.txt")
        assert result is True
    
    def test_resolve_lazy_flag_append_mode(self):
        """Test when mode contains 'a' (append mode)."""
        file_type = File(mode="a")
        result = file_type.resolve_lazy_flag("output.txt")
        assert result is False
    
    def test_resolve_lazy_flag_write_plus_mode(self):
        """Test when mode contains 'w+' (read/write mode)."""
        file_type = File(mode="w+")
        result = file_type.resolve_lazy_flag("output.txt")
        assert result is True
    
    def test_resolve_lazy_flag_read_mode(self):
        """Test when mode is read-only (no 'w')."""
        file_type = File(mode="r")
        result = file_type.resolve_lazy_flag("input.txt")
        assert result is False
    
    def test_resolve_lazy_flag_read_binary_mode(self):
        """Test when mode is read-only binary (no 'w')."""
        file_type = File(mode="rb")
        result = file_type.resolve_lazy_flag("input.bin")
        assert result is False
