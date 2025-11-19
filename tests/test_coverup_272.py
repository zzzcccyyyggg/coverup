# file: src/flask/src/flask/sansio/app.py:439-464
# asked: {"lines": [439, 440, 464], "branches": []}
# gained: {"lines": [439, 440, 464], "branches": []}

import pytest
import logging
from unittest.mock import Mock, patch, MagicMock
from flask import Flask


class TestAppLogger:
    """Test cases for the App.logger property to achieve full coverage."""
    
    def test_logger_created_with_app_name(self):
        """Test that logger uses the app's name."""
        app = Flask("test_app")
        logger = app.logger
        assert logger.name == "test_app"
    
    def test_logger_debug_mode_sets_level(self):
        """Test that debug mode sets logger level to DEBUG when not already set."""
        app = Flask("test_app")
        app.debug = True
        
        # Create a real logger and mock the has_level_handler function
        with patch('flask.logging.has_level_handler') as mock_has_handler:
            mock_has_handler.return_value = True
            
            logger = app.logger
            assert logger.level == logging.DEBUG
    
    def test_logger_no_handlers_adds_default_handler(self):
        """Test that a default handler is added when no handlers exist."""
        app = Flask("test_app")
        
        # Create a logger with no handlers and mock has_level_handler to return False
        logger_name = app.name
        original_logger = logging.getLogger(logger_name)
        
        # Remove all handlers temporarily
        original_handlers = original_logger.handlers[:]
        for handler in original_handlers:
            original_logger.removeHandler(handler)
        
        try:
            with patch('flask.logging.has_level_handler') as mock_has_handler:
                mock_has_handler.return_value = False
                
                # Access logger to trigger handler addition
                logger = app.logger
                
                # Check that handlers were added
                assert len(logger.handlers) > 0
        finally:
            # Restore original handlers
            for handler in logger.handlers[:]:
                logger.removeHandler(handler)
            for handler in original_handlers:
                logger.addHandler(handler)
    
    def test_logger_existing_handlers_no_additional_handler(self):
        """Test that no additional handler is added when handlers already exist."""
        app = Flask("test_app")
        
        # Get the logger before the test to establish baseline
        logger_name = app.name
        original_logger = logging.getLogger(logger_name)
        original_handler_count = len(original_logger.handlers)
        
        with patch('flask.logging.has_level_handler') as mock_has_handler:
            mock_has_handler.return_value = True
            
            # Access logger
            logger = app.logger
            
            # Verify handler count didn't change
            assert len(logger.handlers) == original_handler_count
    
    def test_logger_cached_property_behavior(self):
        """Test that logger is cached and only created once."""
        app = Flask("test_app")
        
        # Access logger multiple times
        logger1 = app.logger
        logger2 = app.logger
        
        # Verify it's the same object (cached)
        assert logger1 is logger2
    
    def test_logger_with_existing_level_no_debug_override(self):
        """Test that existing logger level is not overridden in debug mode."""
        app = Flask("test_app")
        app.debug = True
        
        # Get the logger and set its level first
        logger = logging.getLogger(app.name)
        original_level = logger.level
        logger.setLevel(logging.INFO)
        
        try:
            # Access logger through app property
            app_logger = app.logger
            
            # Verify level is still INFO (not overridden to DEBUG)
            assert app_logger.level == logging.INFO
        finally:
            # Restore original level
            logger.setLevel(original_level)
    
    def test_logger_debug_mode_no_level_change_when_level_set(self):
        """Test that debug mode doesn't change level when logger already has a level set."""
        app = Flask("test_app")
        app.debug = True
        
        # Get the logger and set its level first
        logger = logging.getLogger(app.name)
        original_level = logger.level
        logger.setLevel(logging.WARNING)  # Set to something other than DEBUG
        
        try:
            # Access logger through app property
            app_logger = app.logger
            
            # Verify level is still WARNING (not changed to DEBUG)
            assert app_logger.level == logging.WARNING
        finally:
            # Restore original level
            logger.setLevel(original_level)
