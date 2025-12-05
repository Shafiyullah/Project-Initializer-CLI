import yaml
import os
import sys

def load_config(config_path="config.yaml"):
    """Loads configuration from a YAML file."""
    if not os.path.exists(config_path):
        print(f"Error: Configuration file '{config_path}' not found.")
        sys.exit(1)
        
    try:
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    except ImportError:
        print("Error: PyYAML is not installed. Please install it using 'pip install PyYAML'.")
        sys.exit(1)
    except Exception as e:
        print(f"Error loading configuration: {e}")
        sys.exit(1)
