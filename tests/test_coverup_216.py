# file: src/flask/src/flask/helpers.py:27-32
# asked: {"lines": [27, 31, 32], "branches": []}
# gained: {"lines": [27, 31, 32], "branches": []}

import os
import pytest


def test_get_debug_flag_true_when_set_to_1():
    """Test that get_debug_flag returns True when FLASK_DEBUG=1."""
    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setenv("FLASK_DEBUG", "1")
    from flask.helpers import get_debug_flag
    
    result = get_debug_flag()
    assert result is True
    monkeypatch.undo()


def test_get_debug_flag_false_when_set_to_0():
    """Test that get_debug_flag returns False when FLASK_DEBUG=0."""
    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setenv("FLASK_DEBUG", "0")
    from flask.helpers import get_debug_flag
    
    result = get_debug_flag()
    assert result is False
    monkeypatch.undo()


def test_get_debug_flag_false_when_set_to_false():
    """Test that get_debug_flag returns False when FLASK_DEBUG=false."""
    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setenv("FLASK_DEBUG", "false")
    from flask.helpers import get_debug_flag
    
    result = get_debug_flag()
    assert result is False
    monkeypatch.undo()


def test_get_debug_flag_false_when_set_to_no():
    """Test that get_debug_flag returns False when FLASK_DEBUG=no."""
    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setenv("FLASK_DEBUG", "no")
    from flask.helpers import get_debug_flag
    
    result = get_debug_flag()
    assert result is False
    monkeypatch.undo()


def test_get_debug_flag_false_when_not_set():
    """Test that get_debug_flag returns False when FLASK_DEBUG is not set."""
    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.delenv("FLASK_DEBUG", raising=False)
    from flask.helpers import get_debug_flag
    
    result = get_debug_flag()
    assert result is False
    monkeypatch.undo()
