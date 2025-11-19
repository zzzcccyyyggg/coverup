# file: src/flask/src/flask/debughelpers.py:107-121
# asked: {"lines": [107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121], "branches": [[109, 0], [109, 110], [110, 111], [110, 112], [112, 113], [112, 119], [113, 114], [113, 115], [116, 117], [116, 118], [119, 120], [119, 121]]}
# gained: {"lines": [107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121], "branches": [[109, 0], [109, 110], [110, 111], [110, 112], [112, 113], [112, 119], [113, 114], [113, 115], [116, 117], [116, 118], [119, 120], [119, 121]]}

import pytest
from jinja2.loaders import BaseLoader
from flask.debughelpers import _dump_loader_info

class TestLoader(BaseLoader):
    def __init__(self):
        self.public_str = "test_string"
        self.public_int = 42
        self.public_float = 3.14
        self.public_bool = True
        self._private_attr = "should_be_ignored"
        self.list_of_strings = ["item1", "item2", "item3"]
        self.list_with_non_strings = ["item1", 123, "item3"]
        self.tuple_of_strings = ("tuple1", "tuple2")
        self.complex_object = {"key": "value"}

    def get_source(self, environment, template):
        return "test source", "test.html", lambda: True

def test_dump_loader_info_comprehensive():
    """Test _dump_loader_info with all attribute types to cover all code paths."""
    loader = TestLoader()
    result = list(_dump_loader_info(loader))
    
    # Check class info
    assert any("class: " in line for line in result)
    
    # Check public string attribute
    assert any("public_str: 'test_string'" in line for line in result)
    
    # Check public int attribute
    assert any("public_int: 42" in line for line in result)
    
    # Check public float attribute
    assert any("public_float: 3.14" in line for line in result)
    
    # Check public bool attribute
    assert any("public_bool: True" in line for line in result)
    
    # Check list of strings
    assert any("list_of_strings:" in line for line in result)
    assert any("  - item1" in line for line in result)
    assert any("  - item2" in line for line in result)
    assert any("  - item3" in line for line in result)
    
    # Check tuple of strings
    assert any("tuple_of_strings:" in line for line in result)
    assert any("  - tuple1" in line for line in result)
    assert any("  - tuple2" in line for line in result)
    
    # Verify private attributes are ignored
    assert not any("_private_attr" in line for line in result)
    
    # Verify list with non-strings is ignored
    assert not any("list_with_non_strings:" in line for line in result)
    
    # Verify complex objects are ignored
    assert not any("complex_object" in line for line in result)

def test_dump_loader_info_empty_loader():
    """Test _dump_loader_info with a loader that has no public attributes."""
    class EmptyLoader(BaseLoader):
        def get_source(self, environment, template):
            return "test source", "test.html", lambda: True
    
    loader = EmptyLoader()
    result = list(_dump_loader_info(loader))
    
    # Should only contain class info
    assert len(result) == 1
    assert "class: " in result[0]

def test_dump_loader_info_only_private_attrs():
    """Test _dump_loader_info with a loader that only has private attributes."""
    class PrivateLoader(BaseLoader):
        def __init__(self):
            self._private1 = "private1"
            self.__private2 = "private2"
        
        def get_source(self, environment, template):
            return "test source", "test.html", lambda: True
    
    loader = PrivateLoader()
    result = list(_dump_loader_info(loader))
    
    # Should only contain class info
    assert len(result) == 1
    assert "class: " in result[0]
