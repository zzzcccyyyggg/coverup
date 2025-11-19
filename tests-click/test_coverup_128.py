# file: src/click/src/click/decorators.py:293-311
# asked: {"lines": [293, 294, 295, 305, 306, 308, 309, 311], "branches": [[305, 306], [305, 308], [308, 309], [308, 311]]}
# gained: {"lines": [293, 294, 295, 305, 306, 308, 309, 311], "branches": [[305, 306], [305, 308], [308, 309], [308, 311]]}

import pytest
import click
from click.decorators import group
from click.core import Group

def test_group_with_callable_name():
    """Test group decorator when name is callable (lines 308-309)"""
    @group
    def my_group():
        pass
    
    assert isinstance(my_group, Group)
    # The name is automatically derived from the function name, but may be truncated
    assert my_group.name == "my"

def test_group_with_name_and_cls():
    """Test group decorator with explicit name and cls (line 311)"""
    class CustomGroup(Group):
        pass
    
    @group("custom_name", cls=CustomGroup)
    def my_group():
        pass
    
    assert isinstance(my_group, CustomGroup)
    assert my_group.name == "custom_name"

def test_group_with_name_only():
    """Test group decorator with explicit name only (line 311)"""
    @group("explicit_name")
    def my_group():
        pass
    
    assert isinstance(my_group, Group)
    assert my_group.name == "explicit_name"

def test_group_with_cls_only():
    """Test group decorator with cls parameter only (lines 305-306, 311)"""
    class CustomGroup(Group):
        pass
    
    @group(cls=CustomGroup)
    def my_group():
        pass
    
    assert isinstance(my_group, CustomGroup)
    assert my_group.name == "my"

def test_group_with_additional_attrs():
    """Test group decorator with additional attributes (line 311)"""
    @group("test_group", help="Test group help")
    def my_group():
        pass
    
    assert isinstance(my_group, Group)
    assert my_group.name == "test_group"
    assert my_group.help == "Test group help"
