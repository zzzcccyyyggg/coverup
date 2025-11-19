# file: src/click/src/click/_compat.py:358-368
# asked: {"lines": [358, 365, 366, 368], "branches": [[365, 366], [365, 368]]}
# gained: {"lines": [358, 365, 366, 368], "branches": [[365, 366], [365, 368]]}

import pytest
import tempfile
import os
from click._compat import _wrap_io_open

def test_wrap_io_open_binary_mode():
    """Test _wrap_io_open with binary mode ('b' in mode)."""
    with tempfile.NamedTemporaryFile(mode='wb', delete=False) as tmp:
        tmp.write(b'test content')
        tmp_path = tmp.name
    
    try:
        # Test binary read mode
        with _wrap_io_open(tmp_path, 'rb', 'utf-8', 'strict') as f:
            content = f.read()
            assert content == b'test content'
        
        # Test binary write mode
        with _wrap_io_open(tmp_path, 'wb', 'utf-8', 'strict') as f:
            f.write(b'new content')
        
        # Verify the write worked
        with open(tmp_path, 'rb') as f:
            assert f.read() == b'new content'
            
    finally:
        os.unlink(tmp_path)

def test_wrap_io_open_text_mode():
    """Test _wrap_io_open with text mode (no 'b' in mode)."""
    with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False) as tmp:
        tmp.write('test content')
        tmp_path = tmp.name
    
    try:
        # Test text read mode with encoding and errors
        with _wrap_io_open(tmp_path, 'r', 'utf-8', 'strict') as f:
            content = f.read()
            assert content == 'test content'
        
        # Test text write mode with encoding and errors
        with _wrap_io_open(tmp_path, 'w', 'utf-8', 'strict') as f:
            f.write('new content')
        
        # Verify the write worked
        with open(tmp_path, 'r', encoding='utf-8') as f:
            assert f.read() == 'new content'
            
    finally:
        os.unlink(tmp_path)

def test_wrap_io_open_mixed_modes():
    """Test _wrap_io_open with various mode combinations."""
    with tempfile.NamedTemporaryFile(mode='wb', delete=False) as tmp:
        tmp.write(b'test content')
        tmp_path = tmp.name
    
    try:
        # Test various binary modes
        for mode in ['rb', 'wb', 'ab', 'rb+', 'wb+', 'ab+']:
            if 'r' in mode or '+' in mode:
                with _wrap_io_open(tmp_path, mode, 'utf-8', 'strict') as f:
                    if 'r' in mode:
                        _ = f.read()
                    if 'w' in mode or 'a' in mode:
                        f.write(b'content')
        
        # Create a text file for text mode tests
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False) as tmp_text:
            tmp_text.write('test content')
            tmp_text_path = tmp_text.name
        
        try:
            # Test various text modes
            for mode in ['r', 'w', 'a', 'r+', 'w+', 'a+']:
                with _wrap_io_open(tmp_text_path, mode, 'utf-8', 'strict') as f:
                    if 'r' in mode:
                        _ = f.read()
                    if 'w' in mode or 'a' in mode:
                        f.write('content')
        finally:
            os.unlink(tmp_text_path)
            
    finally:
        os.unlink(tmp_path)
