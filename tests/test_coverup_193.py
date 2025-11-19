# file: src/flask/src/flask/sansio/scaffold.py:240-246
# asked: {"lines": [240, 241, 246], "branches": []}
# gained: {"lines": [240, 241, 246], "branches": []}

import pytest
from flask.sansio.scaffold import Scaffold

class TestScaffoldHasStaticFolder:
    def test_has_static_folder_when_set(self):
        scaffold = Scaffold(__name__, static_folder="static")
        assert scaffold.has_static_folder is True

    def test_has_static_folder_when_not_set(self):
        scaffold = Scaffold(__name__)
        assert scaffold.has_static_folder is False
