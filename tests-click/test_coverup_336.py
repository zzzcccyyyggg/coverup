# file: src/click/src/click/types.py:326-334
# asked: {"lines": [326, 332, 333], "branches": []}
# gained: {"lines": [326, 332, 333], "branches": []}

import pytest
from click.types import Choice
from click.core import Context, Option
from click.decorators import command
from click.testing import CliRunner


class TestChoiceGetMissingMessage:
    """Test cases for Choice.get_missing_message method."""
    
    def test_get_missing_message_with_ctx_and_token_normalize_func(self):
        """Test get_missing_message with context and token_normalize_func."""
        # Create a choice with multiple options
        choices = ['option1', 'option2', 'option3']
        choice_type = Choice(choices)
        
        # Create a context with token_normalize_func
        @command()
        def test_cmd():
            pass
            
        runner = CliRunner()
        with runner.isolation():
            ctx = Context(test_cmd)
            ctx.token_normalize_func = lambda x: x.upper()
            
            # Create a mock parameter using Option
            param = Option(['--test-param'])
            
            # Call get_missing_message
            result = choice_type.get_missing_message(param, ctx)
            
            # Verify the result contains all normalized choices
            assert 'OPTION1' in result
            assert 'OPTION2' in result
            assert 'OPTION3' in result
            assert 'Choose from:' in result
    
    def test_get_missing_message_without_ctx(self):
        """Test get_missing_message without context."""
        # Create a choice with multiple options
        choices = ['apple', 'banana', 'cherry']
        choice_type = Choice(choices)
        
        # Create a mock parameter using Option
        param = Option(['--test-param'])
        
        # Call get_missing_message without context
        result = choice_type.get_missing_message(param, None)
        
        # Verify the result contains all original choices
        assert 'apple' in result
        assert 'banana' in result
        assert 'cherry' in result
        assert 'Choose from:' in result
    
    def test_get_missing_message_with_case_insensitive_choices(self):
        """Test get_missing_message with case-insensitive choices."""
        # Create a case-insensitive choice
        choices = ['Red', 'Green', 'Blue']
        choice_type = Choice(choices, case_sensitive=False)
        
        # Create a mock parameter using Option
        param = Option(['--test-param'])
        
        # Call get_missing_message without context
        result = choice_type.get_missing_message(param, None)
        
        # Verify the result contains casefolded choices
        assert 'red' in result
        assert 'green' in result
        assert 'blue' in result
        assert 'Choose from:' in result
    
    def test_get_missing_message_with_enum_choices(self):
        """Test get_missing_message with enum choices."""
        from enum import Enum
        
        class Color(Enum):
            RED = 1
            GREEN = 2
            BLUE = 3
        
        # Create a choice with enum values
        choices = [Color.RED, Color.GREEN, Color.BLUE]
        choice_type = Choice(choices)
        
        # Create a mock parameter using Option
        param = Option(['--test-param'])
        
        # Call get_missing_message without context
        result = choice_type.get_missing_message(param, None)
        
        # Verify the result contains enum names
        assert 'RED' in result
        assert 'GREEN' in result
        assert 'BLUE' in result
        assert 'Choose from:' in result
    
    def test_get_missing_message_with_ctx_but_no_token_normalize_func(self):
        """Test get_missing_message with context but no token_normalize_func."""
        # Create a choice with multiple options
        choices = ['first', 'second', 'third']
        choice_type = Choice(choices)
        
        # Create a context without token_normalize_func
        @command()
        def test_cmd():
            pass
            
        runner = CliRunner()
        with runner.isolation():
            ctx = Context(test_cmd)
            # ctx.token_normalize_func remains None
            
            # Create a mock parameter using Option
            param = Option(['--test-param'])
            
            # Call get_missing_message
            result = choice_type.get_missing_message(param, ctx)
            
            # Verify the result contains all original choices
            assert 'first' in result
            assert 'second' in result
            assert 'third' in result
            assert 'Choose from:' in result
