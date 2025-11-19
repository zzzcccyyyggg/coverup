# file: src/click/src/click/core.py:679-686
# asked: {"lines": [679, 683, 684, 685, 686], "branches": [[684, 685], [684, 686]]}
# gained: {"lines": [679, 683, 684, 685, 686], "branches": [[684, 685], [684, 686]]}

import pytest
from click.core import Context
from click import Command

class TestContextEnsureObject:
    """Test cases for Context.ensure_object method to achieve full coverage."""
    
    def test_ensure_object_when_object_exists(self):
        """Test ensure_object when object of given type already exists in context chain."""
        # Create a mock object type
        class MockObj:
            pass
        
        # Create parent context with existing object
        parent_obj = MockObj()
        parent_ctx = Context(Command('parent'), obj=parent_obj)
        
        # Create child context - it inherits parent's obj due to Context.__init__ logic
        child_ctx = Context(Command('child'), parent=parent_ctx)
        
        # Call ensure_object - should return existing object from parent
        result = child_ctx.ensure_object(MockObj)
        
        # Verify the existing object is returned
        assert result is parent_obj
        # Verify child context obj is the inherited parent object (not None)
        assert child_ctx.obj is parent_obj
    
    def test_ensure_object_when_object_does_not_exist(self):
        """Test ensure_object when object of given type does not exist in context chain."""
        # Create a mock object type
        class MockObj:
            def __init__(self):
                self.value = "created"
        
        # Create context without any object
        ctx = Context(Command('test'))
        
        # Call ensure_object - should create new instance
        result = ctx.ensure_object(MockObj)
        
        # Verify new object is created and returned
        assert isinstance(result, MockObj)
        assert result.value == "created"
        # Verify context obj is set to the new object
        assert ctx.obj is result
    
    def test_ensure_object_with_custom_object_type(self):
        """Test ensure_object with a custom object type that has parameters."""
        # Create a custom object type with parameters
        class CustomObj:
            def __init__(self, name="default"):
                self.name = name
        
        # Create context without any object
        ctx = Context(Command('test'))
        
        # Call ensure_object - should create new instance
        result = ctx.ensure_object(CustomObj)
        
        # Verify new object is created with default parameters
        assert isinstance(result, CustomObj)
        assert result.name == "default"
        # Verify context obj is set to the new object
        assert ctx.obj is result
    
    def test_ensure_object_when_object_exists_in_grandparent(self):
        """Test ensure_object when object exists in grandparent context."""
        # Create a mock object type
        class MockObj:
            pass
        
        # Create grandparent context with existing object
        grandparent_obj = MockObj()
        grandparent_ctx = Context(Command('grandparent'), obj=grandparent_obj)
        
        # Create parent context (inherits grandparent's obj)
        parent_ctx = Context(Command('parent'), parent=grandparent_ctx)
        
        # Create child context (inherits parent's obj which is grandparent's obj)
        child_ctx = Context(Command('child'), parent=parent_ctx)
        
        # Call ensure_object - should return existing object from grandparent
        result = child_ctx.ensure_object(MockObj)
        
        # Verify the existing object is returned
        assert result is grandparent_obj
        # Verify child context obj is the inherited grandparent object
        assert child_ctx.obj is grandparent_obj
