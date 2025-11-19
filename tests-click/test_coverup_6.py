# file: src/click/src/click/_compat.py:371-449
# asked: {"lines": [371, 373, 374, 375, 376, 378, 379, 383, 384, 385, 386, 387, 388, 389, 390, 393, 394, 397, 398, 399, 404, 405, 406, 407, 413, 414, 416, 417, 418, 419, 421, 423, 424, 426, 427, 428, 429, 431, 432, 433, 434, 435, 436, 437, 438, 439, 441, 442, 444, 445, 447, 448, 449], "branches": [[383, 384], [383, 393], [384, 385], [384, 388], [385, 386], [385, 387], [388, 389], [388, 390], [393, 394], [393, 397], [397, 398], [397, 404], [404, 405], [404, 406], [406, 407], [406, 413], [423, 424], [423, 426], [426, 427], [435, 441], [435, 442], [444, 445], [444, 447]]}
# gained: {"lines": [371, 373, 374, 375, 376, 378, 379, 383, 384, 385, 386, 387, 388, 389, 390, 393, 394, 397, 398, 399, 404, 405, 406, 407, 413, 414, 416, 417, 418, 419, 421, 423, 424, 426, 427, 428, 429, 431, 432, 433, 434, 435, 436, 437, 438, 439, 441, 442, 444, 445, 447, 448, 449], "branches": [[383, 384], [383, 393], [384, 385], [384, 388], [385, 386], [385, 387], [388, 389], [388, 390], [393, 394], [393, 397], [397, 398], [397, 404], [404, 405], [404, 406], [406, 407], [406, 413], [423, 424], [423, 426], [426, 427], [435, 441], [435, 442], [444, 445], [444, 447]]}

import pytest
import os
import tempfile
import typing as t
from unittest.mock import patch, MagicMock
from click._compat import open_stream, _AtomicFile

def test_open_stream_stdin_binary():
    """Test opening stdin in binary mode."""
    stream, should_close = open_stream("-", "rb")
    assert not should_close
    assert hasattr(stream, "read")

def test_open_stream_stdin_text():
    """Test opening stdin in text mode with encoding."""
    stream, should_close = open_stream("-", "r", encoding="utf-8")
    assert not should_close
    assert hasattr(stream, "read")

def test_open_stream_stdout_binary():
    """Test opening stdout in binary mode."""
    stream, should_close = open_stream("-", "wb")
    assert not should_close
    assert hasattr(stream, "write")

def test_open_stream_stdout_text():
    """Test opening stdout in text mode with encoding."""
    stream, should_close = open_stream("-", "w", encoding="utf-8")
    assert not should_close
    assert hasattr(stream, "write")

def test_open_stream_non_atomic():
    """Test opening a regular file in non-atomic mode."""
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp_path = tmp.name
    try:
        stream, should_close = open_stream(tmp_path, "w", atomic=False)
        assert should_close
        stream.write("test")
        stream.close()
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)

def test_open_stream_atomic_append_raises():
    """Test that atomic mode with append raises ValueError."""
    with pytest.raises(ValueError, match="Appending to an existing file is not supported"):
        open_stream("test.txt", "a", atomic=True)

def test_open_stream_atomic_exclusive_raises():
    """Test that atomic mode with exclusive create raises ValueError."""
    with pytest.raises(ValueError, match="Use the `overwrite`-parameter instead"):
        open_stream("test.txt", "x", atomic=True)

def test_open_stream_atomic_invalid_mode_raises():
    """Test that atomic mode with invalid mode raises ValueError."""
    with pytest.raises(ValueError, match="Atomic writes only make sense with `w`-mode"):
        open_stream("test.txt", "r", atomic=True)

def test_open_stream_atomic_success():
    """Test successful atomic file creation."""
    with tempfile.TemporaryDirectory() as tmpdir:
        filename = os.path.join(tmpdir, "test.txt")
        stream, should_close = open_stream(filename, "w", atomic=True)
        assert should_close
        assert isinstance(stream, _AtomicFile)
        stream.write("test content")
        stream.close()
        assert os.path.exists(filename)
        with open(filename, "r") as f:
            assert f.read() == "test content"

def test_open_stream_atomic_binary():
    """Test atomic file creation in binary mode."""
    with tempfile.TemporaryDirectory() as tmpdir:
        filename = os.path.join(tmpdir, "test.bin")
        stream, should_close = open_stream(filename, "wb", atomic=True)
        assert should_close
        assert isinstance(stream, _AtomicFile)
        stream.write(b"binary content")
        stream.close()
        assert os.path.exists(filename)
        with open(filename, "rb") as f:
            assert f.read() == b"binary content"

def test_open_stream_atomic_with_existing_permissions():
    """Test atomic write when target file exists and has permissions."""
    with tempfile.TemporaryDirectory() as tmpdir:
        filename = os.path.join(tmpdir, "existing.txt")
        # Create file with specific permissions
        with open(filename, "w") as f:
            f.write("existing content")
        original_perm = os.stat(filename).st_mode
        
        stream, should_close = open_stream(filename, "w", atomic=True)
        assert should_close
        stream.write("new content")
        stream.close()
        
        # Check file was replaced and permissions preserved
        assert os.path.exists(filename)
        with open(filename, "r") as f:
            assert f.read() == "new content"
        new_perm = os.stat(filename).st_mode
        assert new_perm == original_perm

def test_open_stream_atomic_temp_file_collision_retry():
    """Test atomic write retry when temporary filename collision occurs."""
    with tempfile.TemporaryDirectory() as tmpdir:
        filename = os.path.join(tmpdir, "test.txt")
        
        # Mock os.open to simulate EEXIST error first, then succeed
        original_os_open = os.open
        call_count = 0
        
        def mock_os_open(path, flags, mode):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise OSError(17, "File exists")  # EEXIST
            return original_os_open(path, flags, mode)
        
        with patch('os.open', mock_os_open):
            stream, should_close = open_stream(filename, "w", atomic=True)
            assert should_close
            stream.write("test")
            stream.close()
            assert call_count == 2
            assert os.path.exists(filename)

def test_open_stream_atomic_windows_access_error_retry():
    """Test atomic write retry on Windows EACCES error for directories."""
    with tempfile.TemporaryDirectory() as tmpdir:
        filename = os.path.join(tmpdir, "test.txt")
        
        # Mock os.open to simulate Windows EACCES error first, then succeed
        original_os_open = os.open
        call_count = 0
        
        def mock_os_open(path, flags, mode):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                error = OSError(13, "Permission denied")  # EACCES
                error.filename = tmpdir  # Simulate Windows behavior
                raise error
            return original_os_open(path, flags, mode)
        
        with patch('os.name', 'nt'):
            with patch('os.path.isdir', return_value=True):
                with patch('os.access', return_value=True):
                    with patch('os.open', mock_os_open):
                        stream, should_close = open_stream(filename, "w", atomic=True)
                        assert should_close
                        stream.write("test")
                        stream.close()
                        assert call_count == 2
                        assert os.path.exists(filename)

def test_open_stream_atomic_os_error_propagation():
    """Test that non-retryable OSErrors are propagated."""
    with tempfile.TemporaryDirectory() as tmpdir:
        filename = os.path.join(tmpdir, "test.txt")
        
        # Mock os.open to raise a non-retryable error
        def mock_os_open(path, flags, mode):
            raise OSError(2, "No such file or directory")  # ENOENT
        
        with patch('os.open', mock_os_open):
            with pytest.raises(OSError, match="No such file or directory"):
                open_stream(filename, "w", atomic=True)
