# file: src/click/src/click/types.py:914-941
# asked: {"lines": [914, 916, 917, 918, 919, 920, 921, 922, 923, 924, 926, 927, 928, 929, 930, 931, 932, 933, 934, 936, 937, 938, 939, 941], "branches": [[936, 937], [936, 938], [938, 939], [938, 941]]}
# gained: {"lines": [914, 916, 917, 918, 919, 920, 921, 922, 923, 924, 926, 927, 928, 929, 930, 931, 932, 933, 934, 936, 937, 938, 939, 941], "branches": [[936, 937], [936, 938], [938, 939], [938, 941]]}

import pytest
from click.types import Path
from gettext import gettext as _

class TestPathInit:
    """Test cases for Path.__init__ method to cover lines 914-941"""
    
    def test_path_init_file_only(self):
        """Test Path initialization with file_okay=True, dir_okay=False"""
        path_type = Path(file_okay=True, dir_okay=False)
        assert path_type.file_okay is True
        assert path_type.dir_okay is False
        assert path_type.name == _("file")
    
    def test_path_init_directory_only(self):
        """Test Path initialization with dir_okay=True, file_okay=False"""
        path_type = Path(dir_okay=True, file_okay=False)
        assert path_type.dir_okay is True
        assert path_type.file_okay is False
        assert path_type.name == _("directory")
    
    def test_path_init_both_allowed(self):
        """Test Path initialization with both file_okay=True and dir_okay=True"""
        path_type = Path(file_okay=True, dir_okay=True)
        assert path_type.file_okay is True
        assert path_type.dir_okay is True
        assert path_type.name == _("path")
    
    def test_path_init_neither_allowed(self):
        """Test Path initialization with both file_okay=False and dir_okay=False"""
        path_type = Path(file_okay=False, dir_okay=False)
        assert path_type.file_okay is False
        assert path_type.dir_okay is False
        assert path_type.name == _("path")
    
    def test_path_init_with_all_parameters(self):
        """Test Path initialization with all parameters set"""
        path_type = Path(
            exists=True,
            file_okay=True,
            dir_okay=False,
            writable=True,
            readable=False,
            resolve_path=True,
            allow_dash=True,
            path_type=str,
            executable=True
        )
        assert path_type.exists is True
        assert path_type.file_okay is True
        assert path_type.dir_okay is False
        assert path_type.writable is True
        assert path_type.readable is False
        assert path_type.resolve_path is True
        assert path_type.allow_dash is True
        assert path_type.type is str
        assert path_type.executable is True
        assert path_type.name == _("file")
