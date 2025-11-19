# file: src/flask/src/flask/helpers.py:401-524
# asked: {"lines": [401, 403, 404, 405, 406, 407, 408, 409, 512, 513, 514, 515, 516, 517, 518, 519, 520, 521, 522], "branches": []}
# gained: {"lines": [401, 403, 404, 405, 406, 407, 408, 409, 512, 513, 514, 515, 516, 517, 518, 519, 520, 521, 522], "branches": []}

import pytest
import tempfile
import os
from datetime import datetime
from io import BytesIO
from flask import Flask
from flask.helpers import send_file

def test_send_file_with_file_like_object():
    """Test send_file with a file-like object (BytesIO)."""
    app = Flask(__name__)
    
    with app.test_request_context():
        # Create a file-like object with some content
        file_data = b"Hello, World!"
        file_obj = BytesIO(file_data)
        file_obj.seek(0)
        
        # Call send_file with the file-like object
        response = send_file(
            path_or_file=file_obj,
            mimetype='text/plain',
            as_attachment=False,
            download_name='test.txt'
        )
        
        # Verify the response - don't call get_data() on direct_passthrough responses
        assert response.status_code == 200
        assert response.mimetype == 'text/plain'
        assert response.direct_passthrough is True

def test_send_file_with_path_and_conditional_false():
    """Test send_file with a file path and conditional=False."""
    app = Flask(__name__)
    
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(b"Test content")
        tmp.flush()
        
        try:
            with app.test_request_context():
                response = send_file(
                    path_or_file=tmp.name,
                    mimetype='text/plain',
                    as_attachment=True,
                    download_name='download.txt',
                    conditional=False,
                    etag=False,
                    last_modified=None
                )
                
                assert response.status_code == 200
                assert response.mimetype == 'text/plain'
                assert 'attachment' in response.headers.get('Content-Disposition', '')
        finally:
            os.unlink(tmp.name)

def test_send_file_with_custom_etag():
    """Test send_file with a custom etag string."""
    app = Flask(__name__)
    
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(b"Test content")
        tmp.flush()
        
        try:
            with app.test_request_context():
                response = send_file(
                    path_or_file=tmp.name,
                    mimetype='text/plain',
                    etag='custom-etag-value'
                )
                
                assert response.status_code == 200
                # ETag values are wrapped in quotes
                assert response.headers.get('ETag') == '"custom-etag-value"'
        finally:
            os.unlink(tmp.name)

def test_send_file_with_last_modified_datetime():
    """Test send_file with a datetime object for last_modified."""
    app = Flask(__name__)
    
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(b"Test content")
        tmp.flush()
        
        try:
            with app.test_request_context():
                last_mod = datetime(2023, 1, 1, 12, 0, 0)
                response = send_file(
                    path_or_file=tmp.name,
                    mimetype='text/plain',
                    last_modified=last_mod
                )
                
                assert response.status_code == 200
                # Werkzeug formats the datetime in HTTP format
                assert 'Sun, 01 Jan 2023 12:00:00 GMT' in response.headers.get('Last-Modified', '')
        finally:
            os.unlink(tmp.name)

def test_send_file_with_max_age_callable():
    """Test send_file with a callable for max_age."""
    app = Flask(__name__)
    
    def max_age_callback(filename):
        return 3600  # 1 hour
    
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(b"Test content")
        tmp.flush()
        
        try:
            with app.test_request_context():
                response = send_file(
                    path_or_file=tmp.name,
                    mimetype='text/plain',
                    max_age=max_age_callback
                )
                
                assert response.status_code == 200
                assert 'max-age=3600' in response.headers.get('Cache-Control', '')
        finally:
            os.unlink(tmp.name)

def test_send_file_with_max_age_int():
    """Test send_file with an integer for max_age."""
    app = Flask(__name__)
    
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(b"Test content")
        tmp.flush()
        
        try:
            with app.test_request_context():
                response = send_file(
                    path_or_file=tmp.name,
                    mimetype='text/plain',
                    max_age=1800  # 30 minutes
                )
                
                assert response.status_code == 200
                assert 'max-age=1800' in response.headers.get('Cache-Control', '')
        finally:
            os.unlink(tmp.name)

def test_send_file_inline_with_download_name():
    """Test send_file with as_attachment=False but with download_name."""
    app = Flask(__name__)
    
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(b"Test content")
        tmp.flush()
        
        try:
            with app.test_request_context():
                response = send_file(
                    path_or_file=tmp.name,
                    mimetype='text/plain',
                    as_attachment=False,
                    download_name='display.txt'
                )
                
                assert response.status_code == 200
                content_disp = response.headers.get('Content-Disposition', '')
                assert 'inline' in content_disp
                assert 'display.txt' in content_disp
        finally:
            os.unlink(tmp.name)

def test_send_file_with_app_default_max_age():
    """Test send_file when max_age is None and uses app default."""
    app = Flask(__name__)
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 7200  # 2 hours
    
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(b"Test content")
        tmp.flush()
        
        try:
            with app.test_request_context():
                response = send_file(
                    path_or_file=tmp.name,
                    mimetype='text/plain',
                    max_age=None  # Should use app default
                )
                
                assert response.status_code == 200
                assert 'max-age=7200' in response.headers.get('Cache-Control', '')
        finally:
            os.unlink(tmp.name)
