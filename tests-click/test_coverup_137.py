# file: src/click/src/click/_termui_impl.py:565-575
# asked: {"lines": [565, 567, 568, 569, 570, 572, 573, 574, 575], "branches": []}
# gained: {"lines": [565, 567, 568, 569, 570, 572, 573, 574, 575], "branches": []}

import pytest
import collections.abc as cabc
from click._termui_impl import Editor


class TestEditorInit:
    """Test cases for Editor.__init__ method to achieve full coverage."""
    
    def test_editor_init_with_defaults(self):
        """Test Editor initialization with all default parameters."""
        editor = Editor()
        assert editor.editor is None
        assert editor.env is None
        assert editor.require_save is True
        assert editor.extension == ".txt"
    
    def test_editor_init_with_custom_editor(self):
        """Test Editor initialization with custom editor parameter."""
        custom_editor = "vim"
        editor = Editor(editor=custom_editor)
        assert editor.editor == custom_editor
        assert editor.env is None
        assert editor.require_save is True
        assert editor.extension == ".txt"
    
    def test_editor_init_with_custom_env(self):
        """Test Editor initialization with custom environment mapping."""
        custom_env = {"EDITOR": "nano", "VISUAL": "vim"}
        editor = Editor(env=custom_env)
        assert editor.editor is None
        assert editor.env == custom_env
        assert editor.require_save is True
        assert editor.extension == ".txt"
    
    def test_editor_init_with_require_save_false(self):
        """Test Editor initialization with require_save set to False."""
        editor = Editor(require_save=False)
        assert editor.editor is None
        assert editor.env is None
        assert editor.require_save is False
        assert editor.extension == ".txt"
    
    def test_editor_init_with_custom_extension(self):
        """Test Editor initialization with custom file extension."""
        custom_extension = ".py"
        editor = Editor(extension=custom_extension)
        assert editor.editor is None
        assert editor.env is None
        assert editor.require_save is True
        assert editor.extension == custom_extension
    
    def test_editor_init_with_all_custom_params(self):
        """Test Editor initialization with all custom parameters."""
        custom_editor = "emacs"
        custom_env = {"EDITOR": "code", "TERM": "xterm-256color"}
        custom_extension = ".md"
        
        editor = Editor(
            editor=custom_editor,
            env=custom_env,
            require_save=False,
            extension=custom_extension
        )
        
        assert editor.editor == custom_editor
        assert editor.env == custom_env
        assert editor.require_save is False
        assert editor.extension == custom_extension
