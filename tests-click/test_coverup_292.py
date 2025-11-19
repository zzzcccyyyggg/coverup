# file: src/click/src/click/utils.py:181-182
# asked: {"lines": [181, 182], "branches": []}
# gained: {"lines": [181, 182], "branches": []}

import pytest
import click.utils

def test_lazyfile_context_manager():
    """Test that LazyFile can be used as a context manager and returns self in __enter__."""
    lazy_file = click.utils.LazyFile("test.txt", "w")
    with lazy_file as lf:
        assert lf is lazy_file
