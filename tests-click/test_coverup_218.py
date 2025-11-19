# file: src/click/src/click/types.py:270-286
# asked: {"lines": [270, 271, 280, 281, 282, 283, 285], "branches": []}
# gained: {"lines": [270, 271, 280, 281, 282, 283, 285], "branches": []}

import pytest
from click.types import Choice
from click.core import Context, Command


class TestChoiceNormalizedMapping:
    """Test cases for Choice._normalized_mapping method."""
    
    def test_normalized_mapping_with_ctx_and_token_normalize_func(self):
        """Test _normalized_mapping when ctx has token_normalize_func."""
        # Create a mock command for the context
        mock_command = Command('test_command')
        
        # Create a context with a token_normalize_func
        ctx = Context(mock_command)
        ctx.token_normalize_func = lambda x: x.upper()
        
        # Create a Choice instance with some choices
        choices = ['apple', 'banana', 'cherry']
        choice_type = Choice(choices)
        
        # Call _normalized_mapping with context
        result = choice_type._normalized_mapping(ctx)
        
        # Verify the mapping contains normalized values
        assert result == {
            'apple': 'APPLE',
            'banana': 'BANANA', 
            'cherry': 'CHERRY'
        }
    
    def test_normalized_mapping_without_ctx(self):
        """Test _normalized_mapping when ctx is None."""
        # Create a Choice instance with some choices
        choices = ['apple', 'banana', 'cherry']
        choice_type = Choice(choices)
        
        # Call _normalized_mapping without context
        result = choice_type._normalized_mapping()
        
        # Verify the mapping contains string representations
        assert result == {
            'apple': 'apple',
            'banana': 'banana',
            'cherry': 'cherry'
        }
    
    def test_normalized_mapping_case_insensitive(self):
        """Test _normalized_mapping with case-insensitive choice type."""
        # Create a case-insensitive Choice instance
        choices = ['Apple', 'Banana', 'Cherry']
        choice_type = Choice(choices, case_sensitive=False)
        
        # Call _normalized_mapping without context
        result = choice_type._normalized_mapping()
        
        # Verify the mapping contains casefolded values
        assert result == {
            'Apple': 'apple',
            'Banana': 'banana',
            'Cherry': 'cherry'
        }
    
    def test_normalized_mapping_with_enum_choices(self):
        """Test _normalized_mapping with enum choices."""
        from enum import Enum
        
        class Fruit(Enum):
            APPLE = 1
            BANANA = 2
            CHERRY = 3
        
        # Create a Choice instance with enum choices
        choices = [Fruit.APPLE, Fruit.BANANA, Fruit.CHERRY]
        choice_type = Choice(choices)
        
        # Call _normalized_mapping without context
        result = choice_type._normalized_mapping()
        
        # Verify the mapping uses enum names
        assert result == {
            Fruit.APPLE: 'APPLE',
            Fruit.BANANA: 'BANANA',
            Fruit.CHERRY: 'CHERRY'
        }
    
    def test_normalized_mapping_with_ctx_no_token_normalize_func(self):
        """Test _normalized_mapping when ctx exists but has no token_normalize_func."""
        # Create a mock command for the context
        mock_command = Command('test_command')
        
        # Create a context without token_normalize_func
        ctx = Context(mock_command)
        # ctx.token_normalize_func is None by default
        
        # Create a Choice instance with some choices
        choices = ['apple', 'banana', 'cherry']
        choice_type = Choice(choices)
        
        # Call _normalized_mapping with context
        result = choice_type._normalized_mapping(ctx)
        
        # Verify the mapping contains string representations (no normalization)
        assert result == {
            'apple': 'apple',
            'banana': 'banana',
            'cherry': 'cherry'
        }
