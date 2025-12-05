import argparse
import logging
from .config_loader import load_config
from .utils import setup_logging, get_package_manager
from .core import (
    install_packages,
    create_project_structure,
    secure_project,
    setup_env_vars,
    setup_venv,
    run_hooks,
    final_commit
)

def interactive_mode(config):
    """
    Prompts the user for configuration overrides.
    """
    print("\n--- Interactive Project Setup ---")
    
    name = input(f"Project Name [{config.get('default_repo_name', 'my-project')}]: ").strip()
    if name:
        config['default_repo_name'] = name
        
    create_venv = input(f"Create Virtual Environment? (y/n) [{ 'y' if config.get('create_venv') else 'n' }]: ").strip().lower()
    if create_venv:
        config['create_venv'] = create_venv == 'y'

    return config

def main():
    setup_logging()
    
    parser = argparse.ArgumentParser(description="Automate project setup and configuration.")
    parser.add_argument("--config", type=str, default="config.yaml", help="Path to configuration file.")
    parser.add_argument("--name", type=str, help="Name of the new project/repository.")
    parser.add_argument("--no-venv", action="store_true", help="Skip virtual environment creation.")
    parser.add_argument("--interactive", action="store_true", help="Run in interactive mode.")
    
    args = parser.parse_args()
    
    # Load Config
    config = load_config(args.config)
    
    # Interactive Mode Override
    if args.interactive or (not args.name and not args.no_venv):
        config = interactive_mode(config)
    
    # CLI Overrides
    if args.name:
        config['default_repo_name'] = args.name
    if args.no_venv:
        config['create_venv'] = False
        
    repo_name = config['default_repo_name']
    logging.info(f"Starting setup for: {repo_name}")

    # 1. Install System Packages
    mgr = get_package_manager()
    if mgr: 
        install_packages(mgr, config.get('packages', {}))

    # 2. Create Structure & Git Init
    create_project_structure(repo_name, config.get('structure', {}))

    # 3. Security Check
    secure_project(repo_name)

    # 4. Environment Variables
    setup_env_vars(repo_name, config.get('environment_variables', {}))

    # 5. Virtual Environment
    setup_venv(repo_name, config.get('venv_name', '.venv'), config.get('pip_packages', []), config.get('create_venv', True))

    # 6. Hooks
    run_hooks(repo_name, config.get('venv_name', '.venv'), config.get('post_setup_commands', []))

    # 7. Commit
    final_commit(repo_name, config.get('commit_message', 'Initial commit'))

    logging.info("\n--- DONE ---")

if __name__ == "__main__":
    main()
