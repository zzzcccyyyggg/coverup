# file: src/flask/src/flask/json/provider.py:59-65
# asked: {"lines": [59, 65], "branches": []}
# gained: {"lines": [59, 65], "branches": []}

import pytest
import typing as t
from flask import Flask
from flask.json.provider import JSONProvider

class TestJSONProvider:
    def test_loads_not_implemented(self):
        """Test that JSONProvider.loads raises NotImplementedError"""
        app = Flask(__name__)
        provider = JSONProvider(app)
        
        with pytest.raises(NotImplementedError):
            provider.loads('{"test": "data"}')
    
    def test_loads_with_bytes_input(self):
        """Test that JSONProvider.loads raises NotImplementedError with bytes input"""
        app = Flask(__name__)
        provider = JSONProvider(app)
        
        with pytest.raises(NotImplementedError):
            provider.loads(b'{"test": "data"}')
    
    def test_loads_with_kwargs(self):
        """Test that JSONProvider.loads raises NotImplementedError with additional kwargs"""
        app = Flask(__name__)
        provider = JSONProvider(app)
        
        with pytest.raises(NotImplementedError):
            provider.loads('{"test": "data"}', parse_float=float)
