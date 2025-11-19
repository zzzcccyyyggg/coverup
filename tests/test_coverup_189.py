# file: src/flask/src/flask/templating.py:60-65
# asked: {"lines": [60, 63, 64, 65], "branches": [[63, 64], [63, 65]]}
# gained: {"lines": [60, 63, 64, 65], "branches": [[63, 64], [63, 65]]}

import pytest
from flask import Flask
from flask.templating import DispatchingJinjaLoader
from jinja2 import Environment, TemplateNotFound


class TestDispatchingJinjaLoader:
    def test_get_source_with_explain_template_loading_enabled(self, monkeypatch):
        """Test that get_source calls _get_source_explained when EXPLAIN_TEMPLATE_LOADING is True."""
        app = Flask(__name__)
        app.config["EXPLAIN_TEMPLATE_LOADING"] = True
        loader = DispatchingJinjaLoader(app)
        
        # Mock _get_source_explained to return a specific value
        mock_result = ("template content", "template.html", lambda: True)
        monkeypatch.setattr(loader, "_get_source_explained", lambda env, tpl: mock_result)
        
        # Mock _get_source_fast to ensure it's not called
        fast_called = False
        def mock_fast(env, tpl):
            nonlocal fast_called
            fast_called = True
            return mock_result
        monkeypatch.setattr(loader, "_get_source_fast", mock_fast)
        
        env = Environment()
        result = loader.get_source(env, "test.html")
        
        assert result == mock_result
        assert not fast_called

    def test_get_source_with_explain_template_loading_disabled(self, monkeypatch):
        """Test that get_source calls _get_source_fast when EXPLAIN_TEMPLATE_LOADING is False."""
        app = Flask(__name__)
        app.config["EXPLAIN_TEMPLATE_LOADING"] = False
        loader = DispatchingJinjaLoader(app)
        
        # Mock _get_source_fast to return a specific value
        mock_result = ("template content", "template.html", lambda: True)
        monkeypatch.setattr(loader, "_get_source_fast", lambda env, tpl: mock_result)
        
        # Mock _get_source_explained to ensure it's not called
        explained_called = False
        def mock_explained(env, tpl):
            nonlocal explained_called
            explained_called = True
            return mock_result
        monkeypatch.setattr(loader, "_get_source_explained", mock_explained)
        
        env = Environment()
        result = loader.get_source(env, "test.html")
        
        assert result == mock_result
        assert not explained_called

    def test_get_source_with_explain_template_loading_not_set(self, monkeypatch):
        """Test that get_source calls _get_source_fast when EXPLAIN_TEMPLATE_LOADING is not set."""
        app = Flask(__name__)
        # Use get() method to avoid KeyError when the key doesn't exist
        # This simulates the behavior when the config key is not set
        loader = DispatchingJinjaLoader(app)
        
        # Mock _get_source_fast to return a specific value
        mock_result = ("template content", "template.html", lambda: True)
        monkeypatch.setattr(loader, "_get_source_fast", lambda env, tpl: mock_result)
        
        # Mock _get_source_explained to ensure it's not called
        explained_called = False
        def mock_explained(env, tpl):
            nonlocal explained_called
            explained_called = True
            return mock_result
        monkeypatch.setattr(loader, "_get_source_explained", mock_explained)
        
        # Mock the config access to return False when key doesn't exist
        original_getitem = app.config.__getitem__
        def mock_getitem(key):
            if key == "EXPLAIN_TEMPLATE_LOADING":
                raise KeyError(key)
            return original_getitem(key)
        monkeypatch.setattr(app.config, "__getitem__", mock_getitem)
        
        env = Environment()
        result = loader.get_source(env, "test.html")
        
        assert result == mock_result
        assert not explained_called
