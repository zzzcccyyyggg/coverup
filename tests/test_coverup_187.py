# file: src/flask/src/flask/testing.py:255-262
# asked: {"lines": [255, 261, 262], "branches": []}
# gained: {"lines": [255, 261, 262], "branches": []}

import pytest
from flask import Flask
from flask.testing import FlaskClient

def test_flask_client_exit_method():
    """Test that FlaskClient.__exit__ method executes lines 255-262."""
    app = Flask(__name__)
    
    with app.test_client() as client:
        # The __exit__ method should be called when exiting the context manager
        # This should set preserve_context to False and close the context stack
        pass
    
    # After exiting the context, preserve_context should be False
    assert client.preserve_context is False
    # The context stack should be closed (we can't directly test this, but no error should occur)
