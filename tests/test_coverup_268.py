# file: src/flask/src/flask/sansio/scaffold.py:303-309
# asked: {"lines": [303, 304, 309], "branches": []}
# gained: {"lines": [303, 304, 309], "branches": []}

import pytest
import typing as t
from flask.sansio.scaffold import Scaffold

class MockScaffold(Scaffold):
    """Mock Scaffold that bypasses setup checks for testing."""
    
    def __init__(self, import_name: str):
        super().__init__(import_name)
        # Set up minimal attributes needed to bypass _check_setup_finished
        self.name = import_name
        self._got_first_request = False
    
    def _check_setup_finished(self, f_name: str) -> None:
        """Override to bypass the NotImplementedError for testing."""
        pass

class TestScaffoldPostMethod:
    """Test cases for Scaffold.post method to achieve full coverage."""
    
    def test_post_method_decorator(self, monkeypatch):
        """Test that post method calls _method_route with correct parameters."""
        # Create a mock Scaffold instance
        scaffold = MockScaffold(import_name='test_app')
        
        # Mock the _method_route method to track calls
        mock_calls = []
        def mock_method_route(method, rule, options):
            mock_calls.append((method, rule, options))
            return lambda f: f
        
        monkeypatch.setattr(scaffold, '_method_route', mock_method_route)
        
        # Test the post decorator
        @scaffold.post('/test', endpoint='test_endpoint')
        def test_view():
            return "test response"
        
        # Verify _method_route was called with correct parameters
        assert len(mock_calls) == 1
        method, rule, options = mock_calls[0]
        assert method == 'POST'
        assert rule == '/test'
        assert options == {'endpoint': 'test_endpoint'}
        assert callable(test_view)
    
    def test_post_method_without_options(self, monkeypatch):
        """Test post method without additional options."""
        scaffold = MockScaffold(import_name='test_app')
        
        mock_calls = []
        def mock_method_route(method, rule, options):
            mock_calls.append((method, rule, options))
            return lambda f: f
        
        monkeypatch.setattr(scaffold, '_method_route', mock_method_route)
        
        # Test with just the rule
        @scaffold.post('/simple')
        def simple_view():
            return "simple"
        
        assert len(mock_calls) == 1
        method, rule, options = mock_calls[0]
        assert method == 'POST'
        assert rule == '/simple'
        assert options == {}
        assert callable(simple_view)
