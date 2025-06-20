#!/usr/bin/env python3
"""
Release Notes Generator
Generate GitHub Release notes from templates
"""

import sys
from pathlib import Path
import re

def get_version_from_tag(tag_name):
    """Extract version number from tag name"""
    if tag_name.startswith('v'):
        return tag_name[1:]
    return tag_name

def get_latest_changelog_entry(changelog_path):
    """Get latest version update content from CHANGELOG.md"""
    if not changelog_path.exists():
        return "No changelog available."
    
    try:
        with open(changelog_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find first version entry
        pattern = r'## \[([^\]]+)\] - (\d{4}-\d{2}-\d{2})(.*?)(?=## \[|$)'
        match = re.search(pattern, content, re.DOTALL)

        if match:
            version, _, changes = match.groups()
            # Clean and format update content
            changes = changes.strip()
            if changes:
                return f"## What's New in v{version}\n\n{changes}"
        
        return "See CHANGELOG.md for update details."
    except Exception as e:
        print(f"Error reading changelog: {e}")
        return "See CHANGELOG.md for update details."

def generate_release_notes(version, template_path, changelog_path=None, build_time=None, skip_changelog=False):
    """Generate release notes"""

    # Read template
    if not template_path.exists():
        print(f"Template file not found: {template_path}")
        return None

    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            template = f.read()
    except Exception as e:
        print(f"Error reading template: {e}")
        return None

    # Replace version number
    release_notes = template.replace('{{VERSION}}', version)

    # Replace build time (if provided)
    if build_time:
        release_notes = release_notes.replace('{{BUILD_TIME}}', build_time)

    # If changelog exists and not skipped, add update content
    if not skip_changelog and changelog_path and changelog_path.exists():
        changelog_content = get_latest_changelog_entry(changelog_path)
        # Insert update content before changelog section
        changelog_section = "## Changelog"
        if changelog_section in release_notes:
            release_notes = release_notes.replace(
                changelog_section,
                f"{changelog_content}\n\n{changelog_section}"
            )

    return release_notes

def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Usage: python generate_release_notes.py <version> [output_file] [--manual] [--build-time=<time>] [--skip-changelog]")
        print("Example: python generate_release_notes.py v1.5.6")
        print("Example: python generate_release_notes.py v1.5.6 notes.md --manual --build-time=12345")
        print("Example: python generate_release_notes.py v1.5.6 notes.md --skip-changelog")
        sys.exit(1)

    version_tag = sys.argv[1]
    version = get_version_from_tag(version_tag)
    output_file = sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith('--') else None

    # Parse arguments
    is_manual = '--manual' in sys.argv
    skip_changelog = '--skip-changelog' in sys.argv
    build_time = None
    for arg in sys.argv:
        if arg.startswith('--build-time='):
            build_time = arg.split('=', 1)[1]

    # Set paths
    project_root = Path(__file__).parent.parent
    if is_manual:
        template_path = project_root / ".github" / "manual-release-template.md"
    else:
        template_path = project_root / ".github" / "release-template.md"
    changelog_path = project_root / "CHANGELOG.md"
    
    # Generate release notes
    release_notes = generate_release_notes(version, template_path, changelog_path, build_time, skip_changelog)

    if release_notes is None:
        print("Failed to generate release notes")
        sys.exit(1)

    # Output results
    if output_file:
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(release_notes)
            print(f"Release notes saved to: {output_file}")
        except Exception as e:
            print(f"Error saving to file: {e}")
            sys.exit(1)
    else:
        print(release_notes)

if __name__ == "__main__":
    main()
