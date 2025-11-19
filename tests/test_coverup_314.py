# file: src/flask/src/flask/config.py:323-364
# asked: {"lines": [362], "branches": [[361, 362]]}
# gained: {"lines": [362], "branches": [[361, 362]]}

import pytest
import tempfile
import os
from flask.config import Config

class TestConfigGetNamespace:
    def test_get_namespace_with_lowercase_true(self):
        """Test that get_namespace converts keys to lowercase when lowercase=True"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = Config(tmpdir)
            config['TEST_NAMESPACE_KEY1'] = 'value1'
            config['TEST_NAMESPACE_KEY2'] = 'value2'
            config['OTHER_KEY'] = 'should_not_appear'
            
            result = config.get_namespace('TEST_NAMESPACE_', lowercase=True, trim_namespace=True)
            
            assert result == {'key1': 'value1', 'key2': 'value2'}
            assert 'key1' in result
            assert 'KEY1' not in result
            assert 'OTHER_KEY' not in result

    def test_get_namespace_with_lowercase_false(self):
        """Test that get_namespace preserves original case when lowercase=False"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = Config(tmpdir)
            config['TEST_NAMESPACE_KeyMixed'] = 'value1'
            config['TEST_NAMESPACE_ANOTHER_KEY'] = 'value2'
            config['OTHER_KEY'] = 'should_not_appear'
            
            result = config.get_namespace('TEST_NAMESPACE_', lowercase=False, trim_namespace=True)
            
            assert result == {'KeyMixed': 'value1', 'ANOTHER_KEY': 'value2'}
            assert 'KeyMixed' in result
            assert 'keymixed' not in result
            assert 'ANOTHER_KEY' in result
            assert 'another_key' not in result
            assert 'OTHER_KEY' not in result
