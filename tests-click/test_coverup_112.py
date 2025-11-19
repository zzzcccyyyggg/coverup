# file: src/click/src/click/types.py:787-799
# asked: {"lines": [787, 789, 790, 791, 792, 793, 795, 796, 797, 798, 799], "branches": []}
# gained: {"lines": [787, 789, 790, 791, 792, 793, 795, 796, 797, 798, 799], "branches": []}

import pytest
import click
from click.types import File


class TestFileInit:
    """Test cases for File.__init__ method to cover lines 787-799."""
    
    def test_file_init_default_parameters(self):
        """Test File initialization with default parameters."""
        file_type = File()
        assert file_type.mode == "r"
        assert file_type.encoding is None
        assert file_type.errors == "strict"
        assert file_type.lazy is None
        assert file_type.atomic is False
    
    def test_file_init_custom_parameters(self):
        """Test File initialization with custom parameters."""
        file_type = File(
            mode="wb",
            encoding="utf-8",
            errors="ignore",
            lazy=True,
            atomic=True
        )
        assert file_type.mode == "wb"
        assert file_type.encoding == "utf-8"
        assert file_type.errors == "ignore"
        assert file_type.lazy is True
        assert file_type.atomic is True
    
    def test_file_init_partial_parameters(self):
        """Test File initialization with partial parameters."""
        file_type = File(mode="a", encoding="latin-1")
        assert file_type.mode == "a"
        assert file_type.encoding == "latin-1"
        assert file_type.errors == "strict"
        assert file_type.lazy is None
        assert file_type.atomic is False
    
    def test_file_init_binary_mode(self):
        """Test File initialization with binary mode."""
        file_type = File(mode="rb")
        assert file_type.mode == "rb"
        assert file_type.encoding is None
        assert file_type.errors == "strict"
        assert file_type.lazy is None
        assert file_type.atomic is False
    
    def test_file_init_write_mode(self):
        """Test File initialization with write mode."""
        file_type = File(mode="w", lazy=False)
        assert file_type.mode == "w"
        assert file_type.encoding is None
        assert file_type.errors == "strict"
        assert file_type.lazy is False
        assert file_type.atomic is False
