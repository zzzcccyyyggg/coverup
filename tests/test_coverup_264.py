# file: src/flask/src/flask/sansio/app.py:476-477
# asked: {"lines": [476, 477], "branches": []}
# gained: {"lines": [476, 477], "branches": []}

import pytest
from flask.sansio.app import App


def test_create_jinja_environment_not_implemented():
    """Test that create_jinja_environment raises NotImplementedError."""
    # Create a minimal App instance by setting the required attributes before __init__ completes
    app = App.__new__(App)
    app.default_config = {}
    
    with pytest.raises(NotImplementedError):
        app.create_jinja_environment()
