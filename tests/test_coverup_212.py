# file: src/flask/src/flask/views.py:78-83
# asked: {"lines": [78, 83], "branches": []}
# gained: {"lines": [78, 83], "branches": []}

import pytest
from flask import Flask
from flask.views import View


class TestViewDispatchRequest:
    """Test cases for View.dispatch_request method."""
    
    def test_dispatch_request_not_implemented(self):
        """Test that dispatch_request raises NotImplementedError when called directly."""
        view = View()
        
        with pytest.raises(NotImplementedError):
            view.dispatch_request()
