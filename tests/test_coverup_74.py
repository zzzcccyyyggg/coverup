# file: src/flask/src/flask/blueprints.py:104-128
# asked: {"lines": [104, 105, 120, 121, 123, 125, 126, 128], "branches": [[120, 121], [120, 123], [125, 126], [125, 128]]}
# gained: {"lines": [104, 105, 120, 121, 123, 125, 126, 128], "branches": [[120, 121], [120, 123], [125, 126], [125, 128]]}

import pytest
import tempfile
import os
from flask import Blueprint

class TestBlueprintOpenResource:
    def test_open_resource_text_mode(self):
        """Test opening a resource in text mode with encoding."""
        bp = Blueprint('test', __name__)
        
        # Create a temporary file in the blueprint's root path
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', dir=bp.root_path, delete=False) as f:
            f.write('test content')
            temp_path = f.name
        
        try:
            resource_name = os.path.basename(temp_path)
            with bp.open_resource(resource_name, mode='r', encoding='utf-8') as f:
                content = f.read()
                assert content == 'test content'
        finally:
            os.unlink(temp_path)

    def test_open_resource_binary_mode(self):
        """Test opening a resource in binary mode."""
        bp = Blueprint('test', __name__)
        
        # Create a temporary file in the blueprint's root path
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.bin', dir=bp.root_path, delete=False) as f:
            f.write(b'test binary content')
            temp_path = f.name
        
        try:
            resource_name = os.path.basename(temp_path)
            with bp.open_resource(resource_name, mode='rb') as f:
                content = f.read()
                assert content == b'test binary content'
        finally:
            os.unlink(temp_path)

    def test_open_resource_rt_mode(self):
        """Test opening a resource in 'rt' text mode."""
        bp = Blueprint('test', __name__)
        
        # Create a temporary file in the blueprint's root path
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', dir=bp.root_path, delete=False) as f:
            f.write('test rt content')
            temp_path = f.name
        
        try:
            resource_name = os.path.basename(temp_path)
            with bp.open_resource(resource_name, mode='rt', encoding='utf-8') as f:
                content = f.read()
                assert content == 'test rt content'
        finally:
            os.unlink(temp_path)

    def test_open_resource_invalid_mode(self):
        """Test that invalid mode raises ValueError."""
        bp = Blueprint('test', __name__)
        
        with pytest.raises(ValueError, match="Resources can only be opened for reading."):
            bp.open_resource('nonexistent.txt', mode='w')

    def test_open_resource_nonexistent_file(self):
        """Test opening a non-existent resource raises FileNotFoundError."""
        bp = Blueprint('test', __name__)
        
        with pytest.raises(FileNotFoundError):
            bp.open_resource('nonexistent_file.txt', mode='r')
