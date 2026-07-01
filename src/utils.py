import logging
import sys
import platform
import shutil
import os
import threading
import time

class ColorFormatter(logging.Formatter):
    """Custom logging formatter that colors stdout but leaves logs plain."""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    
    def format(self, record):
        if record.levelno == logging.INFO:
            return record.getMessage()
        elif record.levelno == logging.WARNING:
            return f"{self.YELLOW}WARNING: {record.getMessage()}{self.RESET}"
        elif record.levelno >= logging.ERROR:
            return f"{self.RED}ERROR: {record.getMessage()}{self.RESET}"
        elif record.levelno == logging.DEBUG:
            return f"{self.BLUE}DEBUG: {record.getMessage()}{self.RESET}"
        return super().format(record)

class Spinner:
    """A context manager that displays a CLI spinner during long operations."""
    def __init__(self, message="Loading", delay=0.1):
        self.message = message
        self.delay = delay
        self.spinner_chars = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
        self._stop_event = threading.Event()
        self._thread = None

    def _spin(self):
        is_tty = sys.stdout.isatty()
        idx = 0
        while not self._stop_event.is_set():
            if is_tty:
                char = self.spinner_chars[idx % len(self.spinner_chars)]
                sys.stdout.write(f"\r\033[94m{char}\033[0m {self.message}...")
                sys.stdout.flush()
                idx += 1
            time.sleep(self.delay)
        if is_tty:
            sys.stdout.write("\r\033[K")
            sys.stdout.flush()

    def __enter__(self):
        if not sys.stdout.isatty():
            sys.stdout.write(f"{self.message}...\n")
            sys.stdout.flush()
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._spin, daemon=True)
        self._thread.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._stop_event.set()
        if self._thread:
            self._thread.join()

def setup_logging(log_file="setup.log"):
    """Configures logging to file and stdout with colors for stdout."""
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    if root_logger.hasHandlers():
        root_logger.handlers.clear()
        
    # File Handler - plain text
    try:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)
    except Exception as e:
        sys.stderr.write(f"Warning: Could not configure file logger: {e}\n")
    
    # Stream Handler - color text
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_formatter = ColorFormatter()
    stream_handler.setFormatter(stream_formatter)
    root_logger.addHandler(stream_handler)

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
