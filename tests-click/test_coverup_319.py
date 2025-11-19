# file: src/click/src/click/core.py:2222-2225
# asked: {"lines": [2222, 2225], "branches": []}
# gained: {"lines": [2222, 2225], "branches": []}

import pytest
from click.core import Parameter

class TestParameterParseDecls:
    def test_parse_decls_not_implemented(self):
        """Test that _parse_decls raises NotImplementedError."""
        param = Parameter.__new__(Parameter)
        with pytest.raises(NotImplementedError):
            param._parse_decls([], True)
