# file: src/flask/src/flask/ctx.py:110-114
# asked: {"lines": [110, 111, 112, 113, 114], "branches": [[112, 113], [112, 114]]}
# gained: {"lines": [110, 111, 112, 113, 114], "branches": [[112, 113], [112, 114]]}

import pytest
from flask import Flask
from flask.ctx import _AppCtxGlobals
from flask.globals import _cv_app

class TestAppCtxGlobalsRepr:
    def test_repr_with_app_context(self):
        """Test __repr__ when there is an active app context"""
        app = Flask(__name__)
        with app.app_context():
            g = _AppCtxGlobals()
            result = repr(g)
            assert result == f"<flask.g of '{app.name}'>"

    def test_repr_without_app_context(self):
        """Test __repr__ when there is no active app context"""
        g = _AppCtxGlobals()
        result = repr(g)
        assert result == object.__repr__(g)
