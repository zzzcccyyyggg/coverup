# file: src/click/src/click/termui.py:261-290
# asked: {"lines": [261, 263, 276, 278, 279, 280, 281, 283, 286, 288, 290], "branches": [[278, 279], [278, 280], [280, 281], [280, 283]]}
# gained: {"lines": [261, 263, 276, 278, 279, 280, 281, 283, 286, 288, 290], "branches": [[278, 279], [278, 280], [280, 281], [280, 283]]}

import pytest
from unittest.mock import Mock, patch
import click.termui
from click.termui import echo_via_pager
import inspect
import itertools
import collections.abc as cabc
import typing as t


class TestEchoViaPager:
    """Test cases for echo_via_pager function to achieve full coverage."""
    
    def test_echo_via_pager_with_generator_function(self, monkeypatch):
        """Test echo_via_pager with a generator function parameter."""
        mock_pager = Mock()
        monkeypatch.setattr('click._termui_impl.pager', mock_pager)
        
        def text_generator():
            yield "line 1"
            yield "line 2"
            yield "line 3"
        
        echo_via_pager(text_generator, color=True)
        
        # Verify pager was called with the expected generator
        assert mock_pager.called
        args = mock_pager.call_args[0]
        assert len(args) == 2
        generator_arg = args[0]
        color_arg = args[1]
        assert color_arg is True
        
        # Verify the generator produces the expected content
        generated_content = list(generator_arg)
        # The generator should include our text plus a newline at the end
        assert len(generated_content) == 4
        assert generated_content[:3] == ["line 1", "line 2", "line 3"]
        assert generated_content[3] == "\n"
    
    def test_echo_via_pager_with_string(self, monkeypatch):
        """Test echo_via_pager with a string parameter."""
        mock_pager = Mock()
        monkeypatch.setattr('click._termui_impl.pager', mock_pager)
        
        text = "Hello, World!"
        echo_via_pager(text, color=False)
        
        # Verify pager was called with the expected generator
        assert mock_pager.called
        args = mock_pager.call_args[0]
        assert len(args) == 2
        generator_arg = args[0]
        color_arg = args[1]
        assert color_arg is False
        
        # Verify the generator produces the expected content
        generated_content = list(generator_arg)
        assert len(generated_content) == 2
        assert generated_content[0] == "Hello, World!"
        assert generated_content[1] == "\n"
    
    def test_echo_via_pager_with_iterable(self, monkeypatch):
        """Test echo_via_pager with an iterable parameter."""
        mock_pager = Mock()
        monkeypatch.setattr('click._termui_impl.pager', mock_pager)
        
        text_list = ["first", "second", "third"]
        echo_via_pager(text_list, color=None)
        
        # Verify pager was called with the expected generator
        assert mock_pager.called
        args = mock_pager.call_args[0]
        assert len(args) == 2
        generator_arg = args[0]
        color_arg = args[1]
        assert color_arg is None
        
        # Verify the generator produces the expected content
        generated_content = list(generator_arg)
        assert len(generated_content) == 4
        assert generated_content[:3] == ["first", "second", "third"]
        assert generated_content[3] == "\n"
    
    def test_echo_via_pager_with_non_string_iterable(self, monkeypatch):
        """Test echo_via_pager with an iterable containing non-string elements."""
        mock_pager = Mock()
        monkeypatch.setattr('click._termui_impl.pager', mock_pager)
        
        # Create an iterable with mixed types that will be converted to strings
        mixed_iterable = [123, 45.67, True, "text"]
        echo_via_pager(mixed_iterable, color=True)
        
        # Verify pager was called with the expected generator
        assert mock_pager.called
        args = mock_pager.call_args[0]
        generator_arg = args[0]
        
        # Verify the generator converts non-string elements to strings
        generated_content = list(generator_arg)
        assert len(generated_content) == 5
        assert generated_content[0] == "123"
        assert generated_content[1] == "45.67"
        assert generated_content[2] == "True"
        assert generated_content[3] == "text"
        assert generated_content[4] == "\n"
    
    def test_echo_via_pager_resolve_color_default_called(self, monkeypatch):
        """Test that resolve_color_default is called with the correct parameter."""
        mock_resolve_color = Mock(return_value=True)
        mock_pager = Mock()
        monkeypatch.setattr('click.termui.resolve_color_default', mock_resolve_color)
        monkeypatch.setattr('click._termui_impl.pager', mock_pager)
        
        echo_via_pager("test", color=False)
        
        # Verify resolve_color_default was called with the provided color parameter
        mock_resolve_color.assert_called_once_with(False)
        
        # Verify pager was called with the resolved color value
        mock_pager.assert_called_once()
        args = mock_pager.call_args[0]
        assert args[1] is True  # The resolved color value from our mock
