# file: src/flask/src/flask/sessions.py:263-275
# asked: {"lines": [263, 275], "branches": []}
# gained: {"lines": [263, 275], "branches": []}

import pytest
from flask.app import Flask
from flask.wrappers import Request
from flask.sessions import SessionInterface, SessionMixin


class TestSessionInterface:
    """Test cases for SessionInterface class."""
    
    def test_open_session_not_implemented(self):
        """Test that open_session raises NotImplementedError."""
        session_interface = SessionInterface()
        app = Flask(__name__)
        request = Request({'REQUEST_METHOD': 'GET', 'PATH_INFO': '/'})
        
        with pytest.raises(NotImplementedError):
            session_interface.open_session(app, request)
