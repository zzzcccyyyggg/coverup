# file: src/click/src/click/core.py:3367-3382
# asked: {"lines": [3367, 3370, 3371, 3372, 3373, 3374, 3375, 3376, 3378, 3379, 3380, 3382], "branches": [[3370, 3371], [3370, 3374], [3371, 3372], [3371, 3373], [3374, 3375], [3374, 3378]]}
# gained: {"lines": [3367, 3370, 3371, 3372, 3373, 3374, 3375, 3376, 3378, 3379, 3380, 3382], "branches": [[3370, 3371], [3370, 3374], [3371, 3372], [3371, 3373], [3374, 3375], [3374, 3378]]}

import pytest
from click.core import Argument
import collections.abc as cabc


class TestArgumentParseDecls:
    """Test cases for Argument._parse_decls method to achieve full coverage."""
    
    def test_parse_decls_empty_decls_no_expose_value(self):
        """Test when decls is empty and expose_value is False."""
        # Create an Argument instance with a valid name first
        arg = Argument(["dummy"])
        # Then directly test the _parse_decls method with empty decls and expose_value=False
        result = arg._parse_decls([], False)
        expected = (None, [], [])
        assert result == expected
    
    def test_parse_decls_empty_decls_with_expose_value(self):
        """Test when decls is empty and expose_value is True - should raise TypeError."""
        # Create an Argument instance with a valid name first
        arg = Argument(["dummy"])
        # Then directly test the _parse_decls method with empty decls and expose_value=True
        with pytest.raises(TypeError, match="Argument is marked as exposed, but does not have a name."):
            arg._parse_decls([], True)
    
    def test_parse_decls_single_decl(self):
        """Test when decls has exactly one element."""
        arg = Argument(["test_arg"])
        # The _parse_decls method is called during initialization, so we can check the result
        assert arg.name == "test_arg"
        assert arg.opts == ["test_arg"]
        assert arg.secondary_opts == []
    
    def test_parse_decls_single_decl_with_dashes(self):
        """Test when decls has one element with dashes that get normalized."""
        arg = Argument(["test-arg"])
        # The _parse_decls method is called during initialization, so we can check the result
        assert arg.name == "test_arg"
        assert arg.opts == ["test-arg"]
        assert arg.secondary_opts == []
    
    def test_parse_decls_multiple_decls(self):
        """Test when decls has more than one element - should raise TypeError."""
        with pytest.raises(TypeError, match="Arguments take exactly one parameter declaration, got 2: \\['arg1', 'arg2'\\]."):
            Argument(["arg1", "arg2"])
