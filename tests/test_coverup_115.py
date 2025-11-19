# file: src/flask/src/flask/helpers.py:386-398
# asked: {"lines": [386, 387, 389, 390, 392, 393, 394, 395, 396, 398], "branches": [[389, 390], [389, 392]]}
# gained: {"lines": [386, 387, 389, 390, 392, 393, 394, 395, 396, 398], "branches": [[389, 390], [389, 392]]}

import pytest
from flask import Flask
from flask.helpers import _prepare_send_file_kwargs
from flask.globals import app_ctx


class TestPrepareSendFileKwargs:
    def test_prepare_send_file_kwargs_without_max_age(self):
        """Test _prepare_send_file_kwargs when max_age is not provided."""
        app = Flask(__name__)
        app.config["USE_X_SENDFILE"] = False
        app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 3600
        
        with app.test_request_context():
            ctx = app_ctx._get_current_object()
            result = _prepare_send_file_kwargs()
            
            # The function assigns the method itself, not its return value
            assert result["max_age"] == ctx.app.get_send_file_max_age
            assert result["environ"] == ctx.request.environ
            assert result["use_x_sendfile"] is False
            assert result["response_class"] == app.response_class
            assert result["_root_path"] == app.root_path

    def test_prepare_send_file_kwargs_with_max_age(self):
        """Test _prepare_send_file_kwargs when max_age is provided."""
        app = Flask(__name__)
        app.config["USE_X_SENDFILE"] = True
        app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 3600
        
        with app.test_request_context():
            ctx = app_ctx._get_current_object()
            result = _prepare_send_file_kwargs(max_age=1800)
            
            assert result["max_age"] == 1800
            assert result["environ"] == ctx.request.environ
            assert result["use_x_sendfile"] is True
            assert result["response_class"] == app.response_class
            assert result["_root_path"] == app.root_path

    def test_prepare_send_file_kwargs_with_none_max_age(self):
        """Test _prepare_send_file_kwargs when max_age is explicitly None."""
        app = Flask(__name__)
        app.config["USE_X_SENDFILE"] = False
        app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 3600
        
        with app.test_request_context():
            ctx = app_ctx._get_current_object()
            result = _prepare_send_file_kwargs(max_age=None)
            
            # The function assigns the method itself, not its return value
            assert result["max_age"] == ctx.app.get_send_file_max_age
            assert result["environ"] == ctx.request.environ
            assert result["use_x_sendfile"] is False
            assert result["response_class"] == app.response_class
            assert result["_root_path"] == app.root_path

    def test_prepare_send_file_kwargs_with_none_send_file_max_age_default(self):
        """Test _prepare_send_file_kwargs when SEND_FILE_MAX_AGE_DEFAULT is None."""
        app = Flask(__name__)
        app.config["USE_X_SENDFILE"] = True
        app.config["SEND_FILE_MAX_AGE_DEFAULT"] = None
        
        with app.test_request_context():
            ctx = app_ctx._get_current_object()
            result = _prepare_send_file_kwargs()
            
            # The function assigns the method itself, not its return value
            assert result["max_age"] == ctx.app.get_send_file_max_age
            assert result["environ"] == ctx.request.environ
            assert result["use_x_sendfile"] is True
            assert result["response_class"] == app.response_class
            assert result["_root_path"] == app.root_path
