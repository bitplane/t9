#!/bin/bash
# Step 2: Extract and decode Reddit comments to markdown

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
CORPUS_DIR="$PROJECT_DIR/corpus-data"
OUTPUT_FILE="$PROJECT_DIR/all-comments.md"

echo "=== Step 2: Extract Reddit Comments ==="

# Check if corpus data exists
if [ ! -d "$CORPUS_DIR" ] || [ -z "$(ls -A "$CORPUS_DIR"/*.json 2>/dev/null)" ]; then
    echo "No JSON files found in $CORPUS_DIR"
    echo "Run step 1 first to download corpus data"
    exit 1
fi

# Extract all comment bodies from JSON files
echo "Extracting comment text from JSON files..."
jq -r '.. | select(type == "object" and has("body")) | .body' "$CORPUS_DIR"/*.json > "$PROJECT_DIR/comments-raw.txt"

# Entity decode and clean up
echo "Decoding HTML entities..."
sed 's/&gt;/>/g; s/&lt;/</g; s/&amp;/\&/g; s/&quot;/"/g; s/&#x27;/'\''/g; s/&apos;/'\''/g' "$PROJECT_DIR/comments-raw.txt" > "$OUTPUT_FILE"

# Show stats
comment_count=$(wc -l < "$OUTPUT_FILE")
word_count=$(wc -w < "$OUTPUT_FILE")

echo ""
echo "✓ Extracted $comment_count comments"
echo "✓ Total words: $word_count"
echo "✓ Output saved to: $OUTPUT_FILE"

echo ""
echo "Sample of extracted comments:"
head -5 "$OUTPUT_FILE"