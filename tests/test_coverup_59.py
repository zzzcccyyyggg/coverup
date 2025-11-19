# file: src/flask/src/flask/app.py:1291-1317
# asked: {"lines": [1291, 1304, 1306, 1307, 1309, 1310, 1311, 1312, 1314, 1315, 1317], "branches": [[1306, 1307], [1306, 1309], [1309, 1310], [1309, 1314], [1310, 1309], [1310, 1311], [1311, 1309], [1311, 1312], [1314, 1315], [1314, 1317]]}
# gained: {"lines": [1291, 1304, 1306, 1307, 1309, 1310, 1311, 1312, 1314, 1315, 1317], "branches": [[1306, 1307], [1306, 1309], [1309, 1310], [1309, 1314], [1310, 1309], [1310, 1311], [1311, 1309], [1311, 1312], [1314, 1315], [1314, 1317]]}

import pytest
from flask import Flask, Response
from flask.globals import _cv_app
from unittest.mock import Mock, patch

class TestFlaskProcessResponse:
    def test_process_response_with_after_request_functions(self):
        """Test process_response with _after_request_functions in context"""
        app = Flask(__name__)
        
        # Mock the context and its attributes
        mock_ctx = Mock()
        mock_ctx._after_request_functions = []
        mock_ctx.request = Mock()
        mock_ctx.request.blueprints = []
        mock_ctx.session = Mock()
        
        # Mock session interface to return True for is_null_session
        mock_session_interface = Mock()
        mock_session_interface.is_null_session.return_value = True
        app.session_interface = mock_session_interface
        
        # Set the context directly using _cv_app.set()
        token = _cv_app.set(mock_ctx)
        try:
            response = Response()
            result = app.process_response(response)
            
            assert result == response
            mock_session_interface.is_null_session.assert_called_once_with(mock_ctx.session)
            mock_session_interface.save_session.assert_not_called()
        finally:
            _cv_app.reset(token)

    def test_process_response_with_blueprint_after_request_funcs(self):
        """Test process_response with blueprint after_request functions"""
        app = Flask(__name__)
        
        # Mock the context and its attributes
        mock_ctx = Mock()
        mock_ctx._after_request_functions = []
        mock_ctx.request = Mock()
        mock_ctx.request.blueprints = ['test_blueprint']
        mock_ctx.session = Mock()
        
        # Set up after_request_funcs for the blueprint
        app.after_request_funcs = {'test_blueprint': []}
        
        # Mock session interface to return True for is_null_session
        mock_session_interface = Mock()
        mock_session_interface.is_null_session.return_value = True
        app.session_interface = mock_session_interface
        
        # Set the context directly using _cv_app.set()
        token = _cv_app.set(mock_ctx)
        try:
            response = Response()
            result = app.process_response(response)
            
            assert result == response
            mock_session_interface.is_null_session.assert_called_once_with(mock_ctx.session)
            mock_session_interface.save_session.assert_not_called()
        finally:
            _cv_app.reset(token)

    def test_process_response_with_non_null_session(self):
        """Test process_response when session is not null"""
        app = Flask(__name__)
        
        # Mock the context and its attributes
        mock_ctx = Mock()
        mock_ctx._after_request_functions = []
        mock_ctx.request = Mock()
        mock_ctx.request.blueprints = []
        mock_ctx.session = Mock()
        
        # Mock session interface to return False for is_null_session
        mock_session_interface = Mock()
        mock_session_interface.is_null_session.return_value = False
        app.session_interface = mock_session_interface
        
        # Set the context directly using _cv_app.set()
        token = _cv_app.set(mock_ctx)
        try:
            response = Response()
            result = app.process_response(response)
            
            assert result == response
            mock_session_interface.is_null_session.assert_called_once_with(mock_ctx.session)
            mock_session_interface.save_session.assert_called_once_with(app, mock_ctx.session, response)
        finally:
            _cv_app.reset(token)

    def test_process_response_with_after_request_functions_modifying_response(self):
        """Test process_response with _after_request_functions that modify response"""
        app = Flask(__name__)
        
        def modify_response1(response):
            response.headers['X-Test-1'] = 'value1'
            return response
            
        def modify_response2(response):
            response.headers['X-Test-2'] = 'value2'
            return response
        
        # Mock the context and its attributes
        mock_ctx = Mock()
        mock_ctx._after_request_functions = [modify_response1, modify_response2]
        mock_ctx.request = Mock()
        mock_ctx.request.blueprints = []
        mock_ctx.session = Mock()
        
        # Mock session interface to return True for is_null_session
        mock_session_interface = Mock()
        mock_session_interface.is_null_session.return_value = True
        app.session_interface = mock_session_interface
        
        # Set the context directly using _cv_app.set()
        token = _cv_app.set(mock_ctx)
        try:
            response = Response()
            result = app.process_response(response)
            
            assert result == response
            assert result.headers['X-Test-1'] == 'value1'
            assert result.headers['X-Test-2'] == 'value2'
            mock_session_interface.is_null_session.assert_called_once_with(mock_ctx.session)
            mock_session_interface.save_session.assert_not_called()
        finally:
            _cv_app.reset(token)

    def test_process_response_with_blueprint_after_request_reversed_order(self):
        """Test process_response with blueprint after_request functions in reverse order"""
        app = Flask(__name__)
        
        call_order = []
        
        def blueprint_func1(response):
            call_order.append(1)
            return response
            
        def blueprint_func2(response):
            call_order.append(2)
            return response
        
        # Mock the context and its attributes
        mock_ctx = Mock()
        mock_ctx._after_request_functions = []
        mock_ctx.request = Mock()
        mock_ctx.request.blueprints = ['test_blueprint']
        mock_ctx.session = Mock()
        
        # Set up after_request_funcs for the blueprint in specific order
        app.after_request_funcs = {'test_blueprint': [blueprint_func1, blueprint_func2]}
        
        # Mock session interface to return True for is_null_session
        mock_session_interface = Mock()
        mock_session_interface.is_null_session.return_value = True
        app.session_interface = mock_session_interface
        
        # Set the context directly using _cv_app.set()
        token = _cv_app.set(mock_ctx)
        try:
            response = Response()
            result = app.process_response(response)
            
            assert result == response
            # Functions should be called in reverse order: 2 then 1
            assert call_order == [2, 1]
            mock_session_interface.is_null_session.assert_called_once_with(mock_ctx.session)
            mock_session_interface.save_session.assert_not_called()
        finally:
            _cv_app.reset(token)

    def test_process_response_with_global_after_request_funcs(self):
        """Test process_response with global after_request functions (None blueprint)"""
        app = Flask(__name__)
        
        call_order = []
        
        def global_func1(response):
            call_order.append(1)
            return response
            
        def global_func2(response):
            call_order.append(2)
            return response
        
        # Mock the context and its attributes
        mock_ctx = Mock()
        mock_ctx._after_request_functions = []
        mock_ctx.request = Mock()
        mock_ctx.request.blueprints = []
        mock_ctx.session = Mock()
        
        # Set up after_request_funcs for None (global) in specific order
        app.after_request_funcs = {None: [global_func1, global_func2]}
        
        # Mock session interface to return True for is_null_session
        mock_session_interface = Mock()
        mock_session_interface.is_null_session.return_value = True
        app.session_interface = mock_session_interface
        
        # Set the context directly using _cv_app.set()
        token = _cv_app.set(mock_ctx)
        try:
            response = Response()
            result = app.process_response(response)
            
            assert result == response
            # Functions should be called in reverse order: 2 then 1
            assert call_order == [2, 1]
            mock_session_interface.is_null_session.assert_called_once_with(mock_ctx.session)
            mock_session_interface.save_session.assert_not_called()
        finally:
            _cv_app.reset(token)
