# file: src/flask/src/flask/cli.py:691-695
# asked: {"lines": [691, 695], "branches": []}
# gained: {"lines": [691, 695], "branches": []}

import os
import pytest


def test_path_is_ancestor_child_directory():
    """Test when other is a child directory of path."""
    path = "/home/user"
    other = "/home/user/documents"
    from flask.cli import _path_is_ancestor
    assert _path_is_ancestor(path, other) == True


def test_path_is_ancestor_child_with_trailing_separator():
    """Test when other is a child directory and path has trailing separator."""
    path = "/home/user/"
    other = "/home/user/documents"
    from flask.cli import _path_is_ancestor
    assert _path_is_ancestor(path, other) == True


def test_path_is_ancestor_not_ancestor():
    """Test when path is not an ancestor of other."""
    path = "/home/user"
    other = "/home/other"
    from flask.cli import _path_is_ancestor
    assert _path_is_ancestor(path, other) == False


def test_path_is_ancestor_sibling_directory():
    """Test when other is a sibling directory."""
    path = "/home/user"
    other = "/home/other"
    from flask.cli import _path_is_ancestor
    assert _path_is_ancestor(path, other) == False


def test_path_is_ancestor_parent_directory():
    """Test when other is actually a parent of path."""
    path = "/home/user/documents"
    other = "/home/user"
    from flask.cli import _path_is_ancestor
    assert _path_is_ancestor(path, other) == False


def test_path_is_ancestor_empty_strings():
    """Test with empty strings."""
    path = ""
    other = ""
    from flask.cli import _path_is_ancestor
    assert _path_is_ancestor(path, other) == True


def test_path_is_ancestor_root_path():
    """Test with root path."""
    path = "/"
    other = "/home"
    from flask.cli import _path_is_ancestor
    assert _path_is_ancestor(path, other) == True


def test_path_is_ancestor_root_with_child():
    """Test with root path and child directory."""
    path = "/"
    other = "/home/user"
    from flask.cli import _path_is_ancestor
    assert _path_is_ancestor(path, other) == True


def test_path_is_ancestor_different_drive_windows():
    """Test with different drives on Windows (should return False)."""
    path = "C:\\Users"
    other = "D:\\Users"
    from flask.cli import _path_is_ancestor
    assert _path_is_ancestor(path, other) == False


def test_path_is_ancestor_child_with_leading_separator():
    """Test when other is a child directory and has leading separator in the suffix."""
    path = "/home/user"
    other = "/home/user/documents"
    from flask.cli import _path_is_ancestor
    assert _path_is_ancestor(path, other) == True


def test_path_is_ancestor_child_without_leading_separator():
    """Test when other is a child directory without leading separator in the suffix."""
    path = "/home/user"
    other = "/home/user/documents"
    from flask.cli import _path_is_ancestor
    assert _path_is_ancestor(path, other) == True


def test_path_is_ancestor_same_path_with_trailing_separator():
    """Test when path and other are the same but with trailing separator."""
    path = "/home/user/"
    other = "/home/user/"
    from flask.cli import _path_is_ancestor
    assert _path_is_ancestor(path, other) == True
