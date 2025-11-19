# file: src/click/src/click/_termui_impl.py:594-618
# asked: {"lines": [594, 595, 597, 598, 600, 601, 602, 604, 606, 607, 608, 610, 611, 612, 613, 615, 616, 617, 618], "branches": [[600, 601], [600, 604], [611, 0], [611, 612]]}
# gained: {"lines": [594, 595, 597, 598, 600, 601, 602, 604, 606, 607, 608, 610, 611, 612, 613, 615, 616, 617, 618], "branches": [[600, 601], [600, 604], [611, 0], [611, 612]]}

import pytest
import subprocess
from unittest.mock import Mock, patch, MagicMock
from click._termui_impl import Editor
from click.exceptions import ClickException

class TestEditorEditFiles:
    
    def test_edit_files_with_env(self, monkeypatch):
        """Test edit_files when self.env is set"""
        editor = Editor(env={"TEST_VAR": "test_value"})
        mock_popen = Mock()
        mock_popen.wait.return_value = 0
        
        with patch.object(editor, 'get_editor', return_value='vim'):
            with patch('subprocess.Popen', return_value=mock_popen) as mock_popen_call:
                editor.edit_files(['test.txt'])
                
                # Verify Popen was called with the expected environment
                call_kwargs = mock_popen_call.call_args[1]
                assert 'env' in call_kwargs
                env = call_kwargs['env']
                assert env['TEST_VAR'] == 'test_value'
                # Should also include original environment variables
                assert 'PATH' in env or 'HOME' in env
    
    def test_edit_files_exit_code_non_zero(self):
        """Test edit_files when subprocess returns non-zero exit code"""
        editor = Editor()
        mock_popen = Mock()
        mock_popen.wait.return_value = 1
        
        with patch.object(editor, 'get_editor', return_value='vim'):
            with patch('subprocess.Popen', return_value=mock_popen):
                with pytest.raises(ClickException) as exc_info:
                    editor.edit_files(['test.txt'])
                
                assert "vim: Editing failed" in str(exc_info.value)
    
    def test_edit_files_os_error(self):
        """Test edit_files when subprocess.Popen raises OSError"""
        editor = Editor()
        
        with patch.object(editor, 'get_editor', return_value='vim'):
            with patch('subprocess.Popen', side_effect=OSError("File not found")):
                with pytest.raises(ClickException) as exc_info:
                    editor.edit_files(['test.txt'])
                
                assert "vim: Editing failed: File not found" in str(exc_info.value)
                # Verify the exception is chained
                assert exc_info.value.__cause__ is not None
                assert isinstance(exc_info.value.__cause__, OSError)
