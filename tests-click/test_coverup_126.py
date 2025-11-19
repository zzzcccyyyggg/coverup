# file: src/click/src/click/testing.py:59-66
# asked: {"lines": [59, 60, 61, 62, 64, 65, 66], "branches": [[61, 62], [61, 64]]}
# gained: {"lines": [59, 60, 61, 62, 64, 65, 66], "branches": [[61, 62], [61, 64]]}

import pytest
import io
from click.testing import EchoingStdin, _pause_echo

def test_pause_echo_with_stream():
    """Test _pause_echo context manager with an EchoingStdin stream."""
    input_stream = io.BytesIO(b"test input")
    output_stream = io.BytesIO()
    stream = EchoingStdin(input_stream, output_stream)
    
    # Verify initial state
    assert not stream._paused
    
    # Use the context manager
    with _pause_echo(stream):
        # Inside context, _paused should be True
        assert stream._paused
    
    # After context, _paused should be False again
    assert not stream._paused

def test_pause_echo_with_none():
    """Test _pause_echo context manager with None stream."""
    # This should not raise any exceptions and execute normally
    with _pause_echo(None):
        pass
    # No assertions needed for None case, just ensure it doesn't crash
