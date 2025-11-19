# file: src/click/src/click/__init__.py:74-123
# asked: {"lines": [74, 75, 77, 78, 80, 81, 83, 84, 86, 88, 89, 91, 92, 94, 95, 97, 99, 100, 102, 103, 105, 106, 108, 110, 111, 112, 114, 115, 118, 119, 121, 123], "branches": [[77, 78], [77, 88], [88, 89], [88, 99], [99, 100], [99, 110], [110, 111], [110, 123]]}
# gained: {"lines": [74, 75, 77, 78, 80, 81, 83, 84, 86, 88, 89, 91, 92, 94, 95, 97, 99, 100, 102, 103, 105, 106, 108, 110, 111, 112, 114, 115, 118, 119, 121, 123], "branches": [[77, 78], [77, 88], [88, 89], [88, 99], [99, 100], [99, 110], [110, 111], [110, 123]]}

import pytest
import warnings
import importlib.metadata


def test_getattr_basecommand(monkeypatch):
    """Test __getattr__ for 'BaseCommand' attribute."""
    import click
    
    # Mock the import to avoid actual dependency
    mock_base_command = type('MockBaseCommand', (), {})
    monkeypatch.setattr('click.core._BaseCommand', mock_base_command)
    
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        result = click.__getattr__('BaseCommand')
        
        # Check warning was issued
        assert len(w) == 1
        assert issubclass(w[0].category, DeprecationWarning)
        assert "'BaseCommand' is deprecated" in str(w[0].message)
        
        # Check correct object returned
        assert result is mock_base_command


def test_getattr_multicommand(monkeypatch):
    """Test __getattr__ for 'MultiCommand' attribute."""
    import click
    
    # Mock the import to avoid actual dependency
    mock_multi_command = type('MockMultiCommand', (), {})
    monkeypatch.setattr('click.core._MultiCommand', mock_multi_command)
    
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        result = click.__getattr__('MultiCommand')
        
        # Check warning was issued
        assert len(w) == 1
        assert issubclass(w[0].category, DeprecationWarning)
        assert "'MultiCommand' is deprecated" in str(w[0].message)
        
        # Check correct object returned
        assert result is mock_multi_command


def test_getattr_optionparser(monkeypatch):
    """Test __getattr__ for 'OptionParser' attribute."""
    import click
    
    # Mock the import to avoid actual dependency
    mock_option_parser = type('MockOptionParser', (), {})
    monkeypatch.setattr('click.parser._OptionParser', mock_option_parser)
    
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        result = click.__getattr__('OptionParser')
        
        # Check warning was issued
        assert len(w) == 1
        assert issubclass(w[0].category, DeprecationWarning)
        assert "'OptionParser' is deprecated" in str(w[0].message)
        
        # Check correct object returned
        assert result is mock_option_parser


def test_getattr_version(monkeypatch):
    """Test __getattr__ for '__version__' attribute."""
    import click
    
    # Mock importlib.metadata.version to return a fixed version
    mock_version = "8.1.7"
    monkeypatch.setattr(importlib.metadata, 'version', lambda pkg: mock_version)
    
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        result = click.__getattr__('__version__')
        
        # Check warning was issued
        assert len(w) == 1
        assert issubclass(w[0].category, DeprecationWarning)
        assert "'__version__' attribute is deprecated" in str(w[0].message)
        
        # Check correct version returned
        assert result == mock_version


def test_getattr_unknown_attribute():
    """Test __getattr__ for unknown attribute raises AttributeError."""
    import click
    
    with pytest.raises(AttributeError, match="unknown_attr"):
        click.__getattr__('unknown_attr')
