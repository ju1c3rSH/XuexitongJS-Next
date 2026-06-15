"""Auto-generated version from git history. Falls back to "1.0.0" when .git unavailable."""

import subprocess
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent


def compute_version() -> str:
    git_dir = _PROJECT_ROOT / ".git"
    if git_dir.is_dir():
        try:
            total = int(subprocess.check_output(
                ["git", "rev-list", "--count", "HEAD"],
                cwd=_PROJECT_ROOT, text=True
            ).strip())
            feats = int(subprocess.check_output(
                ["git", "rev-list", "--count", "--grep=^feat", "HEAD"],
                cwd=_PROJECT_ROOT, text=True
            ).strip())
            return f"1.{feats}.{total}"
        except Exception:
            pass
    try:
        from importlib.metadata import version as _pv
        return _pv("uXueXiTongX")
    except Exception:
        pass
    return "1.0.0"


__version__ = compute_version()
