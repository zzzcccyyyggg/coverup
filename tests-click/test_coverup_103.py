# file: src/click/src/click/core.py:495-531
# asked: {"lines": [495, 496, 524, 525, 526, 527, 528, 530, 531], "branches": [[524, 525], [524, 526], [530, 0], [530, 531]]}
# gained: {"lines": [495, 496, 524, 525, 526, 527, 528, 530, 531], "branches": [[524, 525], [524, 526], [530, 0], [530, 531]]}

import pytest
from click.core import Context
from click import Command
from click.globals import get_current_context


class TestContextScope:
    def test_scope_with_cleanup_true(self):
        """Test scope with cleanup=True (default) - should execute lines 524-531 with cleanup=True path"""
        cmd = Command('test_cmd')
        ctx = Context(cmd)
        
        # Initial depth should be 0
        assert ctx._depth == 0
        
        with ctx.scope(cleanup=True) as scoped_ctx:
            # Should be the same context
            assert scoped_ctx is ctx
            # Depth should be increased by __enter__
            assert ctx._depth == 1
            # Should be current context
            assert get_current_context() is ctx
        
        # After scope, depth should be back to 0 (cleanup=True runs __exit__)
        assert ctx._depth == 0

    def test_scope_with_cleanup_false(self):
        """Test scope with cleanup=False - should execute lines 524-531 with cleanup=False path"""
        cmd = Command('test_cmd')
        ctx = Context(cmd)
        
        # Initial depth should be 0
        assert ctx._depth == 0
        
        with ctx.scope(cleanup=False) as scoped_ctx:
            # Should be the same context
            assert scoped_ctx is ctx
            # Depth should be increased by 2 (one from scope, one from __enter__)
            assert ctx._depth == 2
            # Should be current context
            assert get_current_context() is ctx
        
        # After scope, depth should be back to 0 (cleanup=False manually adjusts depth)
        assert ctx._depth == 0

    def test_scope_as_context_manager_equivalent(self):
        """Test that using scope() is equivalent to using context directly as context manager"""
        cmd = Command('test_cmd')
        ctx1 = Context(cmd)
        ctx2 = Context(cmd)
        
        # Test direct context manager usage
        with ctx1:
            assert get_current_context() is ctx1
            assert ctx1._depth == 1
        
        # Test scope() usage with cleanup=True (default)
        with ctx2.scope():
            assert get_current_context() is ctx2
            assert ctx2._depth == 1
        
        # Both should end with depth 0
        assert ctx1._depth == 0
        assert ctx2._depth == 0

    def test_scope_nested_with_cleanup_false(self):
        """Test nested scope calls with cleanup=False to verify depth management"""
        cmd = Command('test_cmd')
        ctx = Context(cmd)
        
        assert ctx._depth == 0
        
        # First scope with cleanup=False
        with ctx.scope(cleanup=False):
            assert ctx._depth == 2
            
            # Nested scope with cleanup=False
            with ctx.scope(cleanup=False):
                assert ctx._depth == 4
            
            # After nested scope, depth should be back to 2
            assert ctx._depth == 2
        
        # After all scopes, depth should be back to 0
        assert ctx._depth == 0

    def test_scope_exception_with_cleanup_false(self):
        """Test that scope properly handles exceptions when cleanup=False"""
        cmd = Command('test_cmd')
        ctx = Context(cmd)
        
        assert ctx._depth == 0
        
        try:
            with ctx.scope(cleanup=False):
                assert ctx._depth == 2
                raise ValueError("Test exception")
        except ValueError:
            pass
        
        # Even with exception, depth should be properly restored
        assert ctx._depth == 0
