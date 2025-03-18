@echo off
:: Script to format all Python files in the project
:: First fix whitespace and quotes, then run black

echo === Fixing whitespace in blank lines ===
python scripts\fix_whitespace.py ./**/*.py

echo === Fixing quotes in all Python files ===
python scripts\fix_quotes.py ./**/*.py

echo === Running Black on all files ===
black --skip-string-normalization .

echo Done! 