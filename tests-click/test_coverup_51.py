# file: src/click/src/click/utils.py:523-575
# asked: {"lines": [523, 524, 546, 547, 549, 550, 556, 557, 558, 559, 560, 563, 568, 569, 572, 573, 575], "branches": [[546, 547], [546, 549], [549, 550], [549, 556], [556, 563], [556, 568], [572, 573], [572, 575]]}
# gained: {"lines": [523, 524, 546, 547, 549, 550, 556, 557, 563, 568, 569, 572, 573, 575], "branches": [[546, 547], [546, 549], [549, 550], [549, 556], [556, 563], [556, 568], [572, 573], [572, 575]]}

import pytest
import sys
import os
from types import ModuleType
from unittest.mock import patch, MagicMock
from click.utils import _detect_program_name


class TestDetectProgramName:
    """Test cases for _detect_program_name function to achieve full coverage."""
    
    def test_detect_program_name_file_execution_no_package(self, monkeypatch):
        """Test when executing a file directly (no __package__)."""
        # Create a mock main module without __package__
        mock_main = MagicMock()
        delattr(mock_main, '__package__')
        
        result = _detect_program_name(path="/path/to/script.py", _main=mock_main)
        assert result == "script.py"
    
    def test_detect_program_name_file_execution_empty_package(self, monkeypatch):
        """Test when executing a file directly (empty __package__)."""
        mock_main = MagicMock()
        mock_main.__package__ = ""
        
        result = _detect_program_name(path="/path/to/script.py", _main=mock_main)
        assert result == "script.py"
    
    def test_detect_program_name_windows_exe_case(self, monkeypatch):
        """Test Windows-specific case where .exe exists but path doesn't."""
        mock_main = MagicMock()
        mock_main.__package__ = ""
        
        with patch('os.name', 'nt'):
            with patch('os.path.exists') as mock_exists:
                mock_exists.side_effect = lambda p: p.endswith('.exe')
                result = _detect_program_name(path="/path/to/script", _main=mock_main)
                assert result == "script"
    
    def test_detect_program_name_module_execution_main_module(self, monkeypatch):
        """Test when executing a module with __main__ as the script name."""
        mock_main = MagicMock()
        mock_main.__package__ = "example"
        
        result = _detect_program_name(path="/path/to/__main__.py", _main=mock_main)
        assert result == "python -m example"
    
    def test_detect_program_name_module_execution_submodule(self, monkeypatch):
        """Test when executing a submodule."""
        mock_main = MagicMock()
        mock_main.__package__ = "example"
        
        result = _detect_program_name(path="/path/to/cli.py", _main=mock_main)
        assert result == "python -m example.cli"
    
    def test_detect_program_name_module_execution_dotted_package(self, monkeypatch):
        """Test when package has leading dots."""
        mock_main = MagicMock()
        mock_main.__package__ = ".example"
        
        result = _detect_program_name(path="/path/to/cli.py", _main=mock_main)
        assert result == "python -m example.cli"
    
    def test_detect_program_name_default_path_and_main(self, monkeypatch):
        """Test with default parameters (None path and _main)."""
        # Save original values
        original_argv0 = sys.argv[0]
        original_main = sys.modules.get("__main__")
        
        try:
            # Set up test environment
            sys.argv[0] = "/path/to/default_script.py"
            mock_main = MagicMock()
            mock_main.__package__ = "test_package"
            sys.modules["__main__"] = mock_main
            
            result = _detect_program_name()
            assert result == "python -m test_package.default_script"
            
        finally:
            # Restore original values
            sys.argv[0] = original_argv0
            if original_main:
                sys.modules["__main__"] = original_main
            else:
                del sys.modules["__main__"]
    
    def test_detect_program_name_windows_normal_case(self, monkeypatch):
        """Test Windows case where path exists normally."""
        mock_main = MagicMock()
        mock_main.__package__ = ""
        
        with patch('os.name', 'nt'):
            with patch('os.path.exists') as mock_exists:
                mock_exists.return_value = True
                result = _detect_program_name(path="/path/to/script.py", _main=mock_main)
                assert result == "script.py"
