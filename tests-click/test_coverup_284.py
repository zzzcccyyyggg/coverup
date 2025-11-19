# file: src/click/src/click/_termui_impl.py:120-126
# asked: {"lines": [120, 126], "branches": []}
# gained: {"lines": [120, 126], "branches": []}

import pytest
from click._termui_impl import ProgressBar
from io import StringIO
from unittest.mock import patch

class TestProgressBarExit:
    def test_exit_calls_render_finish(self):
        """Test that __exit__ method calls render_finish"""
        file = StringIO()
        progress_bar = ProgressBar(range(5), file=file)
        
        # Enter the context manager first
        progress_bar.__enter__()
        
        # Mock render_finish to track if it's called
        with patch.object(progress_bar, 'render_finish') as mock_render_finish:
            # Call __exit__ with no exception
            progress_bar.__exit__(None, None, None)
            
            # Verify render_finish was called
            mock_render_finish.assert_called_once()

    def test_exit_with_exception_calls_render_finish(self):
        """Test that __exit__ method calls render_finish even when there's an exception"""
        file = StringIO()
        progress_bar = ProgressBar(range(5), file=file)
        
        # Enter the context manager first
        progress_bar.__enter__()
        
        # Mock render_finish to track if it's called
        with patch.object(progress_bar, 'render_finish') as mock_render_finish:
            # Call __exit__ with an exception
            exc_type = ValueError
            exc_value = ValueError("test error")
            tb = None
            
            progress_bar.__exit__(exc_type, exc_value, tb)
            
            # Verify render_finish was called regardless of exception
            mock_render_finish.assert_called_once()

    def test_exit_context_manager_usage(self):
        """Test using ProgressBar as a context manager calls render_finish on exit"""
        file = StringIO()
        
        with patch('click._termui_impl.ProgressBar.render_finish') as mock_render_finish:
            with ProgressBar(range(3), file=file) as bar:
                # Do some iteration
                for _ in bar:
                    pass
            
            # Verify render_finish was called when exiting the context
            mock_render_finish.assert_called_once()
