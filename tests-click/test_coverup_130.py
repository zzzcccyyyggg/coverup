# file: src/click/src/click/types.py:336-358
# asked: {"lines": [336, 344, 345, 347, 348, 349, 350, 351, 353, 354, 355, 356, 357], "branches": []}
# gained: {"lines": [336, 344, 345, 347, 348, 349, 350, 351, 353, 354, 355, 356, 357], "branches": []}

import pytest
from click.types import Choice
from click.exceptions import BadParameter
from click.core import Context, Command, Option


class TestChoiceConvert:
    """Test cases for Choice.convert method to cover lines 336-357."""
    
    def test_convert_valid_choice(self):
        """Test that convert returns the original choice when a valid normalized value is provided."""
        choice_type = Choice(['apple', 'banana', 'cherry'])
        result = choice_type.convert('apple', None, None)
        assert result == 'apple'
    
    def test_convert_valid_choice_case_insensitive(self):
        """Test that convert returns the original choice when a case-insensitive match is found."""
        choice_type = Choice(['apple', 'banana', 'cherry'], case_sensitive=False)
        result = choice_type.convert('APPLE', None, None)
        assert result == 'apple'
    
    def test_convert_with_context_token_normalize_func(self):
        """Test that convert works with context token_normalize_func."""
        # Create a minimal command to use with Context
        cmd = Command('test_cmd')
        ctx = Context(cmd)
        ctx.token_normalize_func = lambda x: x.upper()
        choice_type = Choice(['apple', 'banana', 'cherry'])
        
        result = choice_type.convert('APPLE', None, ctx)
        assert result == 'apple'
    
    def test_convert_invalid_choice_raises_bad_parameter(self):
        """Test that convert raises BadParameter when an invalid choice is provided."""
        choice_type = Choice(['apple', 'banana', 'cherry'])
        
        with pytest.raises(BadParameter) as exc_info:
            choice_type.convert('orange', None, None)
        
        assert 'orange' in str(exc_info.value)
        assert 'apple' in str(exc_info.value)
        assert 'banana' in str(exc_info.value)
        assert 'cherry' in str(exc_info.value)
    
    def test_convert_invalid_choice_with_param_and_ctx(self):
        """Test that convert raises BadParameter with proper param and ctx when invalid choice."""
        choice_type = Choice(['apple', 'banana'])
        # Create a minimal command and option for testing
        cmd = Command('test_cmd')
        param = Option(['--fruit'])
        ctx = Context(cmd)
        
        with pytest.raises(BadParameter) as exc_info:
            choice_type.convert('orange', param, ctx)
        
        assert exc_info.value.param is param
        assert exc_info.value.ctx is ctx
    
    def test_convert_with_enum_choices(self):
        """Test that convert works with enum choices."""
        from enum import Enum
        
        class Fruit(Enum):
            APPLE = 'apple'
            BANANA = 'banana'
            CHERRY = 'cherry'
        
        choice_type = Choice([Fruit.APPLE, Fruit.BANANA, Fruit.CHERRY])
        # For enum choices, we need to pass the enum name, not the value
        result = choice_type.convert('APPLE', None, None)
        assert result == Fruit.APPLE
    
    def test_convert_with_enum_choices_case_insensitive(self):
        """Test that convert works with enum choices in case-insensitive mode."""
        from enum import Enum
        
        class Fruit(Enum):
            APPLE = 'apple'
            BANANA = 'banana'
            CHERRY = 'cherry'
        
        choice_type = Choice([Fruit.APPLE, Fruit.BANANA, Fruit.CHERRY], case_sensitive=False)
        # For enum choices in case-insensitive mode, we can pass the enum name in any case
        result = choice_type.convert('apple', None, None)
        assert result == Fruit.APPLE
