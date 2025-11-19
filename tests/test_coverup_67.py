# file: src/flask/src/flask/config.py:126-185
# asked: {"lines": [126, 127, 152, 154, 155, 156, 158, 159, 161, 162, 163, 165, 167, 169, 170, 173, 174, 176, 178, 179, 181, 183, 185], "branches": [[154, 155], [154, 185], [155, 156], [155, 158], [167, 169], [167, 173], [176, 178], [176, 183], [178, 179], [178, 181]]}
# gained: {"lines": [126, 127, 152, 154, 155, 156, 158, 159, 161, 162, 163, 165, 167, 169, 170, 173, 174, 176, 178, 179, 181, 183, 185], "branches": [[154, 155], [154, 185], [155, 156], [155, 158], [167, 169], [167, 173], [176, 178], [176, 183], [178, 179], [178, 181]]}

import json
import os
import pytest
from flask.config import Config


class TestConfigFromPrefixedEnv:
    """Test cases for Config.from_prefixed_env method to achieve full coverage."""
    
    def test_from_prefixed_env_basic_functionality(self, monkeypatch, tmp_path):
        """Test basic functionality with simple key-value pairs."""
        config = Config(tmp_path)
        monkeypatch.setenv('FLASK_TEST_KEY', 'test_value')
        monkeypatch.setenv('FLASK_ANOTHER_KEY', 'another_value')
        
        result = config.from_prefixed_env()
        
        assert result is True
        assert config['TEST_KEY'] == 'test_value'
        assert config['ANOTHER_KEY'] == 'another_value'
    
    def test_from_prefixed_env_with_json_parsing(self, monkeypatch, tmp_path):
        """Test that JSON values are properly parsed."""
        config = Config(tmp_path)
        monkeypatch.setenv('FLASK_NUMBER', '42')
        monkeypatch.setenv('FLASK_LIST', '[1, 2, 3]')
        monkeypatch.setenv('FLASK_DICT', '{"key": "value"}')
        
        result = config.from_prefixed_env()
        
        assert result is True
        assert config['NUMBER'] == 42
        assert config['LIST'] == [1, 2, 3]
        assert config['DICT'] == {'key': 'value'}
    
    def test_from_prefixed_env_json_parsing_failure(self, monkeypatch, tmp_path):
        """Test that JSON parsing failures keep the value as string."""
        config = Config(tmp_path)
        monkeypatch.setenv('FLASK_INVALID_JSON', '{"invalid": json}')
        
        result = config.from_prefixed_env()
        
        assert result is True
        assert config['INVALID_JSON'] == '{"invalid": json}'
    
    def test_from_prefixed_env_nested_keys(self, monkeypatch, tmp_path):
        """Test nested dictionary creation with double underscores."""
        config = Config(tmp_path)
        monkeypatch.setenv('FLASK_DATABASE__HOST', 'localhost')
        monkeypatch.setenv('FLASK_DATABASE__PORT', '5432')
        monkeypatch.setenv('FLASK_API__AUTH__TOKEN', 'secret')
        
        result = config.from_prefixed_env()
        
        assert result is True
        assert config['DATABASE'] == {'HOST': 'localhost', 'PORT': 5432}
        assert config['API'] == {'AUTH': {'TOKEN': 'secret'}}
    
    def test_from_prefixed_env_custom_prefix(self, monkeypatch, tmp_path):
        """Test using a custom prefix instead of default FLASK."""
        config = Config(tmp_path)
        monkeypatch.setenv('MYAPP_SETTING', 'custom_value')
        monkeypatch.setenv('FLASK_IGNORED', 'should_not_appear')
        
        result = config.from_prefixed_env(prefix='MYAPP')
        
        assert result is True
        assert config['SETTING'] == 'custom_value'
        assert 'IGNORED' not in config
    
    def test_from_prefixed_env_custom_loads_function(self, monkeypatch, tmp_path):
        """Test using a custom loading function."""
        config = Config(tmp_path)
        monkeypatch.setenv('FLASK_CUSTOM', 'value')
        
        def custom_loads(value):
            return f"processed_{value}"
        
        result = config.from_prefixed_env(loads=custom_loads)
        
        assert result is True
        assert config['CUSTOM'] == 'processed_value'
    
    def test_from_prefixed_env_custom_loads_function_exception(self, monkeypatch, tmp_path):
        """Test that exceptions in custom loads function keep original value."""
        config = Config(tmp_path)
        monkeypatch.setenv('FLASK_ERROR', 'test_value')
        
        def failing_loads(value):
            raise ValueError("Custom error")
        
        result = config.from_prefixed_env(loads=failing_loads)
        
        assert result is True
        assert config['ERROR'] == 'test_value'
    
    def test_from_prefixed_env_empty_environment(self, tmp_path):
        """Test behavior when no matching environment variables exist."""
        config = Config(tmp_path)
        
        result = config.from_prefixed_env()
        
        assert result is True
        assert config == {}
    
    def test_from_prefixed_env_mixed_nested_and_flat_keys(self, monkeypatch, tmp_path):
        """Test mixed nested and flat keys in the same configuration."""
        config = Config(tmp_path)
        monkeypatch.setenv('FLASK_SIMPLE', 'simple_value')
        monkeypatch.setenv('FLASK_NESTED__KEY', 'nested_value')
        monkeypatch.setenv('FLASK_ANOTHER_SIMPLE', 'another_simple')
        
        result = config.from_prefixed_env()
        
        assert result is True
        assert config['SIMPLE'] == 'simple_value'
        assert config['NESTED'] == {'KEY': 'nested_value'}
        assert config['ANOTHER_SIMPLE'] == 'another_simple'
    
    def test_from_prefixed_env_complex_nested_structure(self, monkeypatch, tmp_path):
        """Test complex nested structure with multiple levels."""
        config = Config(tmp_path)
        monkeypatch.setenv('FLASK_LEVEL1__LEVEL2__LEVEL3__FINAL', 'deep_value')
        monkeypatch.setenv('FLASK_LEVEL1__LEVEL2__OTHER', 'other_value')
        
        result = config.from_prefixed_env()
        
        assert result is True
        expected = {
            'LEVEL1': {
                'LEVEL2': {
                    'LEVEL3': {'FINAL': 'deep_value'},
                    'OTHER': 'other_value'
                }
            }
        }
        assert config['LEVEL1'] == expected['LEVEL1']
