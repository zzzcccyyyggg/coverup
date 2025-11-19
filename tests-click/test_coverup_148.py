# file: src/click/src/click/types.py:308-324
# asked: {"lines": [308, 309, 310, 311, 313, 315, 316, 320, 321, 324], "branches": [[309, 310], [309, 315], [320, 321], [320, 324]]}
# gained: {"lines": [308, 309, 310, 311, 313, 315, 316, 320, 321, 324], "branches": [[309, 310], [309, 315], [320, 321], [320, 324]]}

import pytest
from click.types import Choice
from click.core import Context, Option, Argument
from click import Command

class TestChoiceGetMetavar:
    def test_get_metavar_option_without_show_choices(self):
        """Test get_metavar for option parameter when show_choices is False."""
        choice_type = Choice(['apple', 'banana', 'cherry'])
        param = Option(['--fruit'])
        param.show_choices = False
        
        ctx = Context(Command('test'))
        
        result = choice_type.get_metavar(param, ctx)
        
        # When show_choices is False for an option, it should use type names
        # All choices are strings, so it should be [TEXT] (not [STRING])
        assert result == "[TEXT]"
    
    def test_get_metavar_option_with_show_choices(self):
        """Test get_metavar for option parameter when show_choices is True."""
        choice_type = Choice(['apple', 'banana', 'cherry'])
        param = Option(['--fruit'])
        param.show_choices = True
        
        ctx = Context(Command('test'))
        
        result = choice_type.get_metavar(param, ctx)
        
        # When show_choices is True for an option, it should show actual choices
        assert result == "[apple|banana|cherry]"
    
    def test_get_metavar_required_argument(self):
        """Test get_metavar for required argument parameter."""
        choice_type = Choice(['red', 'green', 'blue'])
        param = Argument(['color'], required=True)
        
        ctx = Context(Command('test'))
        
        result = choice_type.get_metavar(param, ctx)
        
        # Required arguments use curly braces
        assert result == "{red|green|blue}"
    
    def test_get_metavar_optional_argument(self):
        """Test get_metavar for optional argument parameter."""
        choice_type = Choice(['yes', 'no'])
        param = Argument(['answer'], required=False)
        
        ctx = Context(Command('test'))
        
        result = choice_type.get_metavar(param, ctx)
        
        # Optional arguments use square braces
        assert result == "[yes|no]"
    
    def test_get_metavar_option_with_mixed_types(self):
        """Test get_metavar for option with mixed type choices when show_choices is False."""
        choice_type = Choice([1, 2.5, 'three'])
        param = Option(['--value'])
        param.show_choices = False
        
        ctx = Context(Command('test'))
        
        result = choice_type.get_metavar(param, ctx)
        
        # Should deduplicate type names: INTEGER, FLOAT, TEXT -> [INTEGER|FLOAT|TEXT]
        assert result == "[INTEGER|FLOAT|TEXT]"
    
    def test_get_metavar_option_with_duplicate_types(self):
        """Test get_metavar for option with duplicate types when show_choices is False."""
        choice_type = Choice([1, 2, 3])  # All integers
        param = Option(['--number'])
        param.show_choices = False
        
        ctx = Context(Command('test'))
        
        result = choice_type.get_metavar(param, ctx)
        
        # Should deduplicate type names: INTEGER, INTEGER, INTEGER -> [INTEGER]
        assert result == "[INTEGER]"
