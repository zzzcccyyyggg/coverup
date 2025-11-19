# file: src/click/src/click/decorators.py:268-273
# asked: {"lines": [268, 269, 273], "branches": []}
# gained: {"lines": [268, 269], "branches": []}

import pytest
import typing as t
from click.decorators import group
from click.core import Group

def test_group_overload_with_cls_parameter():
    """Test the group decorator overload with explicit cls parameter."""
    
    # Create a custom group class
    class CustomGroup(Group):
        pass
    
    # Test the overload signature by calling group with cls parameter
    @group("test_group", cls=CustomGroup)
    def test_command():
        pass
    
    # Verify the decorator returns a Group instance
    assert isinstance(test_command, CustomGroup)
    assert test_command.name == "test_group"
