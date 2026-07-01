import os
import subprocess
import shutil
from datetime import datetime


def substitute_variables(content: str, repo_path: str) -> str:
    """
    Replaces template placeholders in content with contextual values.

    Supported placeholders:
        {{project_name}} - basename of the repo_path
        {{author}}        - git user.name or OS username fallback
        {{date}}          - current date in YYYY-MM-DD format
        {{year}}          - current year as YYYY
    """
    project_name = os.path.basename(os.path.normpath(repo_path))
    author = _get_author()
    now = datetime.now()

    replacements = {
        "{{project_name}}": project_name,
        "{{author}}": author,
        "{{date}}": now.strftime("%Y-%m-%d"),
        "{{year}}": str(now.year),
    }

    for placeholder, value in replacements.items():
        content = content.replace(placeholder, value)

    return content


def _get_author() -> str:
    """Returns the git user.name if available, otherwise the OS username."""
    if shutil.which("git"):
        try:
            result = subprocess.run(
                ["git", "config", "user.name"],
                capture_output=True,
                text=True,
            )
            name = result.stdout.strip()
            if name:
                return name
        except Exception:
            pass

    # Fallback to OS username
    return os.environ.get("USER") or os.environ.get("USERNAME") or "Unknown"
