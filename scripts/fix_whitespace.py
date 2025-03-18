#!/usr/bin/env python3
"""Script to fix blank lines containing whitespace (W293) in Python files."""

import glob
import sys


def fix_whitespace_in_file(file_path):
    """Fix whitespace in a file by removing spaces/tabs from blank lines."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        # Check if any changes are needed
        changes_made = False
        fixed_lines = []

        for line in lines:
            # If line only contains whitespace, replace with an empty line
            if line.strip() == '':
                if line != '\n':  # Only modify if not already a clean newline
                    changes_made = True
                    fixed_lines.append('\n')
                else:
                    fixed_lines.append(line)
            else:
                fixed_lines.append(line)

        # Only write back if changes were made
        if changes_made:
            with open(file_path, 'w', encoding='utf-8') as file:
                file.writelines(fixed_lines)
            return True

        return False

    except Exception as e:
        print(f'✗ Error processing {file_path}: {str(e)}')
        return False


def main():
    """Fix whitespace in blank lines in all specified files."""
    if len(sys.argv) < 2:
        print('Usage: python fix_whitespace.py <file_pattern>')
        return 1

    pattern = sys.argv[1]
    files = glob.glob(pattern, recursive=True)

    if not files:
        print(f'No files found matching pattern: {pattern}')
        return 1

    print(f'Checking whitespace in {len(files)} files...')

    fixed_count = 0
    for file_path in files:
        if not file_path.endswith('.py'):
            continue

        try:
            if fix_whitespace_in_file(file_path):
                print(f'✓ Fixed whitespace in {file_path}')
                fixed_count += 1
        except Exception as e:
            print(f'✗ Error processing {file_path}: {str(e)}')

    print(f'Fixed whitespace in {fixed_count} files.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
