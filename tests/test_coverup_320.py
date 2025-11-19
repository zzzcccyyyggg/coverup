# file: src/flask/src/flask/cli.py:1048-1107
# asked: {"lines": [1063, 1065, 1066, 1067, 1069, 1070, 1071, 1072, 1074, 1075, 1076, 1077, 1080, 1081, 1083, 1084, 1086, 1087, 1089, 1090, 1091, 1093, 1094, 1096, 1097, 1098, 1099, 1101, 1102, 1103, 1104, 1106, 1107], "branches": [[1065, 1066], [1065, 1069], [1074, 1075], [1074, 1086], [1080, 1081], [1080, 1083], [1089, 1090], [1089, 1093], [1106, 0], [1106, 1107]]}
# gained: {"lines": [1063, 1065, 1066, 1067, 1069, 1070, 1071, 1072, 1074, 1075, 1076, 1077, 1080, 1081, 1083, 1084, 1086, 1087, 1089, 1090, 1091, 1093, 1094, 1096, 1097, 1101, 1102, 1103, 1104, 1106, 1107], "branches": [[1065, 1066], [1065, 1069], [1074, 1075], [1074, 1086], [1080, 1081], [1080, 1083], [1089, 1090], [1089, 1093], [1106, 0], [1106, 1107]]}

import pytest
from flask import Flask
from flask.cli import routes_command
from click.testing import CliRunner
from werkzeug.routing import Map, Rule

class TestRoutesCommand:
    def test_routes_command_no_routes(self):
        """Test routes command when no routes are registered."""
        app = Flask(__name__)
        # Clear all routes including the default static route
        app.url_map = Map()
        
        runner = CliRunner()
        
        with app.app_context():
            result = runner.invoke(routes_command)
            assert result.exit_code == 0
            assert "No routes were registered." in result.output

    def test_routes_command_with_routes_and_domain(self):
        """Test routes command with routes and domain/host matching."""
        app = Flask(__name__)
        app.url_map.host_matching = True
        
        # Clear default routes and add our test routes
        app.url_map = Map(host_matching=True)
        rule1 = Rule('/test1', endpoint='test1', methods=['GET'], host='example.com')
        rule2 = Rule('/test2', endpoint='test2', methods=['POST'], host='api.example.com')
        app.url_map.add(rule1)
        app.url_map.add(rule2)
        
        runner = CliRunner()
        
        with app.app_context():
            result = runner.invoke(routes_command, ['--sort', 'domain'])
            assert result.exit_code == 0
            assert "test1" in result.output
            assert "test2" in result.output
            assert "example.com" in result.output
            assert "api.example.com" in result.output
            assert "Host" in result.output

    def test_routes_command_with_subdomain(self):
        """Test routes command with subdomain matching."""
        app = Flask(__name__)
        app.url_map.host_matching = False
        
        # Clear default routes and add our test routes
        app.url_map = Map(host_matching=False)
        rule1 = Rule('/test1', endpoint='test1', methods=['GET'], subdomain='api')
        rule2 = Rule('/test2', endpoint='test2', methods=['POST'], subdomain='www')
        app.url_map.add(rule1)
        app.url_map.add(rule2)
        
        runner = CliRunner()
        
        with app.app_context():
            result = runner.invoke(routes_command, ['--sort', 'domain'])
            assert result.exit_code == 0
            assert "test1" in result.output
            assert "test2" in result.output
            assert "api" in result.output
            assert "www" in result.output
            assert "Subdomain" in result.output

    def test_routes_command_all_methods(self):
        """Test routes command with --all-methods flag."""
        app = Flask(__name__)
        
        # Clear default routes and add our test route
        app.url_map = Map()
        rule = Rule('/test', endpoint='test', methods=['GET', 'HEAD', 'OPTIONS'])
        app.url_map.add(rule)
        
        runner = CliRunner()
        
        with app.app_context():
            # Test without --all-methods (should filter HEAD and OPTIONS)
            result = runner.invoke(routes_command)
            assert result.exit_code == 0
            assert "GET" in result.output
            assert "HEAD" not in result.output
            assert "OPTIONS" not in result.output
            
            # Test with --all-methods (should show all methods)
            result = runner.invoke(routes_command, ['--all-methods'])
            assert result.exit_code == 0
            assert "GET" in result.output
            assert "HEAD" in result.output
            assert "OPTIONS" in result.output

    def test_routes_command_different_sort_options(self):
        """Test routes command with different sort options."""
        app = Flask(__name__)
        
        # Clear default routes and add our test routes
        app.url_map = Map()
        rule1 = Rule('/aaa', endpoint='z_endpoint', methods=['POST'])
        rule2 = Rule('/zzz', endpoint='a_endpoint', methods=['GET'])
        app.url_map.add(rule1)
        app.url_map.add(rule2)
        
        runner = CliRunner()
        
        with app.app_context():
            # Test sorting by endpoint
            result = runner.invoke(routes_command, ['--sort', 'endpoint'])
            assert result.exit_code == 0
            
            # Test sorting by methods
            result = runner.invoke(routes_command, ['--sort', 'methods'])
            assert result.exit_code == 0
            
            # Test sorting by rule
            result = runner.invoke(routes_command, ['--sort', 'rule'])
            assert result.exit_code == 0

    def test_routes_command_empty_methods(self):
        """Test routes command with rules that have no methods."""
        app = Flask(__name__)
        
        # Clear default routes and add our test route
        app.url_map = Map()
        rule = Rule('/test', endpoint='test')
        app.url_map.add(rule)
        
        runner = CliRunner()
        
        with app.app_context():
            result = runner.invoke(routes_command)
            assert result.exit_code == 0
            assert "test" in result.output
            # Should show empty methods column

    def test_routes_command_with_mixed_domain_rules(self):
        """Test routes command with mix of rules with and without domain/subdomain."""
        app = Flask(__name__)
        app.url_map.host_matching = True
        
        # Clear default routes and add our test routes
        app.url_map = Map(host_matching=True)
        rule1 = Rule('/with_host', endpoint='with_host', methods=['GET'], host='example.com')
        rule2 = Rule('/no_host', endpoint='no_host', methods=['POST'])  # No host specified
        app.url_map.add(rule1)
        app.url_map.add(rule2)
        
        runner = CliRunner()
        
        with app.app_context():
            result = runner.invoke(routes_command)
            assert result.exit_code == 0
            assert "with_host" in result.output
            assert "no_host" in result.output
            assert "example.com" in result.output
            # The rule without host should show empty string in host column

    def test_routes_command_no_domain_column_when_no_domains(self):
        """Test that domain column is not shown when no rules have domains."""
        app = Flask(__name__)
        app.url_map.host_matching = True
        
        # Clear default routes and add routes without domains
        app.url_map = Map(host_matching=True)
        rule1 = Rule('/test1', endpoint='test1', methods=['GET'])
        rule2 = Rule('/test2', endpoint='test2', methods=['POST'])
        app.url_map.add(rule1)
        app.url_map.add(rule2)
        
        runner = CliRunner()
        
        with app.app_context():
            result = runner.invoke(routes_command)
            assert result.exit_code == 0
            assert "test1" in result.output
            assert "test2" in result.output
            # Should not show Host column since no rules have hosts
            assert "Host" not in result.output
