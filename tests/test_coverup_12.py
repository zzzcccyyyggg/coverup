# file: src/flask/src/flask/views.py:85-135
# asked: {"lines": [85, 86, 104, 106, 107, 108, 110, 113, 115, 116, 118, 119, 120, 121, 122, 129, 130, 131, 132, 133, 134, 135], "branches": [[104, 106], [104, 113], [118, 119], [118, 129], [121, 122], [121, 129]]}
# gained: {"lines": [85, 86, 104, 106, 107, 108, 110, 113, 115, 116, 118, 119, 120, 121, 122, 129, 130, 131, 132, 133, 134, 135], "branches": [[104, 106], [104, 113], [118, 119], [118, 129], [121, 122], [121, 129]]}

import pytest
from flask import Flask
from flask.views import View
from typing import ClassVar, Collection, List, Callable, Any


class TestView:
    """Test class for View.as_view method coverage"""

    def test_as_view_init_every_request_true(self):
        """Test as_view when init_every_request is True"""
        class TestViewClass(View):
            init_every_request = True
            methods = ['GET', 'POST']
            provide_automatic_options = False
            
            def __init__(self, custom_arg=None):
                self.custom_arg = custom_arg
                
            def dispatch_request(self, **kwargs):
                return f"Response with custom_arg: {self.custom_arg}"

        view_func = TestViewClass.as_view('test_view', 'test_value')
        
        # Test that view function is created correctly
        assert view_func.__name__ == 'test_view'
        assert view_func.view_class == TestViewClass
        assert view_func.methods == ['GET', 'POST']
        assert view_func.provide_automatic_options == False
        
        # Test that view function creates new instance for each call
        app = Flask(__name__)
        with app.test_request_context():
            response1 = view_func()
            response2 = view_func()
            
        # Each call should create a new instance
        assert "test_value" in response1
        assert "test_value" in response2

    def test_as_view_init_every_request_false(self):
        """Test as_view when init_every_request is False"""
        class TestViewClass(View):
            init_every_request = False
            methods = ['PUT', 'DELETE']
            provide_automatic_options = True
            
            def __init__(self, shared_value=None):
                self.shared_value = shared_value
                self.call_count = 0
                
            def dispatch_request(self, **kwargs):
                self.call_count += 1
                return f"Shared: {self.shared_value}, Calls: {self.call_count}"

        view_func = TestViewClass.as_view('shared_view', 'persistent_value')
        
        # Test that view function is created correctly
        assert view_func.__name__ == 'shared_view'
        assert view_func.view_class == TestViewClass
        assert view_func.methods == ['PUT', 'DELETE']
        assert view_func.provide_automatic_options == True
        
        # Test that view function uses same instance for multiple calls
        app = Flask(__name__)
        with app.test_request_context():
            response1 = view_func()
            response2 = view_func()
            
        # Same instance should be reused, so call_count should increment
        assert "persistent_value" in response1
        assert "persistent_value" in response2
        assert "Calls: 1" in response1
        assert "Calls: 2" in response2

    def test_as_view_with_decorators(self):
        """Test as_view with decorators applied"""
        def decorator1(func):
            def wrapper(**kwargs):
                result = func(**kwargs)
                return f"Decorator1: {result}"
            return wrapper

        def decorator2(func):
            def wrapper(**kwargs):
                result = func(**kwargs)
                return f"Decorator2: {result}"
            return wrapper

        class TestViewClass(View):
            init_every_request = True
            decorators = [decorator1, decorator2]
            
            def dispatch_request(self, **kwargs):
                return "Original response"

        view_func = TestViewClass.as_view('decorated_view')
        
        # Test that decorators are applied
        app = Flask(__name__)
        with app.test_request_context():
            response = view_func()
            
        assert response == "Decorator2: Decorator1: Original response"

    def test_as_view_with_class_args_kwargs(self):
        """Test as_view with class arguments and keyword arguments"""
        class TestViewClass(View):
            init_every_request = True
            
            def __init__(self, arg1, arg2, kwarg1=None, kwarg2=None):
                self.arg1 = arg1
                self.arg2 = arg2
                self.kwarg1 = kwarg1
                self.kwarg2 = kwarg2
                
            def dispatch_request(self, **kwargs):
                return f"Args: {self.arg1}, {self.arg2}, Kwargs: {self.kwarg1}, {self.kwarg2}"

        view_func = TestViewClass.as_view(
            'args_view', 
            'positional1', 
            'positional2', 
            kwarg1='keyword1', 
            kwarg2='keyword2'
        )
        
        app = Flask(__name__)
        with app.test_request_context():
            response = view_func()
            
        assert "positional1" in response
        assert "positional2" in response
        assert "keyword1" in response
        assert "keyword2" in response

    def test_as_view_doc_and_module_attributes(self):
        """Test that view function inherits doc and module from class"""
        class TestViewClass(View):
            """Test view class documentation"""
            init_every_request = True
            
            def dispatch_request(self, **kwargs):
                return "Response"

        view_func = TestViewClass.as_view('doc_view')
        
        assert view_func.__doc__ == "Test view class documentation"
        assert view_func.__module__ == TestViewClass.__module__
