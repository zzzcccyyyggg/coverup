# file: src/flask/src/flask/json/provider.py:49-57
# asked: {"lines": [49, 57], "branches": []}
# gained: {"lines": [49, 57], "branches": []}

import pytest
import tempfile
import os
from unittest.mock import Mock, patch
import typing as t

class TestJSONProviderDump:
    """Test cases for JSONProvider.dump method to achieve full coverage."""
    
    def test_dump_writes_to_file(self):
        """Test that dump method writes serialized data to file."""
        from flask.json.provider import JSONProvider
        from flask import Flask
        
        # Create a Flask app instance to pass to JSONProvider
        app = Flask(__name__)
        
        # Create a mock provider with a dumps method that returns a string
        provider = JSONProvider(app)
        provider.dumps = Mock(return_value='{"test": "data"}')
        
        # Create a temporary file to write to
        with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as temp_file:
            temp_path = temp_file.name
        
        try:
            # Open the file for writing and call dump
            with open(temp_path, 'w', encoding='utf-8') as fp:
                provider.dump({"test": "data"}, fp)
            
            # Verify the file was written with expected content
            with open(temp_path, 'r', encoding='utf-8') as fp:
                content = fp.read()
                assert content == '{"test": "data"}'
            
            # Verify dumps was called with correct arguments
            provider.dumps.assert_called_once_with({"test": "data"})
            
        finally:
            # Clean up the temporary file
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_dump_with_kwargs(self):
        """Test that dump method passes kwargs to dumps method."""
        from flask.json.provider import JSONProvider
        from flask import Flask
        
        # Create a Flask app instance
        app = Flask(__name__)
        
        # Create a mock provider
        provider = JSONProvider(app)
        provider.dumps = Mock(return_value='{"indented": "data"}')
        
        # Create a temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as temp_file:
            temp_path = temp_file.name
        
        try:
            # Call dump with additional kwargs
            with open(temp_path, 'w', encoding='utf-8') as fp:
                provider.dump({"indented": "data"}, fp, indent=2, sort_keys=True)
            
            # Verify dumps was called with kwargs
            provider.dumps.assert_called_once_with({"indented": "data"}, indent=2, sort_keys=True)
            
            # Verify file content
            with open(temp_path, 'r', encoding='utf-8') as fp:
                content = fp.read()
                assert content == '{"indented": "data"}'
                
        finally:
            # Clean up
            if os.path.exists(temp_path):
                os.unlink(temp_path)
