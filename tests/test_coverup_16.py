# file: src/flask/src/flask/views.py:165-180
# asked: {"lines": [165, 166, 168, 169, 171, 172, 173, 175, 176, 177, 179, 180], "branches": [[168, 0], [168, 169], [171, 172], [171, 175], [172, 171], [172, 173], [175, 176], [175, 179], [176, 175], [176, 177], [179, 0], [179, 180]]}
# gained: {"lines": [165, 166, 168, 169, 171, 172, 173, 175, 176, 177, 179, 180], "branches": [[168, 0], [168, 169], [171, 172], [171, 175], [172, 171], [172, 173], [175, 176], [175, 179], [176, 175], [176, 177], [179, 0], [179, 180]]}

import pytest
import typing as t
from flask.views import MethodView, http_method_funcs


class TestMethodViewInitSubclass:
    """Test cases for MethodView.__init_subclass__ method to achieve full coverage."""
    
    def test_init_subclass_without_methods_attribute(self):
        """Test when 'methods' is not in cls.__dict__ and no base classes have methods."""
        class TestView(MethodView):
            pass
        
        # Verify that methods attribute was set to None or empty set when no HTTP methods were defined
        # The original code shows that methods is only set if the set is non-empty
        assert not hasattr(TestView, 'methods') or TestView.methods is None or len(TestView.methods) == 0
    
    def test_init_subclass_with_base_class_methods(self):
        """Test when base class has methods attribute."""
        class BaseView(MethodView):
            methods = {'GET', 'POST'}
        
        class TestView(BaseView):
            pass
        
        # Verify that methods from base class are inherited
        assert TestView.methods == {'GET', 'POST'}
    
    def test_init_subclass_with_http_methods_defined(self):
        """Test when class defines HTTP method handlers."""
        class TestView(MethodView):
            def get(self):
                pass
            
            def post(self):
                pass
        
        # Verify that methods are automatically set based on defined HTTP methods
        assert TestView.methods == {'GET', 'POST'}
    
    def test_init_subclass_with_base_methods_and_new_http_methods(self):
        """Test when base class has methods and subclass adds new HTTP methods."""
        class BaseView(MethodView):
            methods = {'GET'}
        
        class TestView(BaseView):
            def post(self):
                pass
        
        # Verify that methods combine base methods and new HTTP methods
        assert TestView.methods == {'GET', 'POST'}
    
    def test_init_subclass_with_existing_methods_attribute(self):
        """Test when 'methods' is already in cls.__dict__ (should not be modified)."""
        original_methods = {'CUSTOM'}
        class TestView(MethodView):
            methods = original_methods
        
        # Verify that existing methods attribute is preserved
        assert TestView.methods == original_methods
    
    def test_init_subclass_with_all_http_methods(self):
        """Test when all possible HTTP methods are defined."""
        class TestView(MethodView):
            def get(self): pass
            def post(self): pass
            def head(self): pass
            def options(self): pass
            def delete(self): pass
            def put(self): pass
            def trace(self): pass
            def patch(self): pass
        
        # Verify that all HTTP methods are included
        expected_methods = {method.upper() for method in http_method_funcs}
        assert TestView.methods == expected_methods
