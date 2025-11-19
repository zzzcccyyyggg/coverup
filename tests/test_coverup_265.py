# file: src/flask/src/flask/json/__init__.py:138-170
# asked: {"lines": [138, 170], "branches": []}
# gained: {"lines": [138, 170], "branches": []}

import pytest
from flask import Flask, jsonify
import json


class TestJsonify:
    """Test cases for the jsonify function to achieve full coverage."""
    
    def test_jsonify_with_positional_args(self, app: Flask):
        """Test jsonify with positional arguments."""
        with app.app_context():
            response = jsonify("test", 123, True)
            data = json.loads(response.get_data(as_text=True))
            assert data == ["test", 123, True]
            assert response.mimetype == "application/json"
    
    def test_jsonify_with_keyword_args(self, app: Flask):
        """Test jsonify with keyword arguments."""
        with app.app_context():
            response = jsonify(name="test", value=123, flag=True)
            data = json.loads(response.get_data(as_text=True))
            assert data == {"name": "test", "value": 123, "flag": True}
            assert response.mimetype == "application/json"
    
    def test_jsonify_with_no_args(self, app: Flask):
        """Test jsonify with no arguments."""
        with app.app_context():
            response = jsonify()
            data = json.loads(response.get_data(as_text=True))
            assert data is None
            assert response.mimetype == "application/json"
    
    def test_jsonify_with_single_positional_arg(self, app: Flask):
        """Test jsonify with a single positional argument."""
        with app.app_context():
            response = jsonify("single")
            data = json.loads(response.get_data(as_text=True))
            assert data == "single"
            assert response.mimetype == "application/json"
    
    def test_jsonify_with_list_positional_args(self, app: Flask):
        """Test jsonify with multiple positional arguments forming a list."""
        with app.app_context():
            response = jsonify(1, 2, 3)
            data = json.loads(response.get_data(as_text=True))
            assert data == [1, 2, 3]
            assert response.mimetype == "application/json"
    
    def test_jsonify_with_dict_keyword_args(self, app: Flask):
        """Test jsonify with keyword arguments forming a dict."""
        with app.app_context():
            response = jsonify(a=1, b=2, c=3)
            data = json.loads(response.get_data(as_text=True))
            assert data == {"a": 1, "b": 2, "c": 3}
            assert response.mimetype == "application/json"
    
    def test_jsonify_with_nested_data(self, app: Flask):
        """Test jsonify with nested data structures."""
        with app.app_context():
            response = jsonify({
                "users": [
                    {"name": "Alice", "age": 30},
                    {"name": "Bob", "age": 25}
                ],
                "count": 2
            })
            data = json.loads(response.get_data(as_text=True))
            expected = {
                "users": [
                    {"name": "Alice", "age": 30},
                    {"name": "Bob", "age": 25}
                ],
                "count": 2
            }
            assert data == expected
            assert response.mimetype == "application/json"


@pytest.fixture
def app():
    """Create a Flask app for testing."""
    app = Flask(__name__)
    app.config['TESTING'] = True
    return app
