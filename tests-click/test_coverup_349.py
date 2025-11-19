# file: src/click/src/click/core.py:2604-2605
# asked: {"lines": [2604, 2605], "branches": []}
# gained: {"lines": [2604, 2605], "branches": []}

import pytest
from click.core import Context, Parameter, Command

class TestParameterGetHelpRecord:
    def test_get_help_record_returns_none(self):
        """Test that Parameter.get_help_record returns None by default."""
        cmd = Command('test')
        ctx = Context(cmd)
        
        # Create a minimal Parameter subclass that doesn't require param_decls
        class MinimalParameter(Parameter):
            def _parse_decls(self, decls, expose_value):
                return None, [], []
        
        param = MinimalParameter()
        result = param.get_help_record(ctx)
        assert result is None
