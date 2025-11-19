# file: src/click/src/click/parser.py:161-163
# asked: {"lines": [161, 162, 163], "branches": []}
# gained: {"lines": [161, 162, 163], "branches": []}

import pytest
from click.parser import _Option
from click.core import Option

class TestOptionTakesValue:
    
    def test_takes_value_store_action(self):
        """Test that takes_value returns True for 'store' action."""
        option = Option(['--test'], help='Test option')
        parser_option = _Option(option, ['--test'], 'test', action='store')
        assert parser_option.takes_value is True
    
    def test_takes_value_append_action(self):
        """Test that takes_value returns True for 'append' action."""
        option = Option(['--test'], help='Test option')
        parser_option = _Option(option, ['--test'], 'test', action='append')
        assert parser_option.takes_value is True
    
    def test_takes_value_other_action(self):
        """Test that takes_value returns False for other actions."""
        option = Option(['--test'], help='Test option')
        parser_option = _Option(option, ['--test'], 'test', action='store_true')
        assert parser_option.takes_value is False
