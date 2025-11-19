# file: src/flask/src/flask/sansio/scaffold.py:220-221
# asked: {"lines": [220, 221], "branches": []}
# gained: {"lines": [220, 221], "branches": []}

import pytest
from flask.sansio.scaffold import Scaffold

class TestScaffold:
    def test_check_setup_finished_raises_not_implemented_error(self):
        """Test that _check_setup_finished raises NotImplementedError."""
        scaffold = Scaffold("test_app")
        with pytest.raises(NotImplementedError):
            scaffold._check_setup_finished("test_function")
