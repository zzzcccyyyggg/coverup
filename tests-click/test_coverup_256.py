# file: src/click/src/click/core.py:1488-1493
# asked: {"lines": [1488, 1489, 1490, 1492, 1493], "branches": []}
# gained: {"lines": [1488, 1489, 1490, 1492, 1493], "branches": []}

import pytest
import typing as t
from click.core import _FakeSubclassCheck


class TestFakeSubclassCheck:
    """Test cases for _FakeSubclassCheck metaclass."""
    
    def test_subclasscheck_returns_true_for_valid_subclass(self):
        """Test __subclasscheck__ returns True when subclass is valid."""
        class BaseClass:
            pass
        
        class DerivedClass(BaseClass):
            pass
        
        # Create _FakeSubclassCheck with BaseClass as base
        FakeCheck = _FakeSubclassCheck("FakeCheck", (BaseClass,), {})
        
        # Verify subclass check works
        assert FakeCheck.__subclasscheck__(DerivedClass) is True
    
    def test_subclasscheck_returns_false_for_invalid_subclass(self):
        """Test __subclasscheck__ returns False when subclass is not valid."""
        class BaseClass:
            pass
        
        class UnrelatedClass:
            pass
        
        # Create _FakeSubclassCheck with BaseClass as base
        FakeCheck = _FakeSubclassCheck("FakeCheck", (BaseClass,), {})
        
        # Verify subclass check returns False for unrelated class
        assert FakeCheck.__subclasscheck__(UnrelatedClass) is False
    
    def test_instancecheck_returns_true_for_valid_instance(self):
        """Test __instancecheck__ returns True when instance is valid."""
        class BaseClass:
            pass
        
        # Create _FakeSubclassCheck with BaseClass as base
        FakeCheck = _FakeSubclassCheck("FakeCheck", (BaseClass,), {})
        
        # Create instance of BaseClass
        instance = BaseClass()
        
        # Verify instance check works
        assert FakeCheck.__instancecheck__(instance) is True
    
    def test_instancecheck_returns_false_for_invalid_instance(self):
        """Test __instancecheck__ returns False when instance is not valid."""
        class BaseClass:
            pass
        
        class UnrelatedClass:
            pass
        
        # Create _FakeSubclassCheck with BaseClass as base
        FakeCheck = _FakeSubclassCheck("FakeCheck", (BaseClass,), {})
        
        # Create instance of unrelated class
        instance = UnrelatedClass()
        
        # Verify instance check returns False for unrelated instance
        assert FakeCheck.__instancecheck__(instance) is False
