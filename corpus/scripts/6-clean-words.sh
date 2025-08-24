#!/bin/bash
# Step 6: Clean words - remove lines starting with punctuation/numbers and trailing punctuation

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
INPUT_FILE="$PROJECT_DIR/words-sorted.txt"
OUTPUT_FILE="$PROJECT_DIR/words-cleaned.txt"

echo "=== Step 6: Clean Words ==="

# Check if input file exists
if [ ! -f "$INPUT_FILE" ]; then
    echo "Input file not found: $INPUT_FILE"
    echo "Run step 5 first to tokenize and sort"
    exit 1
fi

echo "Removing lines starting with punctuation/numbers and trailing punctuation..."

# Clean words
grep -v '^[[:punct:]]' "$INPUT_FILE" \
| grep -v '^[0-9]' \
| sed 's/[.,:;!?()\[\]]*$//' \
| grep -v '^[[:space:]]*$' \
| sort \
> "$OUTPUT_FILE"

# Show stats
word_count=$(wc -l < "$OUTPUT_FILE")
unique_count=$(sort "$OUTPUT_FILE" | uniq | wc -l)

echo ""
echo "✓ Total words: $word_count"
echo "✓ Unique words: $unique_count"
echo "✓ Output saved to: $OUTPUT_FILE"

echo ""
echo "First 20 cleaned words for review:"
head -20 "$OUTPUT_FILE"