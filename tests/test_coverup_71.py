# file: src/flask/src/flask/sansio/app.py:422-437
# asked: {"lines": [422, 423, 432, 433, 434, 435, 436, 437], "branches": [[432, 433], [432, 437], [434, 435], [434, 436]]}
# gained: {"lines": [422, 423, 432, 433, 434, 435, 436, 437], "branches": [[432, 433], [432, 437], [434, 435], [434, 436]]}

import pytest
import sys
import os
from flask import Flask

class TestAppNameProperty:
    """Test cases for the App.name property to achieve full coverage."""
    
    def test_name_with_import_name_not_main(self):
        """Test name property when import_name is not '__main__'."""
        app = Flask("myapp")
        assert app.name == "myapp"
    
    def test_name_with_import_name_main_and_file_exists(self, monkeypatch):
        """Test name property when import_name is '__main__' and __file__ exists."""
        # Mock sys.modules['__main__'] to have a __file__ attribute
        mock_main_module = type('MockModule', (), {'__file__': '/path/to/test_app.py'})()
        monkeypatch.setitem(sys.modules, '__main__', mock_main_module)
        
        app = Flask("__main__")
        assert app.name == "test_app"
        
        # Clean up
        monkeypatch.delitem(sys.modules, '__main__', raising=False)
    
    def test_name_with_import_name_main_and_no_file(self, monkeypatch):
        """Test name property when import_name is '__main__' and __file__ is None."""
        # Mock sys.modules['__main__'] without __file__ attribute
        mock_main_module = type('MockModule', (), {})()
        monkeypatch.setitem(sys.modules, '__main__', mock_main_module)
        
        app = Flask("__main__")
        assert app.name == "__main__"
        
        # Clean up
        monkeypatch.delitem(sys.modules, '__main__', raising=False)
    
    def test_name_with_import_name_main_and_file_none(self, monkeypatch):
        """Test name property when import_name is '__main__' and __file__ is explicitly None."""
        # Mock sys.modules['__main__'] with __file__ set to None
        mock_main_module = type('MockModule', (), {'__file__': None})()
        monkeypatch.setitem(sys.modules, '__main__', mock_main_module)
        
        app = Flask("__main__")
        assert app.name == "__main__"
        
        # Clean up
        monkeypatch.delitem(sys.modules, '__main__', raising=False)
