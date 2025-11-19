# file: src/flask/src/flask/debughelpers.py:124-179
# asked: {"lines": [124, 136, 137, 138, 140, 141, 143, 144, 145, 146, 147, 149, 151, 153, 154, 156, 157, 159, 160, 161, 163, 164, 165, 166, 167, 168, 169, 171, 172, 173, 174, 176, 177, 179], "branches": [[140, 141], [140, 143], [143, 144], [143, 163], [144, 145], [144, 146], [146, 147], [146, 149], [153, 154], [153, 156], [156, 157], [156, 159], [164, 165], [164, 167], [167, 168], [167, 171], [171, 172], [171, 179]]}
# gained: {"lines": [124, 136, 137, 138, 140, 141, 143, 144, 145, 146, 147, 149, 151, 153, 154, 156, 157, 159, 160, 161, 163, 164, 165, 166, 167, 168, 169, 171, 172, 173, 174, 176, 177, 179], "branches": [[140, 141], [140, 143], [143, 144], [143, 163], [144, 145], [144, 146], [146, 147], [146, 149], [153, 154], [153, 156], [156, 157], [156, 159], [164, 165], [164, 167], [167, 168], [167, 171], [171, 172], [171, 179]]}

import pytest
from unittest.mock import Mock, MagicMock, patch
from flask.debughelpers import explain_template_loading_attempts
from flask.sansio.app import App
from flask.blueprints import Blueprint
from jinja2.loaders import BaseLoader
from flask.globals import _cv_app
import contextvars


class TestExplainTemplateLoadingAttempts:
    
    def test_no_attempts_no_blueprint(self):
        """Test when there are no template loading attempts and no blueprint context"""
        mock_app = Mock(spec=App)
        mock_app.logger = Mock()
        
        # Create a mock context that returns None for _cv_app.get(None)
        with patch('flask.debughelpers._cv_app') as mock_cv_app:
            mock_cv_app.get.return_value = None
            
            explain_template_loading_attempts(mock_app, "test.html", [])
        
        # Verify the logger was called with appropriate message
        call_args = mock_app.logger.info.call_args[0][0]
        assert "Locating template 'test.html':" in call_args
        assert "Error: the template could not be found." in call_args
        assert "blueprint" not in call_args
    
    def test_multiple_found_no_blueprint(self):
        """Test when multiple templates are found and no blueprint context"""
        mock_app = Mock(spec=App)
        mock_app.logger = Mock()
        
        # Create a mock context that returns None for _cv_app.get(None)
        with patch('flask.debughelpers._cv_app') as mock_cv_app:
            mock_cv_app.get.return_value = None
            
            # Create mock loader and scaffold objects
            mock_loader1 = Mock(spec=BaseLoader)
            mock_loader2 = Mock(spec=BaseLoader)
            mock_scaffold1 = Mock(spec=App)
            mock_scaffold1.import_name = "test_app"
            mock_scaffold2 = Mock(spec=App)
            mock_scaffold2.import_name = "test_app2"
            
            # Mock _dump_loader_info to return some info
            with patch('flask.debughelpers._dump_loader_info') as mock_dump:
                mock_dump.return_value = ["class: jinja2.loaders.FileSystemLoader", "searchpath: ['/templates']"]
                
                attempts = [
                    (mock_loader1, mock_scaffold1, ("template1", "/path/template1.html", None)),
                    (mock_loader2, mock_scaffold2, ("template2", "/path/template2.html", None)),
                ]
                
                explain_template_loading_attempts(mock_app, "test.html", attempts)
        
        # Verify the logger was called with warning about multiple matches
        call_args = mock_app.logger.info.call_args[0][0]
        assert "Warning: multiple loaders returned a match for the template." in call_args
        assert "blueprint" not in call_args
    
    def test_no_found_with_blueprint(self):
        """Test when no template is found and there is a blueprint context"""
        mock_app = Mock(spec=App)
        mock_app.logger = Mock()
        
        # Create a mock context with request and blueprint
        mock_ctx = Mock()
        mock_ctx.has_request = True
        mock_ctx.request = Mock()
        mock_ctx.request.blueprint = "test_blueprint"
        
        with patch('flask.debughelpers._cv_app') as mock_cv_app:
            mock_cv_app.get.return_value = mock_ctx
            
            # Create mock loader and scaffold objects
            mock_loader = Mock(spec=BaseLoader)
            mock_scaffold = Mock(spec=App)
            mock_scaffold.import_name = "test_app"
            
            # Mock _dump_loader_info to return some info
            with patch('flask.debughelpers._dump_loader_info') as mock_dump:
                mock_dump.return_value = ["class: jinja2.loaders.FileSystemLoader", "searchpath: ['/templates']"]
                
                attempts = [
                    (mock_loader, mock_scaffold, None),  # No match
                ]
                
                explain_template_loading_attempts(mock_app, "test.html", attempts)
        
        # Verify the logger was called with blueprint-specific advice
        call_args = mock_app.logger.info.call_args[0][0]
        assert "Error: the template could not be found." in call_args
        assert "blueprint 'test_blueprint'" in call_args
        assert "Maybe you did not place a template in the right folder?" in call_args
    
    def test_multiple_found_with_blueprint(self):
        """Test when multiple templates are found and there is a blueprint context"""
        mock_app = Mock(spec=App)
        mock_app.logger = Mock()
        
        # Create a mock context with request and blueprint
        mock_ctx = Mock()
        mock_ctx.has_request = True
        mock_ctx.request = Mock()
        mock_ctx.request.blueprint = "test_blueprint"
        
        with patch('flask.debughelpers._cv_app') as mock_cv_app:
            mock_cv_app.get.return_value = mock_ctx
            
            # Create mock loader and scaffold objects
            mock_loader1 = Mock(spec=BaseLoader)
            mock_loader2 = Mock(spec=BaseLoader)
            mock_scaffold1 = Mock(spec=App)
            mock_scaffold1.import_name = "test_app"
            mock_scaffold2 = Mock(spec=Blueprint)
            mock_scaffold2.name = "test_bp"
            mock_scaffold2.import_name = "test_bp_module"
            
            # Mock _dump_loader_info to return some info
            with patch('flask.debughelpers._dump_loader_info') as mock_dump:
                mock_dump.return_value = ["class: jinja2.loaders.FileSystemLoader", "searchpath: ['/templates']"]
                
                attempts = [
                    (mock_loader1, mock_scaffold1, ("template1", "/path/template1.html", None)),
                    (mock_loader2, mock_scaffold2, ("template2", "/path/template2.html", None)),
                ]
                
                explain_template_loading_attempts(mock_app, "test.html", attempts)
        
        # Verify the logger was called with blueprint-specific advice
        call_args = mock_app.logger.info.call_args[0][0]
        assert "Warning: multiple loaders returned a match for the template." in call_args
        assert "blueprint 'test_blueprint'" in call_args
        assert "Maybe you did not place a template in the right folder?" in call_args
    
    def test_blueprint_scaffold_type(self):
        """Test with Blueprint scaffold type in attempts"""
        mock_app = Mock(spec=App)
        mock_app.logger = Mock()
        
        # Create a mock context that returns None for _cv_app.get(None)
        with patch('flask.debughelpers._cv_app') as mock_cv_app:
            mock_cv_app.get.return_value = None
            
            # Create mock loader and blueprint scaffold
            mock_loader = Mock(spec=BaseLoader)
            mock_blueprint = Mock(spec=Blueprint)
            mock_blueprint.name = "test_bp"
            mock_blueprint.import_name = "test_bp_module"
            
            # Mock _dump_loader_info to return some info
            with patch('flask.debughelpers._dump_loader_info') as mock_dump:
                mock_dump.return_value = ["class: jinja2.loaders.FileSystemLoader", "searchpath: ['/templates']"]
                
                attempts = [
                    (mock_loader, mock_blueprint, ("template", "/path/template.html", None)),
                ]
                
                explain_template_loading_attempts(mock_app, "test.html", attempts)
        
        # Verify the logger was called and blueprint scaffold was handled correctly
        call_args = mock_app.logger.info.call_args[0][0]
        assert "blueprint 'test_bp' (test_bp_module)" in call_args
    
    def test_other_scaffold_type(self):
        """Test with non-App, non-Blueprint scaffold type in attempts"""
        mock_app = Mock(spec=App)
        mock_app.logger = Mock()
        
        # Create a mock context that returns None for _cv_app.get(None)
        with patch('flask.debughelpers._cv_app') as mock_cv_app:
            mock_cv_app.get.return_value = None
            
            # Create mock loader and custom scaffold
            mock_loader = Mock(spec=BaseLoader)
            mock_custom_scaffold = Mock()  # Not App or Blueprint
            
            # Mock _dump_loader_info to return some info
            with patch('flask.debughelpers._dump_loader_info') as mock_dump:
                mock_dump.return_value = ["class: jinja2.loaders.FileSystemLoader", "searchpath: ['/templates']"]
                
                attempts = [
                    (mock_loader, mock_custom_scaffold, ("template", "/path/template.html", None)),
                ]
                
                explain_template_loading_attempts(mock_app, "test.html", attempts)
        
        # Verify the logger was called and custom scaffold was handled with repr
        call_args = mock_app.logger.info.call_args[0][0]
        assert repr(mock_custom_scaffold) in call_args
    
    def test_triple_with_none_filename(self):
        """Test when triple has None filename (should use '<string>')"""
        mock_app = Mock(spec=App)
        mock_app.logger = Mock()
        
        # Create a mock context that returns None for _cv_app.get(None)
        with patch('flask.debughelpers._cv_app') as mock_cv_app:
            mock_cv_app.get.return_value = None
            
            # Create mock loader and scaffold
            mock_loader = Mock(spec=BaseLoader)
            mock_scaffold = Mock(spec=App)
            mock_scaffold.import_name = "test_app"
            
            # Mock _dump_loader_info to return some info
            with patch('flask.debughelpers._dump_loader_info') as mock_dump:
                mock_dump.return_value = ["class: jinja2.loaders.FileSystemLoader", "searchpath: ['/templates']"]
                
                attempts = [
                    (mock_loader, mock_scaffold, ("template", None, None)),  # None filename
                ]
                
                explain_template_loading_attempts(mock_app, "test.html", attempts)
        
        # Verify the logger was called and '<string>' was used
        call_args = mock_app.logger.info.call_args[0][0]
        assert "found ('<string>')" in call_args
    
    def test_blueprint_context_no_seems_fishy(self):
        """Test when there is a blueprint context but nothing seems fishy (single match)"""
        mock_app = Mock(spec=App)
        mock_app.logger = Mock()
        
        # Create a mock context with request and blueprint
        mock_ctx = Mock()
        mock_ctx.has_request = True
        mock_ctx.request = Mock()
        mock_ctx.request.blueprint = "test_blueprint"
        
        with patch('flask.debughelpers._cv_app') as mock_cv_app:
            mock_cv_app.get.return_value = mock_ctx
            
            # Create mock loader and scaffold
            mock_loader = Mock(spec=BaseLoader)
            mock_scaffold = Mock(spec=App)
            mock_scaffold.import_name = "test_app"
            
            # Mock _dump_loader_info to return some info
            with patch('flask.debughelpers._dump_loader_info') as mock_dump:
                mock_dump.return_value = ["class: jinja2.loaders.FileSystemLoader", "searchpath: ['/templates']"]
                
                attempts = [
                    (mock_loader, mock_scaffold, ("template", "/path/template.html", None)),
                ]
                
                explain_template_loading_attempts(mock_app, "test.html", attempts)
        
        # Verify the logger was called but no blueprint-specific advice (since only one match)
        call_args = mock_app.logger.info.call_args[0][0]
        assert "blueprint" not in call_args  # Should not include blueprint advice when not fishy
