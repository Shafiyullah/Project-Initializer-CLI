import logging
import sys
import platform
import shutil
import os

def setup_logging(log_file="setup.log"):
    """Configures logging to file and stdout."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ])

def is_admin() -> bool:
    """Check if the script is running with administrative privileges."""
    try:
        if platform.system() == "Windows":
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        else: 
            # POSIX (Linux, macOS)
            return os.geteuid() == 0
    except Exception as e:
        logging.error(f"Could not determine admin status: {e}")
        return False

def get_package_manager() -> str:
    """Detects the appropriate package manager for the system."""
    system = platform.system()
    if system == "Linux":
        if shutil.which("apt-get"): return "apt-get"
        if shutil.which("dnf"): return "dnf" 
        if shutil.which("yum"): return "yum"
        if shutil.which("pacman"): return "pacman"
    elif system == "Darwin": 
        if shutil.which("brew"): return "brew"
    elif system == "Windows":
        if shutil.which("winget"): return "winget"
    return None
