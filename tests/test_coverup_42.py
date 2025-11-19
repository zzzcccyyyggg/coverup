# file: src/flask/src/flask/helpers.py:344-383
# asked: {"lines": [344, 345, 375, 376, 377, 378, 379, 380, 381, 382, 383], "branches": [[376, 377], [376, 379], [379, 380], [379, 381], [381, 382], [381, 383]]}
# gained: {"lines": [344, 345, 375, 376, 377, 378, 379, 380, 381, 382, 383], "branches": [[376, 377], [376, 379], [379, 380], [379, 381], [381, 382], [381, 383]]}

import pytest
from flask import Flask
from flask.helpers import get_flashed_messages
from flask.globals import app_ctx, session

class TestGetFlashedMessages:
    def test_get_flashed_messages_no_flashes(self):
        """Test when there are no flashed messages in session or app_ctx."""
        app = Flask(__name__)
        app.secret_key = 'test-secret-key'
        
        with app.test_request_context():
            # Ensure no flashes in app_ctx
            app_ctx._flashes = None
            # Ensure no flashes in session
            if '_flashes' in session:
                session.pop('_flashes')
            
            result = get_flashed_messages()
            assert result == []
    
    def test_get_flashed_messages_from_session(self):
        """Test when flashes are retrieved from session."""
        app = Flask(__name__)
        app.secret_key = 'test-secret-key'
        
        with app.test_request_context():
            # Set flashes in session
            session['_flashes'] = [('error', 'Error message'), ('info', 'Info message')]
            # Ensure app_ctx has no flashes initially
            app_ctx._flashes = None
            
            result = get_flashed_messages()
            assert result == ['Error message', 'Info message']
            # Verify flashes were moved to app_ctx
            assert app_ctx._flashes == [('error', 'Error message'), ('info', 'Info message')]
            # Verify flashes were removed from session
            assert '_flashes' not in session
    
    def test_get_flashed_messages_from_app_ctx(self):
        """Test when flashes are already cached in app_ctx."""
        app = Flask(__name__)
        app.secret_key = 'test-secret-key'
        
        with app.test_request_context():
            # Set flashes directly in app_ctx
            app_ctx._flashes = [('warning', 'Warning message'), ('success', 'Success message')]
            
            result = get_flashed_messages()
            assert result == ['Warning message', 'Success message']
            # Verify app_ctx flashes remain unchanged
            assert app_ctx._flashes == [('warning', 'Warning message'), ('success', 'Success message')]
    
    def test_get_flashed_messages_with_categories(self):
        """Test with_categories=True returns tuples."""
        app = Flask(__name__)
        app.secret_key = 'test-secret-key'
        
        with app.test_request_context():
            app_ctx._flashes = [('error', 'Error message'), ('info', 'Info message')]
            
            result = get_flashed_messages(with_categories=True)
            assert result == [('error', 'Error message'), ('info', 'Info message')]
    
    def test_get_flashed_messages_with_category_filter(self):
        """Test filtering flashes by category."""
        app = Flask(__name__)
        app.secret_key = 'test-secret-key'
        
        with app.test_request_context():
            app_ctx._flashes = [
                ('error', 'Error message'),
                ('warning', 'Warning message'), 
                ('info', 'Info message'),
                ('success', 'Success message')
            ]
            
            result = get_flashed_messages(category_filter=['error', 'info'])
            assert result == ['Error message', 'Info message']
    
    def test_get_flashed_messages_with_categories_and_filter(self):
        """Test with_categories=True and category_filter together."""
        app = Flask(__name__)
        app.secret_key = 'test-secret-key'
        
        with app.test_request_context():
            app_ctx._flashes = [
                ('error', 'Error message'),
                ('warning', 'Warning message'),
                ('info', 'Info message'),
                ('success', 'Success message')
            ]
            
            result = get_flashed_messages(with_categories=True, category_filter=['warning', 'success'])
            assert result == [('warning', 'Warning message'), ('success', 'Success message')]
    
    def test_get_flashed_messages_empty_category_filter(self):
        """Test with empty category filter returns all messages."""
        app = Flask(__name__)
        app.secret_key = 'test-secret-key'
        
        with app.test_request_context():
            app_ctx._flashes = [('error', 'Error message'), ('info', 'Info message')]
            
            result = get_flashed_messages(category_filter=[])
            assert result == ['Error message', 'Info message']
    
    def test_get_flashed_messages_no_matching_category_filter(self):
        """Test when category filter doesn't match any flashes."""
        app = Flask(__name__)
        app.secret_key = 'test-secret-key'
        
        with app.test_request_context():
            app_ctx._flashes = [('error', 'Error message'), ('info', 'Info message')]
            
            result = get_flashed_messages(category_filter=['warning'])
            assert result == []
