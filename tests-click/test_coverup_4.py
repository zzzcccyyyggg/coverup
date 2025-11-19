# file: src/click/src/click/_termui_impl.py:507-551
# asked: {"lines": [507, 516, 517, 519, 521, 523, 524, 525, 529, 531, 532, 534, 536, 537, 538, 539, 540, 541, 542, 543, 544, 546, 548, 549, 551], "branches": [[516, 517], [516, 519], [524, 525], [524, 529], [537, 538], [537, 539]]}
# gained: {"lines": [507, 516, 517, 519, 521, 523, 524, 525, 529, 531, 532, 534, 536, 537, 538, 539, 540, 541, 542, 543, 544, 546, 548, 549, 551], "branches": [[516, 517], [516, 519], [524, 525], [524, 529], [537, 538], [537, 539]]}

import pytest
import tempfile
import os
from unittest.mock import Mock, patch
import subprocess
from click._termui_impl import _tempfilepager
from click._compat import strip_ansi


class TestTempFilePager:
    def test_tempfilepager_empty_cmd_parts(self):
        """Test _tempfilepager returns False when cmd_parts is empty"""
        generator = ["line1\n", "line2\n"]
        result = _tempfilepager(generator, [], color=None)
        assert result is False

    def test_tempfilepager_command_not_found(self):
        """Test _tempfilepager returns False when command is not found"""
        generator = ["line1\n", "line2\n"]
        with patch('shutil.which') as mock_which:
            mock_which.return_value = None
            result = _tempfilepager(generator, ['nonexistent_command'], color=None)
            assert result is False

    def test_tempfilepager_successful_execution_with_color(self):
        """Test _tempfilepager successful execution with color=True"""
        generator = ["\x1b[31mred text\x1b[0m\n", "normal text\n"]
        
        with patch('shutil.which') as mock_which, \
             patch('subprocess.call') as mock_call, \
             patch('tempfile.mkstemp') as mock_mkstemp, \
             patch('builtins.open') as mock_open, \
             patch('os.close') as mock_close, \
             patch('os.unlink') as mock_unlink:
            
            # Mock tempfile creation
            mock_mkstemp.return_value = (123, '/tmp/testfile')
            
            # Mock file operations
            mock_file = Mock()
            mock_file.__enter__ = Mock(return_value=mock_file)
            mock_file.__exit__ = Mock(return_value=None)
            mock_open.return_value = mock_file
            
            # Mock command lookup
            mock_which.return_value = '/usr/bin/less'
            
            # Mock subprocess call
            mock_call.return_value = 0
            
            result = _tempfilepager(generator, ['less'], color=True)
            
            assert result is True
            mock_call.assert_called_once()
            mock_close.assert_called_once_with(123)
            mock_unlink.assert_called_once_with('/tmp/testfile')
            
            # Verify text was written with ANSI codes preserved (color=True)
            mock_file.write.assert_called_once()
            written_data = mock_file.write.call_args[0][0]
            assert b'\x1b[31mred text\x1b[0m' in written_data

    def test_tempfilepager_successful_execution_without_color(self):
        """Test _tempfilepager successful execution with color=False"""
        generator = ["\x1b[31mred text\x1b[0m\n", "normal text\n"]
        
        with patch('shutil.which') as mock_which, \
             patch('subprocess.call') as mock_call, \
             patch('tempfile.mkstemp') as mock_mkstemp, \
             patch('builtins.open') as mock_open, \
             patch('os.close') as mock_close, \
             patch('os.unlink') as mock_unlink:
            
            # Mock tempfile creation
            mock_mkstemp.return_value = (123, '/tmp/testfile')
            
            # Mock file operations
            mock_file = Mock()
            mock_file.__enter__ = Mock(return_value=mock_file)
            mock_file.__exit__ = Mock(return_value=None)
            mock_open.return_value = mock_file
            
            # Mock command lookup
            mock_which.return_value = '/usr/bin/less'
            
            # Mock subprocess call
            mock_call.return_value = 0
            
            result = _tempfilepager(generator, ['less'], color=False)
            
            assert result is True
            mock_call.assert_called_once()
            mock_close.assert_called_once_with(123)
            mock_unlink.assert_called_once_with('/tmp/testfile')
            
            # Verify text was written without ANSI codes (color=False)
            mock_file.write.assert_called_once()
            written_data = mock_file.write.call_args[0][0]
            assert b'\x1b[31mred text\x1b[0m' not in written_data
            assert b'red text' in written_data

    def test_tempfilepager_subprocess_oserror(self):
        """Test _tempfilepager handles OSError from subprocess.call"""
        generator = ["line1\n", "line2\n"]
        
        with patch('shutil.which') as mock_which, \
             patch('subprocess.call') as mock_call, \
             patch('tempfile.mkstemp') as mock_mkstemp, \
             patch('builtins.open') as mock_open, \
             patch('os.close') as mock_close, \
             patch('os.unlink') as mock_unlink:
            
            # Mock tempfile creation
            mock_mkstemp.return_value = (123, '/tmp/testfile')
            
            # Mock file operations
            mock_file = Mock()
            mock_file.__enter__ = Mock(return_value=mock_file)
            mock_file.__exit__ = Mock(return_value=None)
            mock_open.return_value = mock_file
            
            # Mock command lookup
            mock_which.return_value = '/usr/bin/less'
            
            # Mock subprocess call raising OSError
            mock_call.side_effect = OSError("Command not found")
            
            result = _tempfilepager(generator, ['less'], color=None)
            
            # Should still return True despite OSError
            assert result is True
            mock_close.assert_called_once_with(123)
            mock_unlink.assert_called_once_with('/tmp/testfile')

    def test_tempfilepager_empty_generator(self):
        """Test _tempfilepager with empty generator"""
        generator = []
        
        with patch('shutil.which') as mock_which, \
             patch('subprocess.call') as mock_call, \
             patch('tempfile.mkstemp') as mock_mkstemp, \
             patch('builtins.open') as mock_open, \
             patch('os.close') as mock_close, \
             patch('os.unlink') as mock_unlink:
            
            # Mock tempfile creation
            mock_mkstemp.return_value = (123, '/tmp/testfile')
            
            # Mock file operations
            mock_file = Mock()
            mock_file.__enter__ = Mock(return_value=mock_file)
            mock_file.__exit__ = Mock(return_value=None)
            mock_open.return_value = mock_file
            
            # Mock command lookup
            mock_which.return_value = '/usr/bin/less'
            
            # Mock subprocess call
            mock_call.return_value = 0
            
            result = _tempfilepager(generator, ['less'], color=None)
            
            assert result is True
            mock_call.assert_called_once()
            mock_close.assert_called_once_with(123)
            mock_unlink.assert_called_once_with('/tmp/testfile')
            
            # Verify empty text was written
            mock_file.write.assert_called_once_with(b'')
