import argparse
import logging
import os
import shutil
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
    
    # 1. Project Location
    default_loc = os.getcwd()
    location = input(f"Where to create the project? (full path) [{default_loc}]: ").strip() or default_loc
    
    # 2. Project Name
    default_name = config.get('default_repo_name', 'my-project')
    name = input(f"Project Name [{default_name}]: ").strip() or default_name
    
    # Combine Location + Name for the full path
    full_path = os.path.join(location, name)
    config['default_repo_name'] = full_path

    # 3. Virtual Environment
    create_venv = input(f"Create Virtual Environment? (y/n) [{ 'y' if config.get('create_venv') else 'n' }]: ").strip().lower()
    if create_venv:
        config['create_venv'] = create_venv == 'y'

    # 4. Additional Dependencies (moved up)
    deps = input("Additional pip packages (comma-sep) []: ").strip()
    if deps:
        current = config.get('pip_packages', [])
        new_deps = [d.strip() for d in deps.split(',')]
        config['pip_packages'] = list(set(current + new_deps))

    # Template selection
    available_templates = list(config.get('templates', {}).keys())
    if available_templates:
        default_tmpl = 'default' if 'default' in available_templates else available_templates[0]
        tmpl = input(f"Select Template ({', '.join(available_templates)}) [{default_tmpl}]: ").strip()
        if tmpl and tmpl in available_templates:
            config['selected_template'] = tmpl
        else:
            config['selected_template'] = default_tmpl # Fallback

    # 5. Git Check
    git_path = shutil.which("git")
    if git_path:
        print(f"Git detected at: {git_path}")
        # 6. Gitignore Templates (Only if Git is found)
        gi = input("Gitignore templates (comma-sep, e.g. python,windows) []: ").strip()
        if gi:
            config['gitignore_types'] = [t.strip() for t in gi.split(',')]
    else:
        print("WARNING: Git not found. Skipping .gitignore setup and Git initialization.")

    return config

def main():
    setup_logging()
    
    parser = argparse.ArgumentParser(description="Automate project setup and configuration.")
    parser.add_argument("--config", type=str, default="config.yaml", help="Path to configuration file.")
    parser.add_argument("--name", type=str, help="Name of the new project/repository.")
    parser.add_argument("--no-venv", action="store_true", help="Skip virtual environment creation.")
    parser.add_argument("--interactive", action="store_true", help="Run in interactive mode.")
    parser.add_argument("--template", type=str, help="Project template to use.")
    parser.add_argument("--dry-run", action="store_true", help="Simulate actions without making changes.")
    parser.add_argument("--force", action="store_true", help="Overwrite existing project directory.")
    
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
    if args.template:
        config['selected_template'] = args.template
    
    # Determine which template structure to use
    selected_tmpl_name = config.get('selected_template', 'default')
    templates = config.get('templates', {})
    if selected_tmpl_name not in templates:
        logging.warning(f"Template '{selected_tmpl_name}' not found. Using 'default' (if available) or empty.")
        selected_tmpl_name = 'default'
    
    project_structure = templates.get(selected_tmpl_name, {})
        
    repo_name = config['default_repo_name']
    
    if args.dry_run:
        logging.info("!!! DRY RUN MODE - No changes will be made !!!")

    logging.info(f"Starting setup for: {repo_name} (Template: {selected_tmpl_name})")

    # 1. Install System Packages
    mgr = get_package_manager()
    if mgr: 
        install_packages(mgr, config.get('packages', {}), dry_run=args.dry_run)

    # 2. Create Structure & Git Init
    create_project_structure(repo_name, project_structure, dry_run=args.dry_run, force=args.force)

    # 3. Security Check
    secure_project(repo_name, gitignore_types=config.get('gitignore_types'), dry_run=args.dry_run)

    # 4. Environment Variables
    setup_env_vars(repo_name, config.get('environment_variables', {}), dry_run=args.dry_run)

    # 5. Virtual Environment
    setup_venv(repo_name, config.get('venv_name', '.venv'), config.get('pip_packages', []), config.get('create_venv', True), dry_run=args.dry_run)

    # 6. Hooks
    run_hooks(repo_name, config.get('venv_name', '.venv'), config.get('post_setup_commands', []), dry_run=args.dry_run)

    # 7. Commit
    final_commit(repo_name, config.get('commit_message', 'Initial commit'), dry_run=args.dry_run)

    logging.info("\n--- DONE ---")

if __name__ == "__main__":
    main()
