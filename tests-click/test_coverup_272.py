# file: src/click/src/click/decorators.py:277-283
# asked: {"lines": [277, 278, 279, 283], "branches": []}
# gained: {"lines": [277, 278, 279], "branches": []}

import pytest
import click
from click.decorators import group
from click.core import Group

class CustomGroup(Group):
    """A custom group class for testing."""
    pass

def test_group_overload_with_none_name_and_custom_cls():
    """Test the @group overload with name=None and custom cls parameter."""
    
    # This should call the overload: group(name=None, *, cls=CustomGroup, **attrs) -> Callable[[AnyCallable], CustomGroup]
    @group(name=None, cls=CustomGroup, help="Test custom group")
    def test_group():
        """Test group function."""
        pass
    
    # Verify the decorator returns a CustomGroup instance
    assert isinstance(test_group, CustomGroup)
    # The name should be derived from the function name, but without "_group" suffix
    assert test_group.name == "test"
    assert test_group.help == "Test custom group"

def test_group_overload_with_none_name_and_custom_cls_with_attrs():
    """Test the @group overload with name=None, custom cls, and additional attributes."""
    
    # Test with various attributes
    @group(name=None, cls=CustomGroup, help="Help text", epilog="Epilog text", short_help="Short help")
    def another_group():
        """Another test group."""
        pass
    
    # Verify the decorator returns a CustomGroup instance with all attributes
    assert isinstance(another_group, CustomGroup)
    # The name should be derived from the function name, but without "_group" suffix
    assert another_group.name == "another"
    assert another_group.help == "Help text"
    assert another_group.epilog == "Epilog text"
    assert another_group.short_help == "Short help"

def test_group_overload_with_none_name_and_custom_cls_no_attrs():
    """Test the @group overload with name=None and custom cls but no additional attributes."""
    
    # Test with minimal parameters
    @group(name=None, cls=CustomGroup)
    def minimal_group():
        """Minimal test group."""
        pass
    
    # Verify the decorator returns a CustomGroup instance
    assert isinstance(minimal_group, CustomGroup)
    # The name should be derived from the function name, but without "_group" suffix
    assert minimal_group.name == "minimal"
