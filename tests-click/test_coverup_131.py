# file: src/click/src/click/core.py:667-677
# asked: {"lines": [667, 669, 671, 672, 673, 675, 677], "branches": [[671, 672], [671, 677], [672, 673], [672, 675]]}
# gained: {"lines": [667, 669, 671, 672, 673, 675, 677], "branches": [[671, 672], [671, 677], [672, 673], [672, 675]]}

import pytest
from click.core import Context
from click import Command

class MockCommand(Command):
    def __init__(self, name):
        super().__init__(name)
        self.allow_extra_args = True
        self.allow_interspersed_args = True
        self.ignore_unknown_options = False

class TestObject:
    def __init__(self, value):
        self.value = value

class TestObject2:
    def __init__(self, value):
        self.value = value

def test_find_object_found_in_current_context():
    """Test that find_object returns the object when it's in the current context."""
    test_obj = TestObject("test_value")
    ctx = Context(MockCommand("test"), obj=test_obj)
    
    result = ctx.find_object(TestObject)
    assert result is test_obj
    assert result.value == "test_value"

def test_find_object_found_in_parent_context():
    """Test that find_object returns the object when it's in a parent context."""
    parent_obj = TestObject("parent_value")
    parent_ctx = Context(MockCommand("parent"), obj=parent_obj)
    
    child_ctx = Context(MockCommand("child"), parent=parent_ctx)
    
    result = child_ctx.find_object(TestObject)
    assert result is parent_obj
    assert result.value == "parent_value"

def test_find_object_found_in_grandparent_context():
    """Test that find_object returns the object when it's in a grandparent context."""
    grandparent_obj = TestObject("grandparent_value")
    grandparent_ctx = Context(MockCommand("grandparent"), obj=grandparent_obj)
    
    parent_ctx = Context(MockCommand("parent"), parent=grandparent_ctx)
    
    child_ctx = Context(MockCommand("child"), parent=parent_ctx)
    
    result = child_ctx.find_object(TestObject)
    assert result is grandparent_obj
    assert result.value == "grandparent_value"

def test_find_object_not_found():
    """Test that find_object returns None when the object type is not found in any context."""
    ctx = Context(MockCommand("test"), obj="not_a_test_object")
    
    result = ctx.find_object(TestObject)
    assert result is None

def test_find_object_empty_context_chain():
    """Test that find_object returns None when there are no contexts with the object type."""
    ctx = Context(MockCommand("test"))
    
    result = ctx.find_object(TestObject)
    assert result is None

def test_find_object_wrong_type_in_context():
    """Test that find_object returns None when the context has an object of different type."""
    wrong_obj = TestObject2("wrong_type")
    ctx = Context(MockCommand("test"), obj=wrong_obj)
    
    result = ctx.find_object(TestObject)
    assert result is None

def test_find_object_multiple_types_in_chain():
    """Test that find_object finds the closest object of the correct type."""
    grandparent_obj = TestObject("grandparent")
    grandparent_ctx = Context(MockCommand("grandparent"), obj=grandparent_obj)
    
    parent_obj = TestObject2("parent_wrong_type")
    parent_ctx = Context(MockCommand("parent"), parent=grandparent_ctx, obj=parent_obj)
    
    child_ctx = Context(MockCommand("child"), parent=parent_ctx)
    
    result = child_ctx.find_object(TestObject)
    assert result is grandparent_obj
    assert result.value == "grandparent"
