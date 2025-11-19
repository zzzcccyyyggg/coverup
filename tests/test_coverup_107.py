# file: src/flask/src/flask/logging.py:31-47
# asked: {"lines": [31, 35, 36, 38, 39, 40, 42, 43, 45, 47], "branches": [[38, 39], [38, 47], [39, 40], [39, 42], [42, 43], [42, 45]]}
# gained: {"lines": [31, 35, 36, 38, 39, 40, 42, 43, 45, 47], "branches": [[38, 39], [38, 47], [39, 40], [39, 42], [42, 43], [42, 45]]}

import pytest
import logging
from flask.logging import has_level_handler


class TestHasLevelHandler:
    def test_has_level_handler_with_matching_handler(self):
        """Test that returns True when a handler has level <= logger's effective level."""
        logger = logging.Logger('test_logger_matching')
        handler = logging.Handler()
        handler.setLevel(logging.DEBUG)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        
        result = has_level_handler(logger)
        assert result is True

    def test_has_level_handler_no_handlers(self):
        """Test that returns False when logger has no handlers."""
        logger = logging.Logger('test_logger_no_handlers')
        logger.setLevel(logging.INFO)
        
        result = has_level_handler(logger)
        assert result is False

    def test_has_level_handler_handler_level_too_high(self):
        """Test that returns False when handler level is higher than logger's effective level."""
        logger = logging.Logger('test_logger_high_handler')
        handler = logging.Handler()
        handler.setLevel(logging.ERROR)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        
        result = has_level_handler(logger)
        assert result is False

    def test_has_level_handler_with_parent_propagation(self):
        """Test that checks parent logger when propagate is True."""
        parent_logger = logging.Logger('parent_logger_prop')
        child_logger = logging.Logger('parent_logger_prop.child')
        child_logger.parent = parent_logger
        
        # Add handler to parent with appropriate level
        handler = logging.Handler()
        handler.setLevel(logging.INFO)
        parent_logger.addHandler(handler)
        parent_logger.setLevel(logging.INFO)
        child_logger.setLevel(logging.INFO)
        
        result = has_level_handler(child_logger)
        assert result is True

    def test_has_level_handler_propagate_false_breaks_loop(self):
        """Test that breaks loop when propagate is False."""
        parent_logger = logging.Logger('parent_logger_propagate_false')
        child_logger = logging.Logger('parent_logger_propagate_false.child')
        child_logger.parent = parent_logger
        
        # Add handler to parent but set propagate to False on child
        handler = logging.Handler()
        handler.setLevel(logging.INFO)
        parent_logger.addHandler(handler)
        parent_logger.setLevel(logging.INFO)
        child_logger.setLevel(logging.INFO)
        child_logger.propagate = False
        
        result = has_level_handler(child_logger)
        assert result is False

    def test_has_level_handler_multiple_handlers_one_matching(self):
        """Test that returns True when at least one handler matches the level requirement."""
        logger = logging.Logger('test_logger_multiple')
        handler1 = logging.Handler()
        handler1.setLevel(logging.ERROR)  # Too high
        handler2 = logging.Handler()
        handler2.setLevel(logging.DEBUG)  # Low enough
        logger.addHandler(handler1)
        logger.addHandler(handler2)
        logger.setLevel(logging.INFO)
        
        result = has_level_handler(logger)
        assert result is True

    def test_has_level_handler_root_logger_with_handler(self):
        """Test that works correctly with root logger."""
        root_logger = logging.getLogger()
        # Store original handlers
        original_handlers = root_logger.handlers[:]
        # Clear handlers for test
        for handler in original_handlers:
            root_logger.removeHandler(handler)
        
        try:
            handler = logging.Handler()
            handler.setLevel(logging.INFO)
            root_logger.addHandler(handler)
            root_logger.setLevel(logging.INFO)
            
            result = has_level_handler(root_logger)
            assert result is True
        finally:
            # Restore original handlers
            for handler in original_handlers:
                root_logger.addHandler(handler)

    def test_has_level_handler_root_logger_no_handler(self):
        """Test that returns False for root logger with no handlers."""
        root_logger = logging.getLogger()
        # Store original handlers
        original_handlers = root_logger.handlers[:]
        # Clear handlers for test
        for handler in original_handlers:
            root_logger.removeHandler(handler)
        
        try:
            result = has_level_handler(root_logger)
            assert result is False
        finally:
            # Restore original handlers
            for handler in original_handlers:
                root_logger.addHandler(handler)

    def test_has_level_handler_none_parent_terminates_loop(self):
        """Test that terminates loop when parent is None."""
        logger = logging.Logger('test_logger_no_parent')
        logger.setLevel(logging.INFO)
        
        result = has_level_handler(logger)
        assert result is False
