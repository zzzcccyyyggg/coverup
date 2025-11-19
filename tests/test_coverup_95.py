# file: src/flask/src/flask/helpers.py:310-341
# asked: {"lines": [310, 332, 333, 334, 335, 336, 337, 338, 339, 340], "branches": []}
# gained: {"lines": [310, 332, 333, 334, 335, 336, 337, 338, 339, 340], "branches": []}

import pytest
from unittest.mock import Mock, patch
from flask import Flask
from flask.helpers import flash

class TestFlashFunction:
    """Test cases for the flash function to achieve full coverage."""
    
    def test_flash_with_existing_flashes(self, monkeypatch):
        """Test flash when '_flashes' already exists in session."""
        mock_session = {'_flashes': [('existing', 'old message')]}
        mock_current_app = Mock()
        mock_send = Mock()
        
        monkeypatch.setattr('flask.helpers.session', mock_session)
        monkeypatch.setattr('flask.helpers.current_app', mock_current_app)
        monkeypatch.setattr('flask.helpers.message_flashed.send', mock_send)
        
        flash('test message', 'test_category')
        
        assert mock_session['_flashes'] == [
            ('existing', 'old message'),
            ('test_category', 'test message')
        ]
        mock_send.assert_called_once_with(
            mock_current_app._get_current_object(),
            _async_wrapper=mock_current_app._get_current_object().ensure_sync,
            message='test message',
            category='test_category'
        )
    
    def test_flash_without_existing_flashes(self, monkeypatch):
        """Test flash when '_flashes' does not exist in session."""
        mock_session = {}
        mock_current_app = Mock()
        mock_send = Mock()
        
        monkeypatch.setattr('flask.helpers.session', mock_session)
        monkeypatch.setattr('flask.helpers.current_app', mock_current_app)
        monkeypatch.setattr('flask.helpers.message_flashed.send', mock_send)
        
        flash('test message', 'test_category')
        
        assert mock_session['_flashes'] == [('test_category', 'test message')]
        mock_send.assert_called_once_with(
            mock_current_app._get_current_object(),
            _async_wrapper=mock_current_app._get_current_object().ensure_sync,
            message='test message',
            category='test_category'
        )
    
    def test_flash_with_default_category(self, monkeypatch):
        """Test flash with default category parameter."""
        mock_session = {}
        mock_current_app = Mock()
        mock_send = Mock()
        
        monkeypatch.setattr('flask.helpers.session', mock_session)
        monkeypatch.setattr('flask.helpers.current_app', mock_current_app)
        monkeypatch.setattr('flask.helpers.message_flashed.send', mock_send)
        
        flash('test message')
        
        assert mock_session['_flashes'] == [('message', 'test message')]
        mock_send.assert_called_once_with(
            mock_current_app._get_current_object(),
            _async_wrapper=mock_current_app._get_current_object().ensure_sync,
            message='test message',
            category='message'
        )
