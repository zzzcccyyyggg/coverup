# file: src/flask/src/flask/json/provider.py:41-47
# asked: {"lines": [41, 47], "branches": []}
# gained: {"lines": [41, 47], "branches": []}

import pytest
from flask import Flask
from flask.json.provider import JSONProvider

class TestJSONProvider:
    def test_dumps_not_implemented(self):
        """Test that JSONProvider.dumps raises NotImplementedError"""
        app = Flask(__name__)
        provider = JSONProvider(app)
        
        with pytest.raises(NotImplementedError):
            provider.dumps({"test": "data"})
