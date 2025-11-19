# file: src/flask/src/flask/json/provider.py:75-87
# asked: {"lines": [75, 78, 79, 81, 82, 84, 85, 87], "branches": [[78, 79], [78, 81], [81, 82], [81, 84], [84, 85], [84, 87]]}
# gained: {"lines": [75, 78, 79, 81, 82, 84, 85, 87], "branches": [[78, 79], [78, 81], [81, 82], [81, 84], [84, 85], [84, 87]]}

import pytest
import typing as t
from flask import Flask
from flask.json.provider import JSONProvider


class TestJSONProviderPrepareResponseObj:
    """Test cases for JSONProvider._prepare_response_obj method"""
    
    def test_prepare_response_obj_both_args_and_kwargs_raises_error(self):
        """Test that TypeError is raised when both args and kwargs are provided"""
        app = Flask(__name__)
        provider = JSONProvider(app)
        
        with pytest.raises(TypeError) as exc_info:
            provider._prepare_response_obj((1, 2), {'key': 'value'})
        
        assert "app.json.response() takes either args or kwargs, not both" in str(exc_info.value)
    
    def test_prepare_response_obj_no_args_no_kwargs_returns_none(self):
        """Test that None is returned when neither args nor kwargs are provided"""
        app = Flask(__name__)
        provider = JSONProvider(app)
        
        result = provider._prepare_response_obj((), {})
        
        assert result is None
    
    def test_prepare_response_obj_single_arg_returns_arg(self):
        """Test that single argument is returned directly"""
        app = Flask(__name__)
        provider = JSONProvider(app)
        
        result = provider._prepare_response_obj(('single',), {})
        
        assert result == 'single'
    
    def test_prepare_response_obj_multiple_args_returns_args(self):
        """Test that multiple arguments are returned as tuple"""
        app = Flask(__name__)
        provider = JSONProvider(app)
        
        result = provider._prepare_response_obj(('first', 'second'), {})
        
        assert result == ('first', 'second')
    
    def test_prepare_response_obj_kwargs_returns_kwargs(self):
        """Test that kwargs are returned when provided"""
        app = Flask(__name__)
        provider = JSONProvider(app)
        
        result = provider._prepare_response_obj((), {'key': 'value'})
        
        assert result == {'key': 'value'}
