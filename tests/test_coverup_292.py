# file: src/flask/src/flask/sansio/app.py:279-408
# asked: {"lines": [303, 304], "branches": [[302, 303]]}
# gained: {"lines": [303, 304], "branches": [[302, 303]]}

import pytest
import os
import tempfile
from flask.sansio.app import App

class TestAppInstancePath:
    def test_app_init_with_relative_instance_path_raises_value_error(self):
        """Test that providing a relative instance_path raises ValueError."""
        # Create a subclass that provides the missing default_config attribute
        class TestApp(App):
            default_config = {}
        
        with pytest.raises(ValueError, match="If an instance path is provided it must be absolute. A relative path was given instead."):
            TestApp(__name__, instance_path="relative/path")

    def test_app_init_with_absolute_instance_path_succeeds(self):
        """Test that providing an absolute instance_path works correctly."""
        # Create a subclass that provides the missing default_config attribute
        class TestApp(App):
            default_config = {}
        
        with tempfile.TemporaryDirectory() as temp_dir:
            app = TestApp(__name__, instance_path=temp_dir)
            assert app.instance_path == temp_dir

    def test_app_init_with_none_instance_path_uses_auto_find(self):
        """Test that providing None instance_path uses auto_find_instance_path."""
        # Create a subclass that provides the missing default_config attribute
        class TestApp(App):
            default_config = {}
        
        app = TestApp(__name__, instance_path=None)
        assert app.instance_path is not None
        assert isinstance(app.instance_path, str)
