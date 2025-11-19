# file: src/flask/src/flask/logging.py:58-79
# asked: {"lines": [58, 71, 73, 74, 76, 77, 79], "branches": [[73, 74], [73, 76], [76, 77], [76, 79]]}
# gained: {"lines": [58, 71, 73, 74, 76, 77, 79], "branches": [[73, 74], [73, 76], [76, 77], [76, 79]]}

import logging
import pytest
from flask import Flask
from flask.logging import create_logger, has_level_handler, default_handler


class TestCreateLogger:
    """Test cases for create_logger function to achieve full coverage."""
    
    def test_create_logger_with_debug_and_no_level(self):
        """Test that logger level is set to DEBUG when app.debug is True and logger has no level set."""
        app = Flask(__name__)
        app.debug = True
        
        # Get logger before calling create_logger to ensure it has no level set
        logger = logging.getLogger(app.name)
        logger.setLevel(logging.NOTSET)  # Ensure no level is set
        
        result = create_logger(app)
        
        assert result is logger
        assert result.level == logging.DEBUG
    
    def test_create_logger_without_level_handler(self, monkeypatch):
        """Test that default handler is added when logger has no level handler."""
        app = Flask(__name__)
        
        # Mock has_level_handler to return False
        monkeypatch.setattr('flask.logging.has_level_handler', lambda x: False)
        
        # Get logger and remove any existing handlers
        logger = logging.getLogger(app.name)
        original_handlers = logger.handlers[:]
        logger.handlers.clear()
        
        try:
            result = create_logger(app)
            
            assert result is logger
            # Check that default_handler was added
            assert default_handler in result.handlers
        finally:
            # Restore original handlers
            logger.handlers = original_handlers
    
    def test_create_logger_with_existing_level_handler(self, monkeypatch):
        """Test that no handler is added when logger already has a level handler."""
        app = Flask(__name__)
        
        # Mock has_level_handler to return True
        monkeypatch.setattr('flask.logging.has_level_handler', lambda x: True)
        
        # Get logger and record original handlers
        logger = logging.getLogger(app.name)
        original_handlers = logger.handlers[:]
        
        try:
            result = create_logger(app)
            
            assert result is logger
            # Ensure no new handlers were added
            assert result.handlers == original_handlers
        finally:
            # Restore original handlers
            logger.handlers = original_handlers
    
    def test_create_logger_with_debug_and_existing_level(self):
        """Test that logger level is not changed when app.debug is True but logger already has a level."""
        app = Flask(__name__)
        app.debug = True
        
        # Get logger and set a specific level
        logger = logging.getLogger(app.name)
        original_level = logger.level
        logger.setLevel(logging.INFO)
        
        try:
            result = create_logger(app)
            
            assert result is logger
            # Level should remain INFO, not be changed to DEBUG
            assert result.level == logging.INFO
        finally:
            # Restore original level
            logger.setLevel(original_level)
    
    def test_create_logger_without_debug(self):
        """Test that logger level is not changed when app.debug is False."""
        app = Flask(__name__)
        app.debug = False
        
        # Get logger and ensure it has no level set
        logger = logging.getLogger(app.name)
        original_level = logger.level
        logger.setLevel(logging.NOTSET)
        
        try:
            result = create_logger(app)
            
            assert result is logger
            # Level should remain NOTSET when app.debug is False
            assert result.level == logging.NOTSET
        finally:
            # Restore original level
            logger.setLevel(original_level)
