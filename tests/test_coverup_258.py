# file: src/flask/src/flask/sessions.py:290-295
# asked: {"lines": [290, 295], "branches": []}
# gained: {"lines": [290, 295], "branches": []}

import pytest
import hashlib
import typing as t
from unittest.mock import patch

def test_lazy_sha1_basic_functionality():
    """Test that _lazy_sha1 returns a sha1 hash object with the provided string."""
    from flask.sessions import _lazy_sha1
    
    test_string = b"test_data"
    result = _lazy_sha1(test_string)
    
    assert isinstance(result, hashlib._hashlib.HASH)
    assert result.name == 'sha1'
    
    # Verify it produces the correct hash
    expected_hash = hashlib.sha1(test_string).hexdigest()
    assert result.hexdigest() == expected_hash

def test_lazy_sha1_empty_string():
    """Test _lazy_sha1 with empty bytes string (default parameter)."""
    from flask.sessions import _lazy_sha1
    
    result = _lazy_sha1()
    
    assert isinstance(result, hashlib._hashlib.HASH)
    assert result.name == 'sha1'
    
    # Verify empty string produces correct hash
    expected_hash = hashlib.sha1(b"").hexdigest()
    assert result.hexdigest() == expected_hash

def test_lazy_sha1_with_different_strings():
    """Test _lazy_sha1 with various byte strings."""
    from flask.sessions import _lazy_sha1
    
    test_cases = [
        b"hello",
        b"flask",
        b"12345",
        b"",
        b"a" * 100
    ]
    
    for test_string in test_cases:
        result = _lazy_sha1(test_string)
        expected = hashlib.sha1(test_string)
        
        assert result.hexdigest() == expected.hexdigest()
        assert result.digest() == expected.digest()

def test_lazy_sha1_hashlib_sha1_not_available(monkeypatch):
    """Test _lazy_sha1 when hashlib.sha1 is not available (simulating FIPS environment)."""
    from flask.sessions import _lazy_sha1
    
    def mock_sha1_raises(string=b""):
        raise ValueError("sha1 is not available")
    
    monkeypatch.setattr(hashlib, 'sha1', mock_sha1_raises)
    
    with pytest.raises(ValueError, match="sha1 is not available"):
        _lazy_sha1(b"test")
