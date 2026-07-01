class ConfigValidationError(Exception):
    """Exception raised when config validation fails."""
    pass

def validate_config(config: dict) -> None:
    """Validates the configuration structure and types."""
    if not isinstance(config, dict):
        raise ConfigValidationError("Configuration must be a dictionary.")

    # List of expected top-level keys and their expected types
    # (some may be optional, but if present, they must match the type)
    expected_keys = {
        'default_repo_name': str,
        'commit_message': str,
        'create_venv': bool,
        'venv_name': str,
        'packages': dict,
        'templates': dict,
        'pip_packages': list,
        'environment_variables': dict,
        'post_setup_commands': list,
        'selected_template': str,
        'package_managers': dict
    }

    for key, expected_type in expected_keys.items():
        if key in config:
            val = config[key]
            if val is not None and not isinstance(val, expected_type):
                raise ConfigValidationError(
                    f"Config key '{key}' has invalid type. "
                    f"Expected {expected_type.__name__}, got {type(val).__name__}."
                )

    # Detailed validation for nested keys
    # 1. Validate packages
    if 'packages' in config and config['packages'] is not None:
        for pm, pkgs in config['packages'].items():
            if not isinstance(pkgs, list):
                raise ConfigValidationError(f"Packages configuration for '{pm}' must be a list.")
            for pkg in pkgs:
                if not isinstance(pkg, str):
                    raise ConfigValidationError(f"Package items under '{pm}' must be strings.")

    # 2. Validate templates
    if 'templates' in config and config['templates'] is not None:
        for tname, tstruct in config['templates'].items():
            if not isinstance(tstruct, dict):
                raise ConfigValidationError(f"Template structure for '{tname}' must be a dictionary.")
            for k, v in tstruct.items():
                if not isinstance(k, str):
                    raise ConfigValidationError(f"Template structure key under '{tname}' must be a string.")
                if v is not None and not isinstance(v, (str, dict)):
                    raise ConfigValidationError(
                        f"Template item '{k}' under '{tname}' must be a string, a nested structure dict, or null."
                    )

    # 3. Validate pip_packages
    if 'pip_packages' in config and config['pip_packages'] is not None:
        for pkg in config['pip_packages']:
            if not isinstance(pkg, str):
                raise ConfigValidationError("pip_packages items must be strings.")

    # 4. Validate environment_variables
    if 'environment_variables' in config and config['environment_variables'] is not None:
        env = config['environment_variables']
        if 'project_env' in env and env['project_env'] is not None:
            if not isinstance(env['project_env'], dict):
                raise ConfigValidationError("environment_variables.project_env must be a dictionary.")
            for k, v in env['project_env'].items():
                if not isinstance(k, str) or not isinstance(v, str):
                    raise ConfigValidationError("project_env keys and values must be strings.")
        if 'shell_profile' in env and env['shell_profile'] is not None:
            if not isinstance(env['shell_profile'], list):
                raise ConfigValidationError("environment_variables.shell_profile must be a list.")
            for val in env['shell_profile']:
                if not isinstance(val, str):
                    raise ConfigValidationError("shell_profile items must be strings.")

    # 5. Validate post_setup_commands
    if 'post_setup_commands' in config and config['post_setup_commands'] is not None:
        for cmd in config['post_setup_commands']:
            if not isinstance(cmd, str):
                raise ConfigValidationError("post_setup_commands items must be strings.")

    # 6. Validate package_managers
    if 'package_managers' in config and config['package_managers'] is not None:
        required_sub_keys = {'update', 'install', 'check'}
        for mgr_name, mgr_cmds in config['package_managers'].items():
            if not isinstance(mgr_cmds, dict):
                raise ConfigValidationError(
                    f"Package manager '{mgr_name}' must be a dictionary with keys: {required_sub_keys}."
                )
            for sub_key in required_sub_keys:
                if sub_key not in mgr_cmds:
                    raise ConfigValidationError(
                        f"Package manager '{mgr_name}' is missing required key '{sub_key}'."
                    )
                if not isinstance(mgr_cmds[sub_key], list):
                    raise ConfigValidationError(
                        f"Package manager '{mgr_name}.{sub_key}' must be a list."
                    )
                for item in mgr_cmds[sub_key]:
                    if not isinstance(item, str):
                        raise ConfigValidationError(
                            f"Package manager '{mgr_name}.{sub_key}' items must be strings."
                        )
