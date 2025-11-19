# file: src/flask/src/flask/sansio/scaffold.py:558-581
# asked: {"lines": [558, 559, 580, 581], "branches": []}
# gained: {"lines": [558, 559, 580, 581], "branches": []}

import pytest
from flask.sansio.scaffold import Scaffold
from typing import Dict, Any

class TestScaffold(Scaffold):
    """Test subclass that implements _check_setup_finished to avoid NotImplementedError"""
    
    def _check_setup_finished(self, f_name: str) -> None:
        # Override to avoid NotImplementedError during testing
        pass

def test_url_value_preprocessor_registration():
    """Test that url_value_preprocessor registers a function correctly."""
    
    scaffold = TestScaffold(__name__)
    
    # Track calls to the preprocessor
    calls = []
    
    def test_preprocessor(endpoint: str, values: Dict[str, Any]) -> None:
        calls.append((endpoint, values))
    
    # Register the preprocessor
    registered_func = scaffold.url_value_preprocessor(test_preprocessor)
    
    # Verify the function was returned unchanged
    assert registered_func is test_preprocessor
    
    # Verify the preprocessor was added to the None key in url_value_preprocessors
    assert len(scaffold.url_value_preprocessors[None]) == 1
    assert scaffold.url_value_preprocessors[None][0] is test_preprocessor
    
    # Test that the preprocessor can be called (simulate what Flask would do)
    test_endpoint = "test_endpoint"
    test_values = {"id": 123, "name": "test"}
    scaffold.url_value_preprocessors[None][0](test_endpoint, test_values)
    
    # Verify the preprocessor was called with correct arguments
    assert len(calls) == 1
    assert calls[0] == (test_endpoint, test_values)

def test_url_value_preprocessor_multiple_registrations():
    """Test that multiple url_value_preprocessors can be registered."""
    
    scaffold = TestScaffold(__name__)
    
    calls1 = []
    calls2 = []
    
    def preprocessor1(endpoint: str, values: Dict[str, Any]) -> None:
        calls1.append((endpoint, values))
    
    def preprocessor2(endpoint: str, values: Dict[str, Any]) -> None:
        calls2.append((endpoint, values))
    
    # Register multiple preprocessors
    scaffold.url_value_preprocessor(preprocessor1)
    scaffold.url_value_preprocessor(preprocessor2)
    
    # Verify both preprocessors were registered
    assert len(scaffold.url_value_preprocessors[None]) == 2
    assert scaffold.url_value_preprocessors[None][0] is preprocessor1
    assert scaffold.url_value_preprocessors[None][1] is preprocessor2
    
    # Test calling all preprocessors
    test_endpoint = "multi_endpoint"
    test_values = {"multi": "test"}
    
    for preprocessor in scaffold.url_value_preprocessors[None]:
        preprocessor(test_endpoint, test_values)
    
    # Verify both were called
    assert len(calls1) == 1
    assert calls1[0] == (test_endpoint, test_values)
    assert len(calls2) == 1
    assert calls2[0] == (test_endpoint, test_values)

def test_url_value_preprocessor_modifies_values():
    """Test that url_value_preprocessor can modify the values dict."""
    
    scaffold = TestScaffold(__name__)
    
    def modifying_preprocessor(endpoint: str, values: Dict[str, Any]) -> None:
        # Modify the values in place (this is the intended use case)
        if "id" in values:
            values["id"] = values["id"] * 2
        values["processed"] = True
    
    # Register the preprocessor
    scaffold.url_value_preprocessor(modifying_preprocessor)
    
    # Test with values that should be modified
    test_values = {"id": 5, "name": "test"}
    scaffold.url_value_preprocessors[None][0]("modify_endpoint", test_values)
    
    # Verify values were modified
    assert test_values["id"] == 10  # doubled
    assert test_values["name"] == "test"  # unchanged
    assert test_values["processed"] is True  # added
