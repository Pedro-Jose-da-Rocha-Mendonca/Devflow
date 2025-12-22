#!/usr/bin/env python3
"""
Cross-Platform Project Workflow Initialization

Automatically detects the operating system and runs the appropriate setup wizard.
Works on Windows, macOS, and Linux.

Usage:
    python init-project-workflow.py
"""

import os
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent


def get_platform():
    """Detect the current platform."""
    if sys.platform == "win32":
        return "windows"
    elif sys.platform == "darwin":
        return "macos"
    else:
        return "linux"


def run_windows():
    """Run PowerShell script on Windows."""
    script = SCRIPT_DIR / "init-project-workflow.ps1"

    if not script.exists():
        print(f"Error: PowerShell script not found: {script}")
        return 1

    cmd = ["powershell", "-ExecutionPolicy", "Bypass", "-File", str(script)]
    return subprocess.call(cmd)


def run_unix():
    """Run shell script on macOS/Linux."""
    script = SCRIPT_DIR / "init-project-workflow.sh"

    if not script.exists():
        print(f"Error: Shell script not found: {script}")
        return 1

    # Ensure script is executable
    os.chmod(script, 0o755)

    cmd = [str(script)]
    return subprocess.call(cmd)


def main():
    platform = get_platform()

    print(f"Detected platform: {platform}")
    print()

    if platform == "windows":
        return run_windows()
    else:
        return run_unix()


if __name__ == "__main__":
    sys.exit(main())
