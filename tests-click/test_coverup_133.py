# file: src/click/src/click/globals.py:54-67
# asked: {"lines": [54, 59, 60, 62, 64, 65, 67], "branches": [[59, 60], [59, 62], [64, 65], [64, 67]]}
# gained: {"lines": [54, 59, 60, 62, 64, 65, 67], "branches": [[59, 60], [59, 62], [64, 65], [64, 67]]}

import pytest
import click
from click.globals import resolve_color_default, get_current_context


class TestResolveColorDefault:
    """Test cases for resolve_color_default function."""

    def test_resolve_color_default_with_color_provided(self):
        """Test when color parameter is explicitly provided."""
        # Test with True
        result = resolve_color_default(color=True)
        assert result is True
        
        # Test with False
        result = resolve_color_default(color=False)
        assert result is False
        
        # Test with None (explicitly provided)
        result = resolve_color_default(color=None)
        assert result is None

    def test_resolve_color_default_with_context_and_color(self, monkeypatch):
        """Test when no color provided but context exists with color set."""
        # Mock context with color=True
        mock_ctx = click.Context(click.Command('test'))
        mock_ctx.color = True
        monkeypatch.setattr('click.globals.get_current_context', lambda silent: mock_ctx)
        
        result = resolve_color_default()
        assert result is True

    def test_resolve_color_default_with_context_and_no_color(self, monkeypatch):
        """Test when no color provided but context exists without color set."""
        # Mock context with color=False
        mock_ctx = click.Context(click.Command('test'))
        mock_ctx.color = False
        monkeypatch.setattr('click.globals.get_current_context', lambda silent: mock_ctx)
        
        result = resolve_color_default()
        assert result is False

    def test_resolve_color_default_no_context(self, monkeypatch):
        """Test when no color provided and no context exists."""
        # Mock no context available
        monkeypatch.setattr('click.globals.get_current_context', lambda silent: None)
        
        result = resolve_color_default()
        assert result is None
