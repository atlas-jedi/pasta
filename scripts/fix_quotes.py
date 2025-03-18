#!/usr/bin/env python3
"""Script to convert double quotes to single quotes in Python files."""

import glob
import re
import sys


def convert_quotes_in_file(file_path):
    """Convert double quotes to single quotes in a file."""
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # First, we'll handle docstrings differently
    # Find all docstrings (triple double quotes) and preserve them
    docstring_pattern = r'""".*?"""'
    docstrings = re.findall(docstring_pattern, content, re.DOTALL)

    # Replace docstrings with placeholders
    for i, docstring in enumerate(docstrings):
        content = content.replace(docstring, f'DOCSTRING_PLACEHOLDER_{i}')

    # Fix regular strings (double quotes to single quotes)
    # This regex finds double-quoted strings that aren't already docstring placeholders
    # We need to handle escaped quotes properly
    content = re.sub(r'"([^"\\]*(\\.[^"\\]*)*)"', r"'\1'", content)

    # Put docstrings back
    for i, docstring in enumerate(docstrings):
        content = content.replace(f'DOCSTRING_PLACEHOLDER_{i}', docstring)

    # Write the fixed content back to the file
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)

    return True


def main():
    """Convert quotes in all specified files."""
    if len(sys.argv) < 2:
        print('Usage: python fix_quotes.py <file_pattern>')
        return 1

    pattern = sys.argv[1]
    files = glob.glob(pattern, recursive=True)

    if not files:
        print(f'No files found matching pattern: {pattern}')
        return 1

    print(f'Converting quotes in {len(files)} files...')

    for file_path in files:
        if not file_path.endswith('.py'):
            continue

        try:
            if convert_quotes_in_file(file_path):
                print(f'✓ Converted quotes in {file_path}')
            else:
                print(f'✗ Failed to convert quotes in {file_path}')
        except Exception as e:
            print(f'✗ Error processing {file_path}: {str(e)}')

    return 0


if __name__ == '__main__':
    sys.exit(main())
