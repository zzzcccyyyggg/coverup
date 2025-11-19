# file: src/click/src/click/decorators.py:404-418
# asked: {"lines": [404, 412, 413, 415, 416, 417, 418], "branches": [[412, 413], [412, 415]]}
# gained: {"lines": [404, 412, 413, 415, 416, 417, 418], "branches": [[412, 413], [412, 415]]}

import pytest
import click
from click.decorators import password_option

def test_password_option_with_default_param_decls():
    """Test password_option with no param_decls (uses default --password)."""
    
    @password_option()
    def test_cmd(password):
        return password
    
    # Verify the command was decorated properly
    assert hasattr(test_cmd, '__click_params__')
    params = test_cmd.__click_params__
    assert len(params) == 1
    param = params[0]
    assert param.name == 'password'
    assert param.opts == ['--password']
    # When prompt=True is passed, it gets converted to the parameter name capitalized
    assert param.prompt == 'Password'
    assert param.confirmation_prompt is True
    assert param.hide_input is True

def test_password_option_with_custom_param_decls():
    """Test password_option with custom param_decls."""
    
    @password_option('--pwd')
    def test_cmd(pwd):
        return pwd
    
    # Verify the command was decorated properly
    assert hasattr(test_cmd, '__click_params__')
    params = test_cmd.__click_params__
    assert len(params) == 1
    param = params[0]
    assert param.name == 'pwd'
    assert param.opts == ['--pwd']
    # When prompt=True is passed, it gets converted to the parameter name capitalized
    assert param.prompt == 'Pwd'
    assert param.confirmation_prompt is True
    assert param.hide_input is True

def test_password_option_with_overridden_kwargs():
    """Test password_option with overridden kwargs (should still set defaults)."""
    
    @password_option(prompt='Custom prompt', hide_input=False)
    def test_cmd(password):
        return password
    
    # Verify the command was decorated properly
    assert hasattr(test_cmd, '__click_params__')
    params = test_cmd.__click_params__
    assert len(params) == 1
    param = params[0]
    assert param.name == 'password'
    assert param.opts == ['--password']
    # The explicitly passed values should be preserved
    assert param.prompt == 'Custom prompt'
    assert param.hide_input is False
    # But confirmation_prompt should still be set to True
    assert param.confirmation_prompt is True

def test_password_option_with_explicit_prompt_false():
    """Test password_option with explicit prompt=False."""
    
    @password_option(prompt=False)
    def test_cmd(password):
        return password
    
    # Verify the command was decorated properly
    assert hasattr(test_cmd, '__click_params__')
    params = test_cmd.__click_params__
    assert len(params) == 1
    param = params[0]
    assert param.name == 'password'
    assert param.opts == ['--password']
    # When prompt=False is explicitly passed, it should be None
    assert param.prompt is None
    assert param.confirmation_prompt is True
    assert param.hide_input is True
