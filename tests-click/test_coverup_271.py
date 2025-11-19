# file: src/click/src/click/decorators.py:287-290
# asked: {"lines": [287, 288, 289, 290], "branches": []}
# gained: {"lines": [287, 288, 289], "branches": []}

import pytest
import typing as t
from click.decorators import group
from click.core import Group

def test_group_overload_with_name_and_no_cls():
    """Test the @t.overload for group with name parameter and no cls parameter."""
    # This test exercises the overload at lines 287-290
    # The overload is just a type hint, so we need to test the actual implementation
    # by calling group() with the signature that matches this overload
    
    # Test the case where name is provided as a string and cls is None
    @group("test_group", cls=None)
    def test_func():
        pass
    
    # Verify that the decorator returns a Group instance
    assert isinstance(test_func, Group)
    assert test_func.name == "test_group"

def test_group_overload_with_name_string_and_no_cls():
    """Test group decorator with string name and no cls parameter."""
    # This should use the overload at lines 287-290
    @group("mygroup")
    def my_func():
        pass
    
    assert isinstance(my_func, Group)
    assert my_func.name == "mygroup"

def test_group_overload_with_none_name_and_no_cls():
    """Test group decorator with None name and no cls parameter."""
    # This should also use the overload at lines 287-290
    # When name is None, Click automatically uses the function name
    @group(None)
    def my_func():
        pass
    
    assert isinstance(my_func, Group)
    # When name is None, Click uses the function name as the command name
    assert my_func.name == "my-func"

def test_group_overload_with_name_and_attrs():
    """Test group decorator with name and additional attributes."""
    # This should use the overload at lines 287-290
    @group("testgroup", help="A test group")
    def my_func():
        pass
    
    assert isinstance(my_func, Group)
    assert my_func.name == "testgroup"
    assert my_func.help == "A test group"
