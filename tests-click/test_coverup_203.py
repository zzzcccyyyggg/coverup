# file: src/click/src/click/types.py:360-372
# asked: {"lines": [360, 367, 368, 369, 370, 371, 372], "branches": []}
# gained: {"lines": [360, 367, 368, 369, 370, 371, 372], "branches": []}

import pytest
from click.types import Choice
from click.core import Context, Command


class TestChoiceInvalidChoiceMessage:
    def test_get_invalid_choice_message_single_choice(self):
        """Test get_invalid_choice_message with a single choice."""
        choice_type = Choice(["option1"])
        value = "invalid_value"
        
        result = choice_type.get_invalid_choice_message(value, None)
        
        assert result == "'invalid_value' is not 'option1'."
    
    def test_get_invalid_choice_message_multiple_choices(self):
        """Test get_invalid_choice_message with multiple choices."""
        choice_type = Choice(["option1", "option2", "option3"])
        value = "invalid_value"
        
        result = choice_type.get_invalid_choice_message(value, None)
        
        assert result == "'invalid_value' is not one of 'option1', 'option2', 'option3'."
    
    def test_get_invalid_choice_message_with_context_normalization(self):
        """Test get_invalid_choice_message with context that has token_normalize_func."""
        choice_type = Choice(["option1", "option2"])
        value = "invalid_value"
        
        # Create a mock command and context with token_normalize_func
        command = Command("test_command")
        ctx = Context(command)
        ctx.token_normalize_func = lambda x: x.upper()
        
        result = choice_type.get_invalid_choice_message(value, ctx)
        
        assert result == "'invalid_value' is not one of 'OPTION1', 'OPTION2'."
    
    def test_get_invalid_choice_message_case_insensitive(self):
        """Test get_invalid_choice_message with case insensitive choices."""
        choice_type = Choice(["Option1", "Option2"], case_sensitive=False)
        value = "invalid_value"
        
        result = choice_type.get_invalid_choice_message(value, None)
        
        assert result == "'invalid_value' is not one of 'option1', 'option2'."
    
    def test_get_invalid_choice_message_enum_choices(self):
        """Test get_invalid_choice_message with enum choices."""
        from enum import Enum
        
        class TestEnum(Enum):
            OPTION1 = "value1"
            OPTION2 = "value2"
        
        choice_type = Choice([TestEnum.OPTION1, TestEnum.OPTION2])
        value = "invalid_value"
        
        result = choice_type.get_invalid_choice_message(value, None)
        
        assert result == "'invalid_value' is not one of 'OPTION1', 'OPTION2'."
