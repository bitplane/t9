#!/bin/bash
# Step 5: Tokenize by various delimiters and sort

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
INPUT_FILE="$PROJECT_DIR/sentences-split.txt"
OUTPUT_FILE="$PROJECT_DIR/words-sorted.txt"

echo "=== Step 5: Tokenize and Sort Words ==="

# Check if input file exists
if [ ! -f "$INPUT_FILE" ]; then
    echo "Input file not found: $INPUT_FILE"
    echo "Run step 4 first to split sentences"
    exit 1
fi

echo "Tokenizing by spaces, commas, semicolons, slashes, and quotes..."

# Split by multiple delimiters and sort
tr ' ,;/"' '\n' < "$INPUT_FILE" \
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
echo "First 20 words for review:"
head -20 "$OUTPUT_FILE"