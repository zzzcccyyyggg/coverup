# file: src/flask/src/flask/config.py:304-321
# asked: {"lines": [304, 305, 314, 315, 316, 317, 318, 319, 320, 321], "branches": [[315, 316], [315, 317], [318, 319], [318, 321], [319, 318], [319, 320]]}
# gained: {"lines": [304, 305, 314, 315, 316, 317, 318, 319, 320, 321], "branches": [[315, 316], [315, 317], [318, 319], [318, 321], [319, 318], [319, 320]]}

import pytest
import typing as t
import tempfile
import os
from flask.config import Config


class TestConfigFromMapping:
    """Test cases for Config.from_mapping method to achieve full coverage."""
    
    def test_from_mapping_with_none_mapping_and_kwargs(self):
        """Test from_mapping with mapping=None and kwargs only."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = Config(tmpdir)
            result = config.from_mapping(None, TEST_KEY="test_value", ANOTHER_KEY=123)
            
            assert result is True
            assert config["TEST_KEY"] == "test_value"
            assert config["ANOTHER_KEY"] == 123
            assert len(config) == 2
    
    def test_from_mapping_with_mapping_and_kwargs(self):
        """Test from_mapping with both mapping and kwargs."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = Config(tmpdir)
            mapping = {"MAPPING_KEY": "mapping_value", "lower_key": "should_be_ignored"}
            result = config.from_mapping(mapping, KWARG_KEY="kwarg_value", another_lower="ignored")
            
            assert result is True
            assert config["MAPPING_KEY"] == "mapping_value"
            assert config["KWARG_KEY"] == "kwarg_value"
            assert "lower_key" not in config
            assert "another_lower" not in config
            assert len(config) == 2
    
    def test_from_mapping_with_only_mapping(self):
        """Test from_mapping with only mapping parameter."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = Config(tmpdir)
            mapping = {"UPPER_KEY": "upper_value", "lower_key": "ignored", "ANOTHER_UPPER": 456}
            result = config.from_mapping(mapping)
            
            assert result is True
            assert config["UPPER_KEY"] == "upper_value"
            assert config["ANOTHER_UPPER"] == 456
            assert "lower_key" not in config
            assert len(config) == 2
    
    def test_from_mapping_with_empty_mapping_and_kwargs(self):
        """Test from_mapping with empty mapping and kwargs."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = Config(tmpdir)
            result = config.from_mapping({}, lower="ignored", another_lower="also_ignored")
            
            assert result is True
            assert len(config) == 0
    
    def test_from_mapping_with_mixed_case_keys(self):
        """Test from_mapping with mixed case keys."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = Config(tmpdir)
            mapping = {"UPPER": "upper", "MixedCase": "mixed", "lower": "lower"}
            result = config.from_mapping(mapping, ANOTHER_UPPER="another", mixedCase="mixed2")
            
            assert result is True
            assert config["UPPER"] == "upper"
            assert config["ANOTHER_UPPER"] == "another"
            assert "MixedCase" not in config
            assert "mixedCase" not in config
            assert "lower" not in config
            assert len(config) == 2
