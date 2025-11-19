# file: src/flask/src/flask/json/tag.py:321-323
# asked: {"lines": [321, 323], "branches": []}
# gained: {"lines": [321, 323], "branches": []}

import pytest
from flask.json.tag import TaggedJSONSerializer
from unittest.mock import patch

class TestTaggedJSONSerializerDumps:
    """Test cases for TaggedJSONSerializer.dumps method to achieve full coverage."""
    
    def test_dumps_calls_tag_and_dumps_with_separators(self):
        """Test that dumps method calls tag and flask.json.dumps with correct separators."""
        serializer = TaggedJSONSerializer()
        
        # Test with a simple value that doesn't require special tagging
        test_value = {"simple": "value"}
        
        # Mock flask.json.dumps to verify it's called with correct parameters
        with patch('flask.json.tag.dumps') as mock_dumps:
            mock_dumps.return_value = '{"simple": "value"}'
            
            result = serializer.dumps(test_value)
            
            # Verify dumps was called with tagged value and correct separators
            # The tag method will be called internally, we just need to verify the final call
            mock_dumps.assert_called_once()
            call_args = mock_dumps.call_args
            assert call_args[1]['separators'] == (",", ":")
            
            # Verify the result is what dumps returned
            assert result == '{"simple": "value"}'
    
    def test_dumps_with_none_value(self):
        """Test dumps method with None value."""
        serializer = TaggedJSONSerializer()
        
        with patch('flask.json.tag.dumps') as mock_dumps:
            mock_dumps.return_value = 'null'
            
            result = serializer.dumps(None)
            
            mock_dumps.assert_called_once()
            call_args = mock_dumps.call_args
            assert call_args[1]['separators'] == (",", ":")
            assert result == 'null'
    
    def test_dumps_with_complex_value(self):
        """Test dumps method with a complex value structure."""
        serializer = TaggedJSONSerializer()
        
        complex_value = {
            "nested": {
                "list": [1, 2, 3],
                "tuple": (4, 5, 6)
            }
        }
        
        with patch('flask.json.tag.dumps') as mock_dumps:
            mock_dumps.return_value = '{"nested": {"list": [1, 2, 3], "tuple": [4, 5, 6]}}'
            
            result = serializer.dumps(complex_value)
            
            mock_dumps.assert_called_once()
            call_args = mock_dumps.call_args
            assert call_args[1]['separators'] == (",", ":")
            assert 'nested' in result
    
    def test_dumps_with_string_value(self):
        """Test dumps method with a simple string value."""
        serializer = TaggedJSONSerializer()
        
        with patch('flask.json.tag.dumps') as mock_dumps:
            mock_dumps.return_value = '"test string"'
            
            result = serializer.dumps("test string")
            
            mock_dumps.assert_called_once()
            call_args = mock_dumps.call_args
            assert call_args[1]['separators'] == (",", ":")
            assert result == '"test string"'
    
    def test_dumps_with_list_value(self):
        """Test dumps method with a list value."""
        serializer = TaggedJSONSerializer()
        
        list_value = [1, "two", {"three": 3}]
        
        with patch('flask.json.tag.dumps') as mock_dumps:
            mock_dumps.return_value = '[1, "two", {"three": 3}]'
            
            result = serializer.dumps(list_value)
            
            mock_dumps.assert_called_once()
            call_args = mock_dumps.call_args
            assert call_args[1]['separators'] == (",", ":")
            assert result == '[1, "two", {"three": 3}]'
