# file: src/click/src/click/_termui_impl.py:577-592
# asked: {"lines": [577, 578, 579, 580, 581, 582, 583, 584, 585, 587, 589, 590, 591, 592], "branches": [[578, 579], [578, 580], [580, 581], [580, 584], [582, 580], [582, 583], [584, 585], [584, 587], [589, 590], [589, 592], [590, 589], [590, 591]]}
# gained: {"lines": [577, 578, 579, 580, 581, 582, 583, 584, 585, 587, 589, 590, 591, 592], "branches": [[578, 579], [578, 580], [580, 581], [580, 584], [582, 580], [582, 583], [584, 585], [584, 587], [589, 590], [589, 592], [590, 589], [590, 591]]}

import os
import pytest
from unittest.mock import patch, MagicMock
from click._termui_impl import Editor
from click._compat import WIN


class TestEditorGetEditor:
    """Test cases for Editor.get_editor method to achieve full coverage."""
    
    def test_get_editor_with_explicit_editor(self):
        """Test when self.editor is explicitly set."""
        editor = Editor(editor="custom_editor")
        result = editor.get_editor()
        assert result == "custom_editor"
    
    def test_get_editor_with_visual_env_var(self):
        """Test when VISUAL environment variable is set."""
        with patch.dict(os.environ, {"VISUAL": "vim", "EDITOR": "nano"}):
            editor = Editor()
            result = editor.get_editor()
            assert result == "vim"
    
    def test_get_editor_with_editor_env_var(self):
        """Test when EDITOR environment variable is set (VISUAL not set)."""
        with patch.dict(os.environ, {"EDITOR": "emacs"}):
            editor = Editor()
            result = editor.get_editor()
            assert result == "emacs"
    
    def test_get_editor_windows_fallback(self):
        """Test Windows fallback to notepad."""
        with patch('click._termui_impl.WIN', True):
            with patch.dict(os.environ, clear=True):
                editor = Editor()
                result = editor.get_editor()
                assert result == "notepad"
    
    def test_get_editor_unix_sensible_editor_found(self):
        """Test Unix fallback when sensible-editor is found."""
        if WIN:
            pytest.skip("This test is for Unix systems")
        
        with patch.dict(os.environ, clear=True):
            with patch('click._termui_impl.WIN', False):
                with patch('shutil.which') as mock_which:
                    mock_which.side_effect = lambda x: x if x == "sensible-editor" else None
                    editor = Editor()
                    result = editor.get_editor()
                    assert result == "sensible-editor"
    
    def test_get_editor_unix_vim_found(self):
        """Test Unix fallback when vim is found (sensible-editor not found)."""
        if WIN:
            pytest.skip("This test is for Unix systems")
        
        with patch.dict(os.environ, clear=True):
            with patch('click._termui_impl.WIN', False):
                with patch('shutil.which') as mock_which:
                    mock_which.side_effect = lambda x: x if x == "vim" else None
                    editor = Editor()
                    result = editor.get_editor()
                    assert result == "vim"
    
    def test_get_editor_unix_nano_found(self):
        """Test Unix fallback when nano is found (sensible-editor and vim not found)."""
        if WIN:
            pytest.skip("This test is for Unix systems")
        
        with patch.dict(os.environ, clear=True):
            with patch('click._termui_impl.WIN', False):
                with patch('shutil.which') as mock_which:
                    mock_which.side_effect = lambda x: x if x == "nano" else None
                    editor = Editor()
                    result = editor.get_editor()
                    assert result == "nano"
    
    def test_get_editor_unix_final_fallback_to_vi(self):
        """Test Unix final fallback to vi when no editors are found."""
        if WIN:
            pytest.skip("This test is for Unix systems")
        
        with patch.dict(os.environ, clear=True):
            with patch('click._termui_impl.WIN', False):
                with patch('shutil.which', return_value=None):
                    editor = Editor()
                    result = editor.get_editor()
                    assert result == "vi"
