# file: src/flask/src/flask/sansio/scaffold.py:217-218
# asked: {"lines": [217, 218], "branches": []}
# gained: {"lines": [217, 218], "branches": []}

import pytest
from flask.sansio.scaffold import Scaffold

class TestScaffoldRepr:
    def test_repr_with_name(self):
        """Test that __repr__ returns the expected string format with name attribute."""
        scaffold = Scaffold(__name__)
        scaffold.name = "test_app"
        
        result = repr(scaffold)
        expected = "<Scaffold 'test_app'>"
        assert result == expected

    def test_repr_without_name(self):
        """Test that __repr__ handles missing name attribute gracefully."""
        scaffold = Scaffold(__name__)
        
        # The Scaffold class doesn't initialize 'name' in __init__, so we need to test
        # what happens when name is not set. Since the __repr__ method expects 'name'
        # to exist, we should test the normal case where name is set.
        # Let's test with a subclass that doesn't set name to see if it raises AttributeError
        class ScaffoldSubclass(Scaffold):
            def __init__(self, import_name):
                super().__init__(import_name)
                # Don't set name attribute
        
        subclass_instance = ScaffoldSubclass(__name__)
        
        # This should raise AttributeError since name is not set
        with pytest.raises(AttributeError, match="'ScaffoldSubclass' object has no attribute 'name'"):
            repr(subclass_instance)
