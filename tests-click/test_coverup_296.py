# file: src/click/src/click/core.py:2227-2232
# asked: {"lines": [2227, 2228, 2232], "branches": []}
# gained: {"lines": [2227, 2228, 2232], "branches": []}

import pytest
import click
from click.core import Option, Argument


class TestParameterHumanReadableName:
    """Test cases for Parameter.human_readable_name property."""
    
    def test_option_human_readable_name_returns_name(self):
        """Test that Option.human_readable_name returns self.name."""
        # Create an Option with a name
        option = Option(param_decls=['--test-option'])
        assert option.human_readable_name == 'test_option'
    
    def test_argument_human_readable_name_returns_metavar_when_available(self):
        """Test that Argument.human_readable_name returns metavar when available."""
        # Create an Argument with metavar
        arg = Argument(param_decls=['test_arg'], metavar='METAVAR')
        assert arg.human_readable_name == 'METAVAR'
    
    def test_argument_human_readable_name_returns_uppercase_name_when_no_metavar(self):
        """Test that Argument.human_readable_name returns uppercase name when no metavar."""
        # Create an Argument without metavar
        arg = Argument(param_decls=['test_arg'])
        assert arg.human_readable_name == 'TEST_ARG'
