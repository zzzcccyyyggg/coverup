# file: src/flask/src/flask/ctx.py:482-484
# asked: {"lines": [482, 483, 484], "branches": []}
# gained: {"lines": [482, 483, 484], "branches": []}

import pytest
from flask import Flask
from flask.ctx import AppContext


def test_app_context_enter_method():
    """Test that AppContext.__enter__ method executes and returns self."""
    app = Flask(__name__)
    
    with AppContext(app) as ctx:
        assert ctx is not None
        assert isinstance(ctx, AppContext)
        assert ctx.app is app
