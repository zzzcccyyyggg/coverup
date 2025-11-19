# file: src/click/src/click/decorators.py:262-263
# asked: {"lines": [262, 263], "branches": []}
# gained: {"lines": [262, 263], "branches": []}

import pytest
import click
from click.decorators import group
from click.core import Group

def test_group_overload_with_callable():
    """Test the @t.overload for group with callable parameter."""
    
    @group
    def my_group():
        """A simple group function."""
        pass
    
    assert isinstance(my_group, Group)
    # The name is automatically derived from the function name, but may be truncated
    # Let's just verify it's a Group instance and has the expected callback
    assert my_group.callback is not None
    assert my_group.callback.__name__ == "my_group"
