#!/usr/bin/env python3
"""
Update README.md version from CHANGELOG.md.

This script extracts the latest version from CHANGELOG.md and updates
the version block in README.md. Run this after updating the changelog.

Usage:
    python update_version.py                    # Update README from CHANGELOG
    python update_version.py --check            # Check if versions match
    python update_version.py --version 1.7.0    # Set specific version
"""

import argparse
import re
import sys
from datetime import date
from pathlib import Path


def get_project_root() -> Path:
    """Get the project root directory."""
    script_dir = Path(__file__).resolve().parent
    return script_dir.parent.parent


def get_changelog_version(changelog_path: Path) -> str | None:
    """Extract the latest version from CHANGELOG.md."""
    if not changelog_path.exists():
        print(f"Error: CHANGELOG.md not found at {changelog_path}")
        return None

    content = changelog_path.read_text()
    # Match version pattern like [1.6.0] - 2025-12-21
    match = re.search(r"## \[(\d+\.\d+\.\d+)\]", content)
    if match:
        return match.group(1)
    return None


def get_readme_version(readme_path: Path) -> str | None:
    """Extract the current version from README.md."""
    if not readme_path.exists():
        print(f"Error: README.md not found at {readme_path}")
        return None

    content = readme_path.read_text()
    match = re.search(r"\*\*Version\*\*: (\d+\.\d+\.\d+)", content)
    if match:
        return match.group(1)
    return None


def update_readme_version(readme_path: Path, version: str) -> bool:
    """Update the version in README.md."""
    if not readme_path.exists():
        print(f"Error: README.md not found at {readme_path}")
        return False

    content = readme_path.read_text()
    today = date.today().isoformat()

    # Pattern to match the version block (with or without markers)
    pattern = r"(<!-- VERSION_START.*?-->.*?)?\*\*Version\*\*: \d+\.\d+\.\d+\n\*\*Status\*\*: ([^\n]+)\n\*\*Last Updated\*\*: \d{4}-\d{2}-\d{2}(.*?<!-- VERSION_END -->)?"
    
    # Check if markers exist
    if "<!-- VERSION_START" in content:
        replacement = f"""<!-- VERSION_START - Auto-updated by update_version.py -->
**Version**: {version}
**Status**: \\2
**Last Updated**: {today}
<!-- VERSION_END -->"""
    else:
        replacement = f"""**Version**: {version}
**Status**: \\2
**Last Updated**: {today}"""

    new_content, count = re.subn(pattern, replacement, content, flags=re.DOTALL)
    
    if count == 0:
        print("Error: Could not find version block in README.md")
        return False

    readme_path.write_text(new_content)
    return True


def update_pyproject_version(pyproject_path: Path, version: str) -> bool:
    """Update the version in pyproject.toml."""
    if not pyproject_path.exists():
        print(f"Warning: pyproject.toml not found at {pyproject_path}")
        return False

    content = pyproject_path.read_text()
    pattern = r'version = "\d+\.\d+\.\d+"'
    replacement = f'version = "{version}"'
    
    new_content, count = re.subn(pattern, replacement, content, count=1)
    
    if count == 0:
        print("Warning: Could not find version in pyproject.toml")
        return False

    pyproject_path.write_text(new_content)
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Update README.md version from CHANGELOG.md"
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check if versions match without updating",
    )
    parser.add_argument(
        "--version",
        type=str,
        help="Set a specific version instead of reading from CHANGELOG",
    )
    parser.add_argument(
        "--sync-pyproject",
        action="store_true",
        help="Also update version in pyproject.toml",
    )
    args = parser.parse_args()

    root = get_project_root()
    changelog_path = root / "CHANGELOG.md"
    readme_path = root / "README.md"
    pyproject_path = root / "pyproject.toml"

    # Get versions
    changelog_version = get_changelog_version(changelog_path)
    readme_version = get_readme_version(readme_path)

    if args.version:
        target_version = args.version
    elif changelog_version:
        target_version = changelog_version
    else:
        print("Error: Could not determine version from CHANGELOG.md")
        sys.exit(1)

    print(f"CHANGELOG version: {changelog_version or 'not found'}")
    print(f"README version:    {readme_version or 'not found'}")
    print(f"Target version:    {target_version}")

    if args.check:
        if readme_version == target_version:
            print("✓ Versions are in sync")
            sys.exit(0)
        else:
            print("✗ Versions are out of sync")
            sys.exit(1)

    # Update README
    if readme_version == target_version:
        print("README already at target version, updating date only...")
    
    if update_readme_version(readme_path, target_version):
        print(f"✓ Updated README.md to version {target_version}")
    else:
        print("✗ Failed to update README.md")
        sys.exit(1)

    # Optionally update pyproject.toml
    if args.sync_pyproject:
        if update_pyproject_version(pyproject_path, target_version):
            print(f"✓ Updated pyproject.toml to version {target_version}")
        else:
            print("✗ Failed to update pyproject.toml")

    print("\nDone! Don't forget to commit the changes.")


if __name__ == "__main__":
    main()
