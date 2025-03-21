#!/usr/bin/env python3
"""Script to format all Python files in the project."""

from pathlib import Path
import subprocess
import sys


def run_command(command, description):
    """Run a command and print its output."""
    print(f'\n=== Running {description} ===')
    try:
        # Explicitly setting encoding to UTF-8
        result = subprocess.run(
            command, capture_output=True, text=True, encoding='utf-8', errors='replace'
        )
        print(result.stdout)
        if result.stderr:
            print(f'Errors:\n{result.stderr}', file=sys.stderr)
        return result.returncode
    except Exception as e:
        print(f'Error running {description}: {str(e)}', file=sys.stderr)
        return 1


def main():
    """Run all formatters."""
    # Comandos para executar
    commands = [
        (
            ['python', 'scripts/fix_whitespace.py', './**/*.py'],
            'fix_whitespace to remove whitespace from blank lines (W293)',
        ),
        (['isort', '.'], 'isort to sort imports'),
        (
            ['python', 'scripts/fix_quotes.py', './**/*.py'],
            'fix_quotes to convert double quotes to single quotes',
        ),
        (['black', '--skip-string-normalization', '.'], 'black to format code'),
        (['autopep8', '--in-place', '--recursive', '.'], 'autopep8 to fix remaining issues'),
        (
            ['flake8', '--output-file=flake8_report.txt', '.'],
            'flake8 to check for remaining issues',
        ),
    ]

    # Run each command
    exit_code = 0
    for command, description in commands:
        current_code = run_command(command, description)
        if current_code != 0:
            exit_code = current_code

    # If flake8 generated a report, let's read it and display it
    try:
        if Path('flake8_report.txt').exists():
            print('\n=== Flake8 Report ===')
            try:
                with open('flake8_report.txt', 'r', encoding='utf-8', errors='replace') as f:
                    print(f.read())
            except UnicodeError:
                # Fall back to system default encoding if UTF-8 fails
                with open('flake8_report.txt', 'r', errors='replace') as f:
                    print(f.read())
            Path('flake8_report.txt').unlink()  # Remove the temporary file
    except Exception as e:
        print(f'Error reading flake8 report: {str(e)}', file=sys.stderr)

    if exit_code == 0:
        print('\nAll formatting completed successfully!')
    else:
        print('\nSome formatting tasks reported errors. Check the output above.')

    return exit_code


if __name__ == '__main__':
    sys.exit(main())
