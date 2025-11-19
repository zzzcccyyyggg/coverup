# file: src/flask/src/flask/helpers.py:265-285
# asked: {"lines": [282, 283, 285], "branches": [[282, 283], [282, 285]]}
# gained: {"lines": [282, 283, 285], "branches": [[282, 283], [282, 285]]}

import pytest
from werkzeug.exceptions import HTTPException
from flask import Flask
from flask.helpers import abort
from flask.globals import _cv_app


def test_abort_with_current_app():
    """Test abort when current app context is available."""
    app = Flask(__name__)
    
    # Mock the aborter to verify it's called
    mock_aborter_called = False
    
    def mock_aborter(code, *args, **kwargs):
        nonlocal mock_aborter_called
        mock_aborter_called = True
        # Create a proper HTTPException with description
        exc = HTTPException()
        exc.code = code
        exc.description = f"Mock abort with code {code}"
        raise exc
    
    app.aborter = mock_aborter
    
    with app.app_context():
        # Verify current app context is available
        assert _cv_app.get(None) is not None
        
        # Test that abort calls the app's aborter
        with pytest.raises(HTTPException) as exc_info:
            abort(404)
        
        assert mock_aborter_called
        assert exc_info.value.code == 404
        assert exc_info.value.description == "Mock abort with code 404"


def test_abort_without_current_app():
    """Test abort when no current app context is available."""
    # Ensure no app context is active
    assert _cv_app.get(None) is None
    
    # Test that abort falls back to werkzeug.abort
    with pytest.raises(HTTPException) as exc_info:
        abort(500)
    
    # Verify it's using werkzeug's abort (should have default description)
    assert exc_info.value.code == 500
