# file: src/click/src/click/types.py:163-168
# asked: {"lines": [163, 164, 166, 167, 168], "branches": []}
# gained: {"lines": [163, 164, 166, 167, 168], "branches": []}

import pytest
from click.types import CompositeParamType


class TestCompositeParamType:
    def test_arity_property_raises_not_implemented_error(self):
        """Test that accessing arity property raises NotImplementedError."""
        composite_type = CompositeParamType()
        
        with pytest.raises(NotImplementedError):
            _ = composite_type.arity
    
    def test_is_composite_attribute_is_true(self):
        """Test that is_composite attribute is set to True."""
        composite_type = CompositeParamType()
        assert composite_type.is_composite is True
