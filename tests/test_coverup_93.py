# file: src/flask/src/flask/app.py:1121-1261
# asked: {"lines": [1121, 1178, 1179, 1182, 1183, 1186, 1187, 1189, 1190, 1191, 1193, 1196, 1197, 1203, 1204, 1205, 1211, 1212, 1216, 1217, 1218, 1219, 1221, 1222, 1223, 1224, 1227, 1228, 1229, 1230, 1232, 1233, 1234, 1238, 1239, 1241, 1242, 1246, 1249, 1251, 1252, 1253, 1255, 1258, 1259, 1261], "branches": [[1182, 1183], [1182, 1203], [1186, 1187], [1186, 1189], [1189, 1190], [1189, 1196], [1190, 1191], [1190, 1193], [1203, 1204], [1203, 1211], [1211, 1212], [1211, 1249], [1212, 1216], [1212, 1222], [1222, 1223], [1222, 1224], [1224, 1227], [1224, 1241], [1251, 1252], [1251, 1258], [1252, 1253], [1252, 1255], [1258, 1259], [1258, 1261]]}
# gained: {"lines": [1121, 1178, 1179, 1182, 1183, 1186, 1187, 1189, 1190, 1191, 1193, 1196, 1197, 1203, 1204, 1205, 1211, 1212, 1216, 1217, 1218, 1219, 1221, 1222, 1223, 1224, 1227, 1228, 1229, 1230, 1241, 1242, 1246, 1249, 1251, 1252, 1255, 1258, 1259, 1261], "branches": [[1182, 1183], [1182, 1203], [1186, 1187], [1186, 1189], [1189, 1190], [1189, 1196], [1190, 1191], [1190, 1193], [1203, 1204], [1203, 1211], [1211, 1212], [1211, 1249], [1212, 1216], [1212, 1222], [1222, 1223], [1222, 1224], [1224, 1227], [1224, 1241], [1251, 1252], [1251, 1258], [1252, 1255], [1258, 1259], [1258, 1261]]}

import pytest
from flask import Flask, Response
from werkzeug.wrappers import Response as BaseResponse
from werkzeug.datastructures import Headers
import typing as t
from unittest.mock import Mock, MagicMock


class TestFlaskMakeResponse:
    """Test cases for Flask.make_response method to achieve full coverage."""

    def test_make_response_with_3_tuple(self):
        """Test make_response with 3-tuple (body, status, headers)."""
        app = Flask(__name__)
        
        with app.test_request_context():
            # Test with 3-tuple: (body, status, headers)
            body = "test body"
            status = 201
            headers = {"X-Test": "value"}
            
            response = app.make_response((body, status, headers))
            
            assert response.get_data(as_text=True) == body
            assert response.status_code == status
            assert response.headers["X-Test"] == "value"

    def test_make_response_with_2_tuple_body_status(self):
        """Test make_response with 2-tuple (body, status)."""
        app = Flask(__name__)
        
        with app.test_request_context():
            # Test with 2-tuple: (body, status)
            body = "test body"
            status = 404
            
            response = app.make_response((body, status))
            
            assert response.get_data(as_text=True) == body
            assert response.status_code == status

    def test_make_response_with_2_tuple_body_headers(self):
        """Test make_response with 2-tuple (body, headers)."""
        app = Flask(__name__)
        
        with app.test_request_context():
            # Test with 2-tuple: (body, headers)
            body = "test body"
            headers = {"X-Custom": "header"}
            
            response = app.make_response((body, headers))
            
            assert response.get_data(as_text=True) == body
            assert response.headers["X-Custom"] == "header"

    def test_make_response_with_invalid_tuple_length(self):
        """Test make_response with invalid tuple length raises TypeError."""
        app = Flask(__name__)
        
        with app.test_request_context():
            # Test with invalid tuple length (4-tuple)
            with pytest.raises(TypeError, match="The view function did not return a valid response tuple"):
                app.make_response(("body", 200, {}, "extra"))

    def test_make_response_with_none_rv(self):
        """Test make_response with None raises TypeError."""
        app = Flask(__name__)
        
        with app.test_request_context():
            with pytest.raises(TypeError, match="did not return a valid response"):
                app.make_response(None)

    def test_make_response_with_bytes(self):
        """Test make_response with bytes body."""
        app = Flask(__name__)
        
        with app.test_request_context():
            body = b"test bytes"
            response = app.make_response(body)
            
            assert response.get_data() == body

    def test_make_response_with_bytearray(self):
        """Test make_response with bytearray body."""
        app = Flask(__name__)
        
        with app.test_request_context():
            body = bytearray(b"test bytearray")
            response = app.make_response(body)
            
            assert response.get_data() == bytes(body)

    def test_make_response_with_iterator(self):
        """Test make_response with iterator body."""
        app = Flask(__name__)
        
        with app.test_request_context():
            def body_generator():
                yield "part1"
                yield "part2"
            
            response = app.make_response(body_generator())
            
            # Streaming response should have the iterator
            assert response.is_streamed

    def test_make_response_with_dict(self):
        """Test make_response with dict body."""
        app = Flask(__name__)
        
        with app.test_request_context():
            body = {"key": "value"}
            response = app.make_response(body)
            
            assert response.mimetype == "application/json"
            assert response.get_json() == body

    def test_make_response_with_list(self):
        """Test make_response with list body."""
        app = Flask(__name__)
        
        with app.test_request_context():
            body = [1, 2, 3]
            response = app.make_response(body)
            
            assert response.mimetype == "application/json"
            assert response.get_json() == body

    def test_make_response_with_base_response(self):
        """Test make_response with BaseResponse instance."""
        app = Flask(__name__)
        
        with app.test_request_context():
            base_response = BaseResponse("test", status=201)
            response = app.make_response(base_response)
            
            assert isinstance(response, Response)
            assert response.get_data(as_text=True) == "test"
            assert response.status_code == 201

    def test_make_response_with_callable(self):
        """Test make_response with WSGI callable."""
        app = Flask(__name__)
        
        with app.test_request_context():
            def wsgi_app(environ, start_response):
                start_response("200 OK", [("Content-Type", "text/plain")])
                return [b"wsgi response"]
            
            response = app.make_response(wsgi_app)
            
            assert isinstance(response, Response)
            assert response.get_data(as_text=True) == "wsgi response"

    def test_make_response_with_invalid_type(self):
        """Test make_response with invalid type raises TypeError."""
        app = Flask(__name__)
        
        with app.test_request_context():
            with pytest.raises(TypeError, match="did not return a valid response"):
                app.make_response(123)  # int is not a valid response type

    def test_make_response_with_status_string(self):
        """Test make_response with string status."""
        app = Flask(__name__)
        
        with app.test_request_context():
            response = app.make_response(("test", "201 CREATED"))
            
            assert response.status == "201 CREATED"

    def test_make_response_with_status_int(self):
        """Test make_response with integer status."""
        app = Flask(__name__)
        
        with app.test_request_context():
            response = app.make_response(("test", 201))
            
            assert response.status_code == 201

    def test_make_response_with_headers_dict(self):
        """Test make_response with headers as dict."""
        app = Flask(__name__)
        
        with app.test_request_context():
            headers = {"X-Test": "value", "X-Another": "test"}
            response = app.make_response(("test", headers))
            
            assert response.headers["X-Test"] == "value"
            assert response.headers["X-Another"] == "test"

    def test_make_response_with_headers_list(self):
        """Test make_response with headers as list of tuples."""
        app = Flask(__name__)
        
        with app.test_request_context():
            headers = [("X-Test", "value"), ("X-Another", "test")]
            response = app.make_response(("test", headers))
            
            assert response.headers["X-Test"] == "value"
            assert response.headers["X-Another"] == "test"

    def test_make_response_with_headers_tuple(self):
        """Test make_response with headers as tuple of tuples."""
        app = Flask(__name__)
        
        with app.test_request_context():
            headers = (("X-Test", "value"), ("X-Another", "test"))
            response = app.make_response(("test", headers))
            
            assert response.headers["X-Test"] == "value"
            assert response.headers["X-Another"] == "test"

    def test_make_response_with_headers_werkzeug_headers(self):
        """Test make_response with headers as werkzeug Headers object."""
        app = Flask(__name__)
        
        with app.test_request_context():
            headers = Headers([("X-Test", "value")])
            response = app.make_response(("test", headers))
            
            assert response.headers["X-Test"] == "value"

    def test_make_response_with_status_and_headers(self):
        """Test make_response with both status and headers provided."""
        app = Flask(__name__)
        
        with app.test_request_context():
            response = app.make_response(("test", 201, {"X-Test": "value"}))
            
            assert response.get_data(as_text=True) == "test"
            assert response.status_code == 201
            assert response.headers["X-Test"] == "value"

    def test_make_response_with_existing_response_and_status(self):
        """Test make_response with existing Response and status override."""
        app = Flask(__name__)
        
        with app.test_request_context():
            existing_response = Response("original", status=200)
            response = app.make_response((existing_response, 201))
            
            assert response.get_data(as_text=True) == "original"
            assert response.status_code == 201

    def test_make_response_with_existing_response_and_headers(self):
        """Test make_response with existing Response and headers extension."""
        app = Flask(__name__)
        
        with app.test_request_context():
            existing_response = Response("original")
            existing_response.headers["X-Existing"] = "existing"
            response = app.make_response((existing_response, {"X-New": "new"}))
            
            assert response.get_data(as_text=True) == "original"
            assert response.headers["X-Existing"] == "existing"
            assert response.headers["X-New"] == "new"

    def test_make_response_with_existing_response_status_and_headers(self):
        """Test make_response with existing Response, status and headers."""
        app = Flask(__name__)
        
        with app.test_request_context():
            existing_response = Response("original", status=200)
            existing_response.headers["X-Existing"] = "existing"
            response = app.make_response((existing_response, 201, {"X-New": "new"}))
            
            assert response.get_data(as_text=True) == "original"
            assert response.status_code == 201
            assert response.headers["X-Existing"] == "existing"
            assert response.headers["X-New"] == "new"

    def test_make_response_force_type_exception(self):
        """Test make_response when force_type raises TypeError."""
        app = Flask(__name__)
        
        with app.test_request_context():
            # Create a mock object that will raise TypeError when force_type is called
            class InvalidResponse:
                pass
            
            invalid_response = InvalidResponse()
            
            with pytest.raises(TypeError, match="The view function did not return a valid response"):
                app.make_response(invalid_response)
