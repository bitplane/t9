#!/bin/bash
# Step 3: Remove markdown formatting from comments

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
INPUT_FILE="$PROJECT_DIR/all-comments.md"
OUTPUT_FILE="$PROJECT_DIR/comments-cleaned.txt"

echo "=== Step 3: Clean Markdown Formatting ==="

# Check if input file exists
if [ ! -f "$INPUT_FILE" ]; then
    echo "Input file not found: $INPUT_FILE"
    echo "Run step 2 first to extract comments"
    exit 1
fi

echo "Cleaning markdown formatting..."

# Remove markdown formatting
grep -v '^>' "$INPUT_FILE" \
| sed 's/^    .*//' \
| sed 's/\[\([^]]*\)\]([^)]*)/\1/g' \
| sed "s/\`[^\`]*\`//g" \
| sed 's/\*\*\([^*]*\)\*\*/\1/g' \
| sed 's/__\([^_]*\)__/\1/g' \
| sed 's/\*\([^*]*\)\*/\1/g' \
| sed 's/_\([^_]*\)_/\1/g' \
| sed 's/~~\([^~]*\)~~/\1/g' \
| sed 's/^#\+[[:space:]]*//' \
| sed 's/^[*+-][[:space:]]*//' \
| sed 's/^[0-9]\+\.[[:space:]]*//' \
| sed 's/---//g' \
| sed 's/|[^|]*|//g' \
| sed 's/\^[^[:space:]]*//' \
| sed 's|/u/[^[:space:]]*||g' \
| sed 's|/r/[^[:space:]]*||g' \
| sed 's/&nbsp;/ /g' \
| grep -v '^[[:space:]]*$' \
> "$OUTPUT_FILE"

# Show stats
line_count=$(wc -l < "$OUTPUT_FILE")
word_count=$(wc -w < "$OUTPUT_FILE")

echo ""
echo "✓ Cleaned $line_count lines"
echo "✓ Total words: $word_count"
echo "✓ Output saved to: $OUTPUT_FILE"

echo ""
echo "Sample of cleaned comments:"
head -5 "$OUTPUT_FILE"