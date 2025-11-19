# file: src/flask/src/flask/ctx.py:380-396
# asked: {"lines": [380, 381, 386, 387, 389, 390, 391, 393, 394, 396], "branches": [[386, 387], [386, 389], [389, 390], [389, 396], [393, 394], [393, 396]]}
# gained: {"lines": [380, 381, 386, 387, 389, 390, 391, 393, 394, 396], "branches": [[386, 387], [386, 389], [389, 390], [389, 396], [393, 394], [393, 396]]}

import pytest
from flask import Flask
from flask.ctx import AppContext
from flask.sessions import SessionMixin, SessionInterface
from flask.wrappers import Request
from werkzeug.test import EnvironBuilder


class MockSession(SessionMixin, dict):
    """Mock session that implements SessionMixin interface."""
    pass


class MockSessionInterface(SessionInterface):
    """Mock session interface for testing."""
    
    def __init__(self, open_session_return=None):
        self.open_session_return = open_session_return
        self.open_session_called = False
        self.make_null_session_called = False
    
    def open_session(self, app, request):
        self.open_session_called = True
        return self.open_session_return
    
    def make_null_session(self, app):
        self.make_null_session_called = True
        return MockSession()


def test_session_property_without_request_raises_runtime_error():
    """Test that accessing session without request raises RuntimeError."""
    app = Flask(__name__)
    ctx = AppContext(app)
    
    with pytest.raises(RuntimeError, match="There is no request in this context."):
        _ = ctx.session


def test_session_property_opens_session_when_none():
    """Test that session property opens session when _session is None."""
    app = Flask(__name__)
    mock_session = MockSession()
    mock_session_interface = MockSessionInterface(open_session_return=mock_session)
    app.session_interface = mock_session_interface
    
    # Create a request context
    builder = EnvironBuilder()
    environ = builder.get_environ()
    request = app.request_class(environ)
    
    ctx = AppContext(app, request=request)
    
    # Access session property - should trigger session opening
    session = ctx.session
    
    assert session is mock_session
    assert mock_session_interface.open_session_called
    assert not mock_session_interface.make_null_session_called
    assert ctx._session is mock_session


def test_session_property_creates_null_session_when_open_returns_none():
    """Test that session property creates null session when open_session returns None."""
    app = Flask(__name__)
    mock_session_interface = MockSessionInterface(open_session_return=None)
    app.session_interface = mock_session_interface
    
    # Create a request context
    builder = EnvironBuilder()
    environ = builder.get_environ()
    request = app.request_class(environ)
    
    ctx = AppContext(app, request=request)
    
    # Access session property - should trigger null session creation
    session = ctx.session
    
    assert isinstance(session, MockSession)
    assert mock_session_interface.open_session_called
    assert mock_session_interface.make_null_session_called
    assert ctx._session is session


def test_session_property_returns_existing_session():
    """Test that session property returns existing session without re-opening."""
    app = Flask(__name__)
    existing_session = MockSession()
    mock_session_interface = MockSessionInterface()
    app.session_interface = mock_session_interface
    
    # Create a request context with existing session
    builder = EnvironBuilder()
    environ = builder.get_environ()
    request = app.request_class(environ)
    
    ctx = AppContext(app, request=request, session=existing_session)
    
    # Access session property multiple times
    session1 = ctx.session
    session2 = ctx.session
    
    assert session1 is existing_session
    assert session2 is existing_session
    assert not mock_session_interface.open_session_called
    assert not mock_session_interface.make_null_session_called
