# file: src/flask/src/flask/wrappers.py:197-210
# asked: {"lines": [205, 206, 208, 210], "branches": [[202, 208]]}
# gained: {"lines": [205, 206, 208, 210], "branches": [[202, 208]]}

import pytest
from flask import Flask
from flask.wrappers import Request
from werkzeug.test import EnvironBuilder
from werkzeug.datastructures import MultiDict


def test_request_load_form_data_debug_mode_non_multipart_no_files():
    """Test that _load_form_data attaches enctype error multidict in debug mode with non-multipart content type and no files."""
    app = Flask(__name__)
    app.config['DEBUG'] = True
    
    with app.test_request_context():
        builder = EnvironBuilder(method='POST', data={'key': 'value'})
        environ = builder.get_environ()
        request = Request(environ)
        
        # Ensure conditions are met: debug mode, non-multipart, no files
        assert app.debug is True
        assert request.mimetype != "multipart/form-data"
        assert not request.files
        
        # Store original class for comparison
        original_files_class = request.files.__class__
        
        # Call the method that should trigger the attachment
        request._load_form_data()
        
        # Verify that files multidict class was modified
        assert request.files.__class__ != original_files_class
        # The class should have a different name indicating it was patched
        assert hasattr(request.files.__class__, '__name__')


def test_request_load_form_data_debug_mode_multipart_with_files():
    """Test that _load_form_data does NOT attach enctype error multidict when mimetype is multipart/form-data."""
    app = Flask(__name__)
    app.config['DEBUG'] = True
    
    with app.test_request_context():
        # Create a multipart form data request
        builder = EnvironBuilder(
            method='POST',
            data={'field': 'value'},
            content_type='multipart/form-data'
        )
        environ = builder.get_environ()
        request = Request(environ)
        
        # Ensure conditions: debug mode, multipart mimetype
        assert app.debug is True
        assert request.mimetype == "multipart/form-data"
        
        # Store original class for comparison
        original_files_class = request.files.__class__
        
        # Call the method - should NOT trigger attachment due to multipart mimetype
        request._load_form_data()
        
        # Verify that files multidict class was NOT modified
        assert request.files.__class__ == original_files_class


def test_request_load_form_data_debug_mode_with_files():
    """Test that _load_form_data does NOT attach enctype error multidict when files exist."""
    app = Flask(__name__)
    app.config['DEBUG'] = True
    
    with app.test_request_context():
        builder = EnvironBuilder(method='POST')
        environ = builder.get_environ()
        request = Request(environ)
        
        # Mock files to be non-empty by creating a mock files multidict
        mock_files = MultiDict()
        mock_files.add('file', 'mock_file_data')
        
        # Use monkeypatch to safely replace the files attribute
        import flask.wrappers
        
        # Store original files
        original_files = request.files
        
        # Replace files with mock that has content
        request.files = mock_files
        
        try:
            # Store original class for comparison
            original_files_class = request.files.__class__
            
            # Call the method - should NOT trigger attachment due to existing files
            request._load_form_data()
            
            # Verify that files multidict class was NOT modified
            assert request.files.__class__ == original_files_class
        finally:
            # Restore original files
            request.files = original_files


def test_request_load_form_data_non_debug_mode():
    """Test that _load_form_data does NOT attach enctype error multidict when not in debug mode."""
    app = Flask(__name__)
    app.config['DEBUG'] = False
    
    with app.test_request_context():
        builder = EnvironBuilder(method='POST', data={'key': 'value'})
        environ = builder.get_environ()
        request = Request(environ)
        
        # Ensure conditions: non-debug mode, non-multipart, no files
        assert app.debug is False
        assert request.mimetype != "multipart/form-data"
        assert not request.files
        
        # Store original class for comparison
        original_files_class = request.files.__class__
        
        # Call the method - should NOT trigger attachment due to non-debug mode
        request._load_form_data()
        
        # Verify that files multidict class was NOT modified
        assert request.files.__class__ == original_files_class
