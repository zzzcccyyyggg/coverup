# file: src/flask/src/flask/config.py:323-364
# asked: {"lines": [353, 354, 355, 356, 357, 358, 360, 361, 362, 363, 364], "branches": [[354, 355], [354, 364], [355, 356], [355, 357], [357, 358], [357, 360], [361, 362], [361, 363]]}
# gained: {"lines": [353, 354, 355, 356, 357, 358, 360, 361, 363, 364], "branches": [[354, 355], [354, 364], [355, 356], [355, 357], [357, 358], [357, 360], [361, 363]]}

import pytest
import tempfile
import os

class TestConfigGetNamespace:
    def test_get_namespace_with_trim_namespace_false(self):
        """Test get_namespace with trim_namespace=False"""
        from flask.config import Config
        
        with tempfile.TemporaryDirectory() as tmpdir:
            config = Config(tmpdir)
            config['IMAGE_STORE_TYPE'] = 'fs'
            config['IMAGE_STORE_PATH'] = '/var/app/images'
            config['OTHER_CONFIG'] = 'value'
            
            result = config.get_namespace('IMAGE_STORE_', trim_namespace=False, lowercase=False)
            
            expected = {
                'IMAGE_STORE_TYPE': 'fs',
                'IMAGE_STORE_PATH': '/var/app/images'
            }
            assert result == expected

    def test_get_namespace_with_lowercase_false(self):
        """Test get_namespace with lowercase=False"""
        from flask.config import Config
        
        with tempfile.TemporaryDirectory() as tmpdir:
            config = Config(tmpdir)
            config['IMAGE_STORE_TYPE'] = 'fs'
            config['IMAGE_STORE_PATH'] = '/var/app/images'
            config['OTHER_CONFIG'] = 'value'
            
            result = config.get_namespace('IMAGE_STORE_', lowercase=False)
            
            expected = {
                'TYPE': 'fs',
                'PATH': '/var/app/images'
            }
            assert result == expected

    def test_get_namespace_with_both_false(self):
        """Test get_namespace with both lowercase=False and trim_namespace=False"""
        from flask.config import Config
        
        with tempfile.TemporaryDirectory() as tmpdir:
            config = Config(tmpdir)
            config['IMAGE_STORE_TYPE'] = 'fs'
            config['IMAGE_STORE_PATH'] = '/var/app/images'
            config['OTHER_CONFIG'] = 'value'
            
            result = config.get_namespace('IMAGE_STORE_', lowercase=False, trim_namespace=False)
            
            expected = {
                'IMAGE_STORE_TYPE': 'fs',
                'IMAGE_STORE_PATH': '/var/app/images'
            }
            assert result == expected

    def test_get_namespace_empty_result(self):
        """Test get_namespace when no keys match the namespace"""
        from flask.config import Config
        
        with tempfile.TemporaryDirectory() as tmpdir:
            config = Config(tmpdir)
            config['OTHER_CONFIG'] = 'value'
            config['ANOTHER_CONFIG'] = 'another_value'
            
            result = config.get_namespace('IMAGE_STORE_')
            
            assert result == {}
