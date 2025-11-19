# file: src/flask/src/flask/templating.py:67-89
# asked: {"lines": [67, 70, 72, 74, 75, 76, 77, 78, 79, 80, 81, 83, 85, 87, 88, 89], "branches": [[74, 75], [74, 83], [77, 78], [77, 81], [87, 88], [87, 89]]}
# gained: {"lines": [67, 70, 72, 74, 75, 76, 77, 78, 79, 80, 81, 83, 85, 87, 88, 89], "branches": [[74, 75], [74, 83], [77, 78], [77, 81], [87, 88], [87, 89]]}

import pytest
from unittest.mock import Mock, MagicMock, patch
from jinja2 import Environment, TemplateNotFound
from flask.templating import DispatchingJinjaLoader


class TestDispatchingJinjaLoaderGetSourceExplained:
    
    def test_get_source_explained_success_first_loader(self, monkeypatch):
        """Test _get_source_explained when first loader succeeds"""
        app = Mock()
        app.logger = Mock()
        loader = DispatchingJinjaLoader(app)
        
        # Create a reusable callback function
        callback = lambda: True
        
        # Mock _iter_loaders to return one loader that succeeds
        mock_loader = Mock()
        mock_loader.get_source.return_value = ("source", "filename", callback)
        monkeypatch.setattr(loader, '_iter_loaders', lambda template: [(app, mock_loader)])
        
        # Mock explain_template_loading_attempts to verify it's called
        mock_explain = Mock()
        monkeypatch.setattr('flask.debughelpers.explain_template_loading_attempts', mock_explain)
        
        env = Environment()
        template = "test_template.html"
        
        result = loader._get_source_explained(env, template)
        
        # Check individual tuple elements instead of comparing the whole tuple
        assert result[0] == "source"
        assert result[1] == "filename"
        assert callable(result[2])
        mock_loader.get_source.assert_called_once_with(env, template)
        mock_explain.assert_called_once_with(app, template, [(mock_loader, app, ("source", "filename", callback))])
        
    def test_get_source_explained_success_second_loader(self, monkeypatch):
        """Test _get_source_explained when first loader fails but second succeeds"""
        app = Mock()
        app.logger = Mock()
        loader = DispatchingJinjaLoader(app)
        
        # Create a reusable callback function
        callback = lambda: True
        
        # Mock _iter_loaders to return two loaders - first fails, second succeeds
        mock_loader1 = Mock()
        mock_loader1.get_source.side_effect = TemplateNotFound("template not found")
        mock_loader2 = Mock()
        mock_loader2.get_source.return_value = ("source", "filename", callback)
        monkeypatch.setattr(loader, '_iter_loaders', lambda template: [(app, mock_loader1), (app, mock_loader2)])
        
        # Mock explain_template_loading_attempts to verify it's called
        mock_explain = Mock()
        monkeypatch.setattr('flask.debughelpers.explain_template_loading_attempts', mock_explain)
        
        env = Environment()
        template = "test_template.html"
        
        result = loader._get_source_explained(env, template)
        
        # Check individual tuple elements instead of comparing the whole tuple
        assert result[0] == "source"
        assert result[1] == "filename"
        assert callable(result[2])
        mock_loader1.get_source.assert_called_once_with(env, template)
        mock_loader2.get_source.assert_called_once_with(env, template)
        mock_explain.assert_called_once_with(app, template, [
            (mock_loader1, app, None),
            (mock_loader2, app, ("source", "filename", callback))
        ])
        
    def test_get_source_explained_all_loaders_fail(self, monkeypatch):
        """Test _get_source_explained when all loaders fail"""
        app = Mock()
        app.logger = Mock()
        loader = DispatchingJinjaLoader(app)
        
        # Mock _iter_loaders to return two loaders that both fail
        mock_loader1 = Mock()
        mock_loader1.get_source.side_effect = TemplateNotFound("template not found")
        mock_loader2 = Mock()
        mock_loader2.get_source.side_effect = TemplateNotFound("template not found")
        monkeypatch.setattr(loader, '_iter_loaders', lambda template: [(app, mock_loader1), (app, mock_loader2)])
        
        # Mock explain_template_loading_attempts to verify it's called
        mock_explain = Mock()
        monkeypatch.setattr('flask.debughelpers.explain_template_loading_attempts', mock_explain)
        
        env = Environment()
        template = "test_template.html"
        
        with pytest.raises(TemplateNotFound) as exc_info:
            loader._get_source_explained(env, template)
        
        assert str(exc_info.value) == template
        mock_loader1.get_source.assert_called_once_with(env, template)
        mock_loader2.get_source.assert_called_once_with(env, template)
        mock_explain.assert_called_once_with(app, template, [
            (mock_loader1, app, None),
            (mock_loader2, app, None)
        ])
        
    def test_get_source_explained_mixed_success_failure(self, monkeypatch):
        """Test _get_source_explained with mixed loader results"""
        app = Mock()
        app.logger = Mock()
        loader = DispatchingJinjaLoader(app)
        
        # Create reusable callback functions
        callback1 = lambda: True
        callback2 = lambda: False
        
        # Mock _iter_loaders to return three loaders with mixed results
        mock_loader1 = Mock()
        mock_loader1.get_source.side_effect = TemplateNotFound("template not found")
        mock_loader2 = Mock()
        mock_loader2.get_source.return_value = ("source1", "file1", callback1)
        mock_loader3 = Mock()
        mock_loader3.get_source.return_value = ("source2", "file2", callback2)
        monkeypatch.setattr(loader, '_iter_loaders', lambda template: [
            (app, mock_loader1), 
            (app, mock_loader2), 
            (app, mock_loader3)
        ])
        
        # Mock explain_template_loading_attempts to verify it's called
        mock_explain = Mock()
        monkeypatch.setattr('flask.debughelpers.explain_template_loading_attempts', mock_explain)
        
        env = Environment()
        template = "test_template.html"
        
        result = loader._get_source_explained(env, template)
        
        # Should return the first successful result (loader2)
        assert result[0] == "source1"
        assert result[1] == "file1"
        assert callable(result[2])
        mock_loader1.get_source.assert_called_once_with(env, template)
        mock_loader2.get_source.assert_called_once_with(env, template)
        mock_loader3.get_source.assert_called_once_with(env, template)
        mock_explain.assert_called_once_with(app, template, [
            (mock_loader1, app, None),
            (mock_loader2, app, ("source1", "file1", callback1)),
            (mock_loader3, app, ("source2", "file2", callback2))
        ])
