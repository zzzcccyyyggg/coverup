# file: src/flask/src/flask/sessions.py:277-284
# asked: {"lines": [277, 284], "branches": []}
# gained: {"lines": [277, 284], "branches": []}

import pytest
from flask.app import Flask
from flask.wrappers import Response
from flask.sessions import SessionInterface

class ConcreteSession(dict):
    """A concrete session class that implements SessionMixin interface."""
    new = False
    modified = True
    accessed = True
    
    @property
    def permanent(self):
        return False
    
    @permanent.setter
    def permanent(self, value):
        pass

class TestSessionInterface:
    def test_save_session_not_implemented(self):
        """Test that save_session raises NotImplementedError when called."""
        interface = SessionInterface()
        app = Flask(__name__)
        session = ConcreteSession()
        response = Response()
        
        with pytest.raises(NotImplementedError):
            interface.save_session(app, session, response)
