import unittest
import os
import sys

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.schema_validator import validate_config, ConfigValidationError

class TestSchemaValidator(unittest.TestCase):
    def setUp(self):
        # A valid baseline config
        self.valid_config = {
            'default_repo_name': 'test-project',
            'commit_message': 'feat: init',
            'create_venv': True,
            'venv_name': '.venv',
            'packages': {
                'apt-get': ['git', 'curl']
            },
            'templates': {
                'default': {
                    'src': None,
                    'README.md': 'Demo'
                }
            },
            'pip_packages': ['requests', 'pytest'],
            'environment_variables': {
                'project_env': {
                    'DEBUG': 'True'
                },
                'shell_profile': ['export X=1']
            },
            'post_setup_commands': ['echo done']
        }

    def test_valid_config_passes(self):
        try:
            validate_config(self.valid_config)
        except ConfigValidationError:
            self.fail("validate_config raised ConfigValidationError unexpectedly on a valid config.")

    def test_invalid_top_level_types(self):
        invalid_configs = [
            {'default_repo_name': 123},  # Should be string
            {'create_venv': "yes"},     # Should be boolean
            {'pip_packages': "requests"},# Should be list
            {'packages': ["git"]}        # Should be dict
        ]
        for config in invalid_configs:
            with self.assertRaises(ConfigValidationError):
                validate_config(config)

    def test_invalid_nested_packages(self):
        config1 = {'packages': {'apt-get': 'git'}}  # packages val must be list
        config2 = {'packages': {'apt-get': [123]}}   # package item must be string
        with self.assertRaises(ConfigValidationError):
            validate_config(config1)
        with self.assertRaises(ConfigValidationError):
            validate_config(config2)

    def test_invalid_nested_templates(self):
        config1 = {'templates': {'default': 'src'}}   # template val must be dict
        config2 = {'templates': {'default': {123: None}}} # key must be string
        config3 = {'templates': {'default': {'src': 123}}} # value must be string or None or dict
        with self.assertRaises(ConfigValidationError):
            validate_config(config1)
        with self.assertRaises(ConfigValidationError):
            validate_config(config2)
        with self.assertRaises(ConfigValidationError):
            validate_config(config3)

    def test_invalid_nested_env_variables(self):
        config1 = {'environment_variables': {'project_env': 'DEBUG=True'}} # must be dict
        config2 = {'environment_variables': {'project_env': {'DEBUG': 123}}} # val must be str
        config3 = {'environment_variables': {'shell_profile': 'export X=1'}} # must be list
        config4 = {'environment_variables': {'shell_profile': [123]}} # item must be str
        with self.assertRaises(ConfigValidationError):
            validate_config(config1)
        with self.assertRaises(ConfigValidationError):
            validate_config(config2)
        with self.assertRaises(ConfigValidationError):
            validate_config(config3)
        with self.assertRaises(ConfigValidationError):
            validate_config(config4)

    def test_valid_package_managers(self):
        config = {
            'package_managers': {
                'choco': {
                    'update': [],
                    'install': ['choco', 'install', '-y'],
                    'check': ['choco', 'list', '--local-only']
                }
            }
        }
        try:
            validate_config(config)
        except ConfigValidationError:
            self.fail("validate_config raised ConfigValidationError on a valid package_managers config.")

    def test_invalid_package_managers_not_dict(self):
        config = {'package_managers': 'choco'}
        with self.assertRaises(ConfigValidationError):
            validate_config(config)

    def test_invalid_package_managers_missing_key(self):
        # Missing 'check' key
        config = {
            'package_managers': {
                'choco': {
                    'update': [],
                    'install': ['choco', 'install']
                }
            }
        }
        with self.assertRaises(ConfigValidationError):
            validate_config(config)

    def test_invalid_package_managers_bad_type(self):
        # install should be a list, not a string
        config = {
            'package_managers': {
                'choco': {
                    'update': [],
                    'install': 'choco install',
                    'check': []
                }
            }
        }
        with self.assertRaises(ConfigValidationError):
            validate_config(config)

if __name__ == '__main__':
    unittest.main()
