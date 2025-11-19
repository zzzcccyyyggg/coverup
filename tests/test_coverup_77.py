# file: src/flask/src/flask/globals.py:65-77
# asked: {"lines": [65, 66, 68, 69, 70, 72, 73, 75, 77], "branches": [[68, 69], [68, 77]]}
# gained: {"lines": [65, 66, 68, 69, 70, 72, 73, 75, 77], "branches": [[68, 69], [68, 77]]}

import pytest
import warnings
import flask.globals


class TestGetAttr:
    def test_getattr_request_ctx_deprecation_warning(self):
        """Test that accessing request_ctx raises a DeprecationWarning and returns app_ctx."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = flask.globals.__getattr__("request_ctx")
            assert len(w) == 1
            assert issubclass(w[0].category, DeprecationWarning)
            assert "'request_ctx' has merged with 'app_ctx'" in str(w[0].message)
            assert result is flask.globals.app_ctx

    def test_getattr_unknown_attribute_raises_attribute_error(self):
        """Test that accessing an unknown attribute raises AttributeError."""
        with pytest.raises(AttributeError, match="unknown_attr"):
            flask.globals.__getattr__("unknown_attr")
