# file: src/flask/src/flask/sansio/app.py:495-505
# asked: {"lines": [495, 505], "branches": []}
# gained: {"lines": [495, 505], "branches": []}

import pytest
from flask import Flask
from werkzeug.exceptions import Aborter

class TestAppMakeAborter:
    """Test cases for App.make_aborter method."""
    
    def test_make_aborter_returns_default_aborter(self):
        """Test that make_aborter returns an instance of the default aborter_class."""
        app = Flask(__name__)
        aborter = app.make_aborter()
        
        assert isinstance(aborter, Aborter)
        assert aborter is not None
    
    def test_make_aborter_custom_aborter_class(self):
        """Test that make_aborter uses custom aborter_class when set."""
        
        class CustomAborter(Aborter):
            def __init__(self):
                super().__init__()
                self.custom_flag = True
        
        app = Flask(__name__)
        app.aborter_class = CustomAborter
        
        aborter = app.make_aborter()
        
        assert isinstance(aborter, CustomAborter)
        assert aborter.custom_flag is True
        assert isinstance(aborter, Aborter)
