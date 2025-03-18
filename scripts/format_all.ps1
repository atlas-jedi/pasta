# Script to format all Python files in the project
# First fix whitespace and quotes, then run black

Write-Host "=== Fixing whitespace in blank lines ===" -ForegroundColor Green
python scripts\fix_whitespace.py ./**/*.py

Write-Host "=== Fixing quotes in all Python files ===" -ForegroundColor Green
python scripts\fix_quotes.py ./**/*.py

Write-Host "=== Running Black on all files ===" -ForegroundColor Green
black --skip-string-normalization .

Write-Host "Done!" -ForegroundColor Green 