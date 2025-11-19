# file: src/flask/src/flask/testing.py:193-202
# asked: {"lines": [193, 196, 197, 199, 200, 202], "branches": []}
# gained: {"lines": [193, 196, 197, 199, 200, 202], "branches": []}

import pytest
from flask import Flask
from werkzeug.wrappers import Request as BaseRequest
from flask.testing import FlaskClient, EnvironBuilder
from unittest.mock import Mock, patch


class TestFlaskClientRequestFromBuilderArgs:
    """Test cases for FlaskClient._request_from_builder_args method"""
    
    def test_request_from_builder_args_success(self):
        """Test that _request_from_builder_args successfully creates and returns a request"""
        app = Flask(__name__)
        client = FlaskClient(app)
        
        # Mock the EnvironBuilder to control its behavior
        mock_builder = Mock()
        mock_request = Mock(spec=BaseRequest)
        mock_builder.get_request.return_value = mock_request
        
        with patch('flask.testing.EnvironBuilder', return_value=mock_builder):
            # Call the method under test
            result = client._request_from_builder_args(
                args=('/test-path',),
                kwargs={'method': 'GET'}
            )
        
        # Verify the request was returned
        assert result is mock_request
        # Verify builder.close() was called (in finally block)
        mock_builder.close.assert_called_once()
    
    def test_request_from_builder_args_with_environ_base(self):
        """Test that _request_from_builder_args copies environ_base correctly"""
        app = Flask(__name__)
        client = FlaskClient(app)
        
        # Set up initial environ_base on client
        client.environ_base = {'REMOTE_ADDR': '192.168.1.1', 'HTTP_USER_AGENT': 'TestAgent'}
        
        # Mock the EnvironBuilder to capture the arguments passed to it
        captured_kwargs = {}
        mock_builder = Mock()
        mock_request = Mock(spec=BaseRequest)
        mock_builder.get_request.return_value = mock_request
        
        def environ_builder_side_effect(*args, **kwargs):
            captured_kwargs.update(kwargs)
            return mock_builder
        
        with patch('flask.testing.EnvironBuilder', side_effect=environ_builder_side_effect):
            # Call with custom environ_base
            custom_environ = {'HTTP_X_CUSTOM': 'value'}
            result = client._request_from_builder_args(
                args=('/test',),
                kwargs={'environ_base': custom_environ}
            )
        
        # Verify environ_base was copied and merged
        assert 'environ_base' in captured_kwargs
        merged_environ = captured_kwargs['environ_base']
        assert merged_environ['REMOTE_ADDR'] == '192.168.1.1'
        assert merged_environ['HTTP_USER_AGENT'] == 'TestAgent'
        assert merged_environ['HTTP_X_CUSTOM'] == 'value'
        
        # Verify builder.close() was called
        mock_builder.close.assert_called_once()
    
    def test_request_from_builder_args_exception_in_get_request(self):
        """Test that builder.close() is called even when get_request() raises an exception"""
        app = Flask(__name__)
        client = FlaskClient(app)
        
        # Mock the EnvironBuilder to raise an exception in get_request
        mock_builder = Mock()
        mock_builder.get_request.side_effect = RuntimeError("Test exception")
        
        with patch('flask.testing.EnvironBuilder', return_value=mock_builder):
            # Verify that the exception is propagated
            with pytest.raises(RuntimeError, match="Test exception"):
                client._request_from_builder_args(
                    args=('/error-path',),
                    kwargs={}
                )
        
        # Verify builder.close() was called despite the exception (finally block executed)
        mock_builder.close.assert_called_once()
    
    def test_request_from_builder_args_empty_environ_base(self):
        """Test that _request_from_builder_args handles empty environ_base correctly"""
        app = Flask(__name__)
        client = FlaskClient(app)
        
        # Mock the EnvironBuilder to capture the arguments
        captured_kwargs = {}
        mock_builder = Mock()
        mock_request = Mock(spec=BaseRequest)
        mock_builder.get_request.return_value = mock_request
        
        def environ_builder_side_effect(*args, **kwargs):
            captured_kwargs.update(kwargs)
            return mock_builder
        
        with patch('flask.testing.EnvironBuilder', side_effect=environ_builder_side_effect):
            # Call without environ_base
            result = client._request_from_builder_args(
                args=('/test',),
                kwargs={}
            )
        
        # Verify environ_base was created and contains client's environ_base
        assert 'environ_base' in captured_kwargs
        assert captured_kwargs['environ_base'] == client.environ_base
        
        # Verify builder.close() was called
        mock_builder.close.assert_called_once()
