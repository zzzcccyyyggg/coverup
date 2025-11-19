# file: src/flask/src/flask/debughelpers.py:23-47
# asked: {"lines": [23, 24, 28, 29, 30, 31, 33, 38, 39, 40, 41, 42, 44, 46, 47], "branches": [[38, 39], [38, 44]]}
# gained: {"lines": [23, 24, 28, 29, 30, 31, 33, 38, 39, 40, 41, 42, 44, 46, 47], "branches": [[38, 39], [38, 44]]}

import pytest
from flask import Flask
from flask.debughelpers import DebugFilesKeyError
from unittest.mock import Mock

class TestDebugFilesKeyError:
    def test_debug_files_key_error_without_form_matches(self):
        """Test DebugFilesKeyError when there are no form matches for the key."""
        app = Flask(__name__)
        with app.test_request_context(method='POST', data={'other_field': 'value'}):
            request = Mock()
            request.mimetype = 'application/x-www-form-urlencoded'
            request.form.getlist.return_value = []
            
            error = DebugFilesKeyError(request, 'missing_file')
            
            expected_msg = (
                "You tried to access the file 'missing_file' in the request.files "
                "dictionary but it does not exist. The mimetype for the request is "
                "'application/x-www-form-urlencoded' instead of 'multipart/form-data' "
                "which means that no file contents were transmitted. To fix this error "
                'you should provide enctype="multipart/form-data" in your form.'
            )
            assert str(error) == expected_msg
            assert isinstance(error, KeyError)
            assert isinstance(error, AssertionError)
            request.form.getlist.assert_called_once_with('missing_file')

    def test_debug_files_key_error_with_form_matches(self):
        """Test DebugFilesKeyError when there are form matches for the key."""
        app = Flask(__name__)
        with app.test_request_context(method='POST', data={'file_field': ['file1.txt', 'file2.jpg']}):
            request = Mock()
            request.mimetype = 'application/x-www-form-urlencoded'
            request.form.getlist.return_value = ['file1.txt', 'file2.jpg']
            
            error = DebugFilesKeyError(request, 'file_field')
            
            expected_msg = (
                "You tried to access the file 'file_field' in the request.files "
                "dictionary but it does not exist. The mimetype for the request is "
                "'application/x-www-form-urlencoded' instead of 'multipart/form-data' "
                "which means that no file contents were transmitted. To fix this error "
                'you should provide enctype="multipart/form-data" in your form.'
                '\n\nThe browser instead transmitted some file names. This was submitted: '
                "'file1.txt', 'file2.jpg'"
            )
            assert str(error) == expected_msg
            assert isinstance(error, KeyError)
            assert isinstance(error, AssertionError)
            request.form.getlist.assert_called_once_with('file_field')
