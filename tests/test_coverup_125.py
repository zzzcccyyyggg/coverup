# file: src/flask/src/flask/helpers.py:241-262
# asked: {"lines": [241, 242, 259, 260, 262], "branches": [[259, 260], [259, 262]]}
# gained: {"lines": [241, 242, 259, 260, 262], "branches": [[259, 260], [259, 262]]}

import pytest
from flask import Flask
from flask.helpers import redirect
from werkzeug.wrappers import Response as BaseResponse


class TestRedirect:
    def test_redirect_with_app_context(self):
        """Test redirect when current_app is available (lines 259-260)"""
        app = Flask(__name__)
        with app.app_context():
            response = redirect("/new-location", 301)
            assert response.status_code == 301
            assert response.headers["Location"] == "/new-location"
            assert isinstance(response, BaseResponse)

    def test_redirect_without_app_context(self):
        """Test redirect when current_app is not available (line 262)"""
        response = redirect("/another-location", 303)
        assert response.status_code == 303
        assert response.headers["Location"] == "/another-location"
        assert isinstance(response, BaseResponse)

    def test_redirect_with_custom_response_class(self):
        """Test redirect without app context but with custom Response class (line 262)"""
        class CustomResponse(BaseResponse):
            pass

        response = redirect("/custom", 307, Response=CustomResponse)
        assert response.status_code == 307
        assert response.headers["Location"] == "/custom"
        assert isinstance(response, CustomResponse)

    def test_redirect_default_code(self):
        """Test redirect with default status code"""
        response = redirect("/default")
        assert response.status_code == 302
        assert response.headers["Location"] == "/default"
        assert isinstance(response, BaseResponse)
