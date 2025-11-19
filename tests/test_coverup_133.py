# file: src/flask/src/flask/templating.py:91-99
# asked: {"lines": [91, 94, 95, 96, 97, 98, 99], "branches": [[94, 95], [94, 99]]}
# gained: {"lines": [91, 94, 95, 96, 97, 98, 99], "branches": [[94, 95], [94, 99]]}

import pytest
from jinja2 import Environment, TemplateNotFound
from flask.templating import DispatchingJinjaLoader
from unittest.mock import Mock

class TestDispatchingJinjaLoaderGetSourceFast:
    
    def test_get_source_fast_template_found_first_loader(self, monkeypatch):
        """Test _get_source_fast when template is found by first loader"""
        app = Mock()
        loader = DispatchingJinjaLoader(app)
        
        # Mock _iter_loaders to return one loader that finds the template
        mock_loader = Mock()
        # Store the actual lambda function to compare later
        uptodate_func = lambda: True
        mock_loader.get_source.return_value = ("source", "filename", uptodate_func)
        
        def mock_iter_loaders(template):
            return [("app", mock_loader)]
        
        monkeypatch.setattr(loader, '_iter_loaders', mock_iter_loaders)
        
        environment = Environment()
        result = loader._get_source_fast(environment, "test_template.html")
        
        # Compare tuple elements individually to avoid lambda function comparison issues
        assert result[0] == "source"
        assert result[1] == "filename"
        assert callable(result[2])  # Verify it's callable
        mock_loader.get_source.assert_called_once_with(environment, "test_template.html")
    
    def test_get_source_fast_template_found_second_loader(self, monkeypatch):
        """Test _get_source_fast when template is found by second loader after first raises TemplateNotFound"""
        app = Mock()
        loader = DispatchingJinjaLoader(app)
        
        # Mock _iter_loaders to return two loaders
        mock_loader1 = Mock()
        mock_loader1.get_source.side_effect = TemplateNotFound("test_template.html")
        
        mock_loader2 = Mock()
        # Store the actual lambda function to compare later
        uptodate_func = lambda: True
        mock_loader2.get_source.return_value = ("source", "filename", uptodate_func)
        
        def mock_iter_loaders(template):
            return [("app", mock_loader1), ("blueprint", mock_loader2)]
        
        monkeypatch.setattr(loader, '_iter_loaders', mock_iter_loaders)
        
        environment = Environment()
        result = loader._get_source_fast(environment, "test_template.html")
        
        # Compare tuple elements individually to avoid lambda function comparison issues
        assert result[0] == "source"
        assert result[1] == "filename"
        assert callable(result[2])  # Verify it's callable
        mock_loader1.get_source.assert_called_once_with(environment, "test_template.html")
        mock_loader2.get_source.assert_called_once_with(environment, "test_template.html")
    
    def test_get_source_fast_template_not_found_any_loader(self, monkeypatch):
        """Test _get_source_fast when template is not found by any loader"""
        app = Mock()
        loader = DispatchingJinjaLoader(app)
        
        # Mock _iter_loaders to return two loaders that both raise TemplateNotFound
        mock_loader1 = Mock()
        mock_loader1.get_source.side_effect = TemplateNotFound("test_template.html")
        
        mock_loader2 = Mock()
        mock_loader2.get_source.side_effect = TemplateNotFound("test_template.html")
        
        def mock_iter_loaders(template):
            return [("app", mock_loader1), ("blueprint", mock_loader2)]
        
        monkeypatch.setattr(loader, '_iter_loaders', mock_iter_loaders)
        
        environment = Environment()
        
        with pytest.raises(TemplateNotFound) as exc_info:
            loader._get_source_fast(environment, "test_template.html")
        
        assert str(exc_info.value) == "test_template.html"
        mock_loader1.get_source.assert_called_once_with(environment, "test_template.html")
        mock_loader2.get_source.assert_called_once_with(environment, "test_template.html")
    
    def test_get_source_fast_no_loaders(self, monkeypatch):
        """Test _get_source_fast when _iter_loaders returns no loaders"""
        app = Mock()
        loader = DispatchingJinjaLoader(app)
        
        # Mock _iter_loaders to return empty list
        def mock_iter_loaders(template):
            return []
        
        monkeypatch.setattr(loader, '_iter_loaders', mock_iter_loaders)
        
        environment = Environment()
        
        with pytest.raises(TemplateNotFound) as exc_info:
            loader._get_source_fast(environment, "test_template.html")
        
        assert str(exc_info.value) == "test_template.html"
