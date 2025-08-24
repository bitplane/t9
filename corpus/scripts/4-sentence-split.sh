#!/bin/bash
# Step 4: Split sentences and remove first word from each line

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
INPUT_FILE="$PROJECT_DIR/comments-cleaned.txt"
OUTPUT_FILE="$PROJECT_DIR/sentences-split.txt"

echo "=== Step 4: Split Sentences and Remove First Words ==="

# Check if input file exists
if [ ! -f "$INPUT_FILE" ]; then
    echo "Input file not found: $INPUT_FILE"
    echo "Run step 3 first to clean markdown"
    exit 1
fi

echo "Splitting sentences and removing first words..."

# Split on sentence endings and remove first word from each line
sed 's/[?.!:] /\n/g' "$INPUT_FILE" \
| sed 's/^[^[:space:]]*[[:space:]]*//' \
| grep -v '^[[:space:]]*$' \
> "$OUTPUT_FILE"

# Show stats
line_count=$(wc -l < "$OUTPUT_FILE")
word_count=$(wc -w < "$OUTPUT_FILE")

echo ""
echo "✓ Split into $line_count sentence fragments"
echo "✓ Total words: $word_count"
echo "✓ Output saved to: $OUTPUT_FILE"

echo ""
echo "Sample of sentence fragments:"
head -10 "$OUTPUT_FILE"