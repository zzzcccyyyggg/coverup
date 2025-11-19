# file: src/flask/src/flask/debughelpers.py:81-104
# asked: {"lines": [81, 88, 90, 91, 92, 93, 94, 95, 96, 98, 99, 100, 102, 103, 104], "branches": [[95, 96], [95, 98]]}
# gained: {"lines": [81, 88, 90, 91, 92, 93, 94, 95, 96, 98, 99, 100, 102, 103, 104], "branches": [[95, 96], [95, 98]]}

import pytest
from flask import Flask, Request
from flask.debughelpers import attach_enctype_error_multidict, DebugFilesKeyError
from werkzeug.datastructures import MultiDict
from werkzeug.test import EnvironBuilder


class TestAttachEnctypeErrorMultidict:
    def test_attach_enctype_error_multidict_key_in_form_raises_debug_error(self):
        """Test that accessing a key in request.files that exists in form raises DebugFilesKeyError."""
        app = Flask(__name__)
        
        builder = EnvironBuilder(
            method='POST',
            data={'file_field': 'filename.txt'},
            content_type='application/x-www-form-urlencoded'
        )
        environ = builder.get_environ()
        
        with app.request_context(environ):
            request = Request(environ)
            # Ensure form data is loaded
            _ = request.form
            
            attach_enctype_error_multidict(request)
            
            with pytest.raises(DebugFilesKeyError) as exc_info:
                _ = request.files['file_field']
            
            assert 'file_field' in str(exc_info.value)
            assert "enctype=\"multipart/form-data\"" in str(exc_info.value)

    def test_attach_enctype_error_multidict_key_not_in_form_raises_keyerror(self):
        """Test that accessing a key in request.files that doesn't exist in form raises KeyError."""
        app = Flask(__name__)
        
        builder = EnvironBuilder(
            method='POST',
            data={'other_field': 'value'},
            content_type='application/x-www-form-urlencoded'
        )
        environ = builder.get_environ()
        
        with app.request_context(environ):
            request = Request(environ)
            # Ensure form data is loaded
            _ = request.form
            
            attach_enctype_error_multidict(request)
            
            with pytest.raises(KeyError):
                _ = request.files['nonexistent_field']

    def test_attach_enctype_error_multidict_successful_access(self):
        """Test that accessing a key in request.files that exists works normally."""
        app = Flask(__name__)
        
        builder = EnvironBuilder(
            method='POST',
            content_type='multipart/form-data'
        )
        environ = builder.get_environ()
        
        with app.request_context(environ):
            request = Request(environ)
            # Add a file to the files multidict
            request.files = MultiDict({'file_field': 'file_content'})
            attach_enctype_error_multidict(request)
            
            # Should not raise any exception
            result = request.files['file_field']
            assert result == 'file_content'
