# file: src/click/src/click/testing.py:25-56
# asked: {"lines": [25, 26, 27, 28, 29, 31, 32, 34, 35, 36, 38, 40, 41, 43, 44, 46, 47, 49, 50, 52, 53, 55, 56], "branches": [[35, 36], [35, 38]]}
# gained: {"lines": [25, 26, 27, 28, 29, 31, 32, 34, 35, 36, 38, 40, 41, 43, 44, 46, 47, 49, 50, 52, 53, 55, 56], "branches": [[35, 36], [35, 38]]}

import io
import pytest
from click.testing import EchoingStdin


class TestEchoingStdin:
    def test_init(self):
        """Test EchoingStdin initialization."""
        input_stream = io.BytesIO(b"test")
        output_stream = io.BytesIO()
        stdin = EchoingStdin(input_stream, output_stream)
        
        assert stdin._input is input_stream
        assert stdin._output is output_stream
        assert stdin._paused is False

    def test_getattr_delegates_to_input(self):
        """Test __getattr__ delegates to underlying input stream."""
        input_stream = io.BytesIO(b"test")
        output_stream = io.BytesIO()
        stdin = EchoingStdin(input_stream, output_stream)
        
        # Test that getattr works for attributes from input stream
        assert stdin.closed == input_stream.closed
        # BytesIO doesn't have 'name' attribute, test with 'readable' instead
        assert stdin.readable == input_stream.readable

    def test_echo_writes_to_output_when_not_paused(self):
        """Test _echo writes to output when not paused."""
        input_stream = io.BytesIO(b"test")
        output_stream = io.BytesIO()
        stdin = EchoingStdin(input_stream, output_stream)
        
        result = stdin._echo(b"hello")
        
        assert result == b"hello"
        assert output_stream.getvalue() == b"hello"

    def test_echo_does_not_write_when_paused(self):
        """Test _echo does not write to output when paused."""
        input_stream = io.BytesIO(b"test")
        output_stream = io.BytesIO()
        stdin = EchoingStdin(input_stream, output_stream)
        stdin._paused = True
        
        result = stdin._echo(b"hello")
        
        assert result == b"hello"
        assert output_stream.getvalue() == b""

    def test_read_with_echo(self):
        """Test read method echoes content."""
        input_stream = io.BytesIO(b"hello world")
        output_stream = io.BytesIO()
        stdin = EchoingStdin(input_stream, output_stream)
        
        result = stdin.read(5)
        
        assert result == b"hello"
        assert output_stream.getvalue() == b"hello"

    def test_read1_with_echo(self):
        """Test read1 method echoes content."""
        input_stream = io.BytesIO(b"hello world")
        output_stream = io.BytesIO()
        stdin = EchoingStdin(input_stream, output_stream)
        
        result = stdin.read1(5)
        
        assert result == b"hello"
        assert output_stream.getvalue() == b"hello"

    def test_readline_with_echo(self):
        """Test readline method echoes content."""
        input_stream = io.BytesIO(b"hello\nworld\n")
        output_stream = io.BytesIO()
        stdin = EchoingStdin(input_stream, output_stream)
        
        result = stdin.readline()
        
        assert result == b"hello\n"
        assert output_stream.getvalue() == b"hello\n"

    def test_readlines_with_echo(self):
        """Test readlines method echoes content."""
        input_stream = io.BytesIO(b"hello\nworld\n")
        output_stream = io.BytesIO()
        stdin = EchoingStdin(input_stream, output_stream)
        
        result = stdin.readlines()
        
        assert result == [b"hello\n", b"world\n"]
        assert output_stream.getvalue() == b"hello\nworld\n"

    def test_iter_with_echo(self):
        """Test __iter__ method echoes content."""
        input_stream = io.BytesIO(b"hello\nworld\n")
        output_stream = io.BytesIO()
        stdin = EchoingStdin(input_stream, output_stream)
        
        result = list(stdin)
        
        assert result == [b"hello\n", b"world\n"]
        assert output_stream.getvalue() == b"hello\nworld\n"

    def test_repr(self):
        """Test __repr__ method."""
        input_stream = io.BytesIO(b"test")
        output_stream = io.BytesIO()
        stdin = EchoingStdin(input_stream, output_stream)
        
        result = repr(stdin)
        
        assert result == repr(input_stream)
