# file: src/click/src/click/core.py:443-453
# asked: {"lines": [443, 444, 445, 447, 448, 450, 451, 453], "branches": []}
# gained: {"lines": [443, 444, 445, 447, 448, 450, 451, 453], "branches": []}

import pytest
import warnings
from click.core import Context
from click import Command

class TestContextProtectedArgs:
    def test_protected_args_property_emits_deprecation_warning(self):
        """Test that accessing protected_args property emits DeprecationWarning."""
        # Create a minimal command for context
        cmd = Command('test_cmd')
        ctx = Context(cmd)
        
        # Set some protected args to test the return value
        ctx._protected_args = ['arg1', 'arg2']
        
        # Capture warnings
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            
            # Access the protected_args property
            result = ctx.protected_args
            
            # Verify the warning was issued
            assert len(w) == 1
            assert issubclass(w[0].category, DeprecationWarning)
            assert "'protected_args' is deprecated" in str(w[0].message)
            assert "Click 9.0" in str(w[0].message)
            assert "'args' will contain remaining unparsed tokens" in str(w[0].message)
            
            # Verify the return value
            assert result == ['arg1', 'arg2']
