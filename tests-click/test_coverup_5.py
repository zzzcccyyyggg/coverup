# file: src/click/src/click/types.py:968-1039
# asked: {"lines": [968, 974, 976, 978, 979, 980, 982, 983, 984, 985, 986, 987, 988, 989, 991, 992, 995, 996, 997, 998, 1000, 1001, 1003, 1004, 1005, 1006, 1008, 1009, 1012, 1013, 1014, 1015, 1017, 1018, 1021, 1022, 1023, 1024, 1026, 1027, 1030, 1031, 1032, 1033, 1035, 1036, 1039], "branches": [[978, 979], [978, 1039], [979, 980], [979, 982], [985, 986], [985, 987], [995, 996], [995, 1003], [1003, 1004], [1003, 1012], [1012, 1013], [1012, 1021], [1021, 1022], [1021, 1030], [1030, 1031], [1030, 1039]]}
# gained: {"lines": [968, 974, 976, 978, 979, 980, 982, 983, 984, 985, 986, 987, 988, 989, 991, 992, 995, 996, 997, 998, 1000, 1001, 1003, 1004, 1005, 1006, 1008, 1009, 1012, 1013, 1014, 1015, 1017, 1018, 1021, 1022, 1023, 1024, 1026, 1027, 1030, 1031, 1032, 1033, 1035, 1036, 1039], "branches": [[978, 979], [978, 1039], [979, 980], [979, 982], [985, 986], [985, 987], [995, 996], [995, 1003], [1003, 1004], [1003, 1012], [1012, 1013], [1012, 1021], [1021, 1022], [1021, 1030], [1030, 1031], [1030, 1039]]}

import os
import tempfile
import pytest
from click.types import Path
from click.core import Context, Parameter

class TestPathConvert:
    """Test cases for Path.convert method to achieve full coverage of lines 968-1039."""
    
    def test_convert_with_dash_when_file_okay_and_allow_dash(self):
        """Test that '-' is allowed when file_okay=True and allow_dash=True."""
        path_type = Path(file_okay=True, allow_dash=True)
        result = path_type.convert("-", None, None)
        assert result == "-"
    
    def test_convert_with_dash_bytes_when_file_okay_and_allow_dash(self):
        """Test that b'-' is allowed when file_okay=True and allow_dash=True."""
        path_type = Path(file_okay=True, allow_dash=True)
        result = path_type.convert(b"-", None, None)
        assert result == b"-"
    
    def test_convert_with_resolve_path(self, tmp_path):
        """Test that resolve_path resolves symlinks."""
        # Create a file and a symlink to it
        target_file = tmp_path / "target.txt"
        target_file.write_text("content")
        symlink_file = tmp_path / "symlink.txt"
        symlink_file.symlink_to(target_file)
        
        path_type = Path(resolve_path=True)
        result = path_type.convert(str(symlink_file), None, None)
        assert result == str(target_file.resolve())
    
    def test_convert_nonexistent_path_when_exists_false(self, tmp_path):
        """Test that non-existent path is allowed when exists=False."""
        nonexistent_path = tmp_path / "nonexistent.txt"
        path_type = Path(exists=False)
        result = path_type.convert(str(nonexistent_path), None, None)
        assert result == str(nonexistent_path)
    
    def test_convert_nonexistent_path_when_exists_true(self, tmp_path):
        """Test that non-existent path fails when exists=True."""
        nonexistent_path = tmp_path / "nonexistent.txt"
        path_type = Path(exists=True)
        with pytest.raises(Exception) as exc_info:
            path_type.convert(str(nonexistent_path), None, None)
        assert "does not exist" in str(exc_info.value)
    
    def test_convert_file_when_file_okay_false(self, tmp_path):
        """Test that file fails when file_okay=False."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")
        path_type = Path(file_okay=False, dir_okay=True)
        with pytest.raises(Exception) as exc_info:
            path_type.convert(str(test_file), None, None)
        assert "is a file" in str(exc_info.value)
    
    def test_convert_directory_when_dir_okay_false(self, tmp_path):
        """Test that directory fails when dir_okay=False."""
        test_dir = tmp_path / "test_dir"
        test_dir.mkdir()
        path_type = Path(file_okay=True, dir_okay=False)
        with pytest.raises(Exception) as exc_info:
            path_type.convert(str(test_dir), None, None)
        assert "is a directory" in str(exc_info.value)
    
    def test_convert_unreadable_file_when_readable_true(self, tmp_path):
        """Test that unreadable file fails when readable=True."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")
        # Make file unreadable
        test_file.chmod(0o000)
        
        path_type = Path(readable=True)
        with pytest.raises(Exception) as exc_info:
            path_type.convert(str(test_file), None, None)
        assert "is not readable" in str(exc_info.value)
        
        # Clean up permissions
        test_file.chmod(0o644)
    
    def test_convert_unwritable_file_when_writable_true(self, tmp_path):
        """Test that unwritable file fails when writable=True."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")
        # Make file unwritable
        test_file.chmod(0o444)
        
        path_type = Path(writable=True)
        with pytest.raises(Exception) as exc_info:
            path_type.convert(str(test_file), None, None)
        assert "is not writable" in str(exc_info.value)
        
        # Clean up permissions
        test_file.chmod(0o644)
    
    def test_convert_unexecutable_file_when_executable_true(self, tmp_path):
        """Test that unexecutable file fails when executable=True."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")
        # Make file unexecutable
        test_file.chmod(0o644)
        
        path_type = Path(executable=True)
        with pytest.raises(Exception) as exc_info:
            path_type.convert(str(test_file), None, None)
        assert "is not executable" in str(exc_info.value)
    
    def test_convert_executable_file_when_executable_true(self, tmp_path):
        """Test that executable file passes when executable=True."""
        test_file = tmp_path / "test.sh"
        test_file.write_text("#!/bin/bash\necho 'test'")
        # Make file executable
        test_file.chmod(0o755)
        
        path_type = Path(executable=True)
        result = path_type.convert(str(test_file), None, None)
        assert result == str(test_file)
    
    def test_convert_with_dash_when_file_okay_false_but_allow_dash(self):
        """Test that '-' is still allowed even when file_okay=False if allow_dash=True."""
        path_type = Path(file_okay=False, allow_dash=True)
        result = path_type.convert("-", None, None)
        assert result == "-"
    
    def test_convert_with_dash_when_dir_okay_false_but_allow_dash(self):
        """Test that '-' is still allowed even when dir_okay=False if allow_dash=True."""
        path_type = Path(dir_okay=False, allow_dash=True)
        result = path_type.convert("-", None, None)
        assert result == "-"
