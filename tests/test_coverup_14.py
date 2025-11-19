# file: src/flask/src/flask/config.py:20-47
# asked: {"lines": [20, 21, 23, 24, 26, 27, 29, 30, 32, 33, 35, 36, 37, 39, 41, 42, 44, 46, 47], "branches": [[36, 37], [36, 39], [41, 42], [41, 44]]}
# gained: {"lines": [20, 21, 23, 24, 26, 27, 29, 30, 32, 33, 35, 36, 37, 39, 41, 42, 44, 46, 47], "branches": [[36, 37], [36, 39], [41, 42], [41, 44]]}

import pytest
import typing as t
from flask.config import ConfigAttribute


class MockApp:
    """Mock App class for testing ConfigAttribute."""
    
    def __init__(self):
        self.config = {}


class TestConfigAttribute:
    def test_init_with_converter(self):
        """Test ConfigAttribute initialization with a converter function."""
        def converter(value: t.Any) -> int:
            return int(value)
        
        attr = ConfigAttribute("test_attr", get_converter=converter)
        assert attr.__name__ == "test_attr"
        assert attr.get_converter is converter

    def test_init_without_converter(self):
        """Test ConfigAttribute initialization without a converter function."""
        attr = ConfigAttribute("test_attr")
        assert attr.__name__ == "test_attr"
        assert attr.get_converter is None

    def test_get_descriptor_without_obj(self):
        """Test __get__ when obj is None (descriptor access on class)."""
        attr = ConfigAttribute("test_attr")
        result = attr.__get__(None, None)
        assert result is attr

    def test_get_with_converter(self):
        """Test __get__ with a converter function."""
        def converter(value: t.Any) -> str:
            return f"converted_{value}"
        
        attr = ConfigAttribute("test_attr", get_converter=converter)
        
        class TestApp(MockApp):
            test_attr = attr
            
        app = TestApp()
        app.config["test_attr"] = "value"
        
        result = app.test_attr
        assert result == "converted_value"

    def test_get_without_converter(self):
        """Test __get__ without a converter function."""
        attr = ConfigAttribute("test_attr")
        
        class TestApp(MockApp):
            test_attr = attr
            
        app = TestApp()
        app.config["test_attr"] = "test_value"
        
        result = app.test_attr
        assert result == "test_value"

    def test_set_descriptor(self):
        """Test __set__ descriptor method."""
        attr = ConfigAttribute("test_attr")
        
        class TestApp(MockApp):
            test_attr = attr
            
        app = TestApp()
        app.test_attr = "new_value"
        
        assert app.config["test_attr"] == "new_value"
