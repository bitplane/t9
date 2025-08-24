#!/bin/bash
# Step 1: Download Reddit corpus data

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
CORPUS_DIR="$PROJECT_DIR/corpus-data"

echo "=== Step 1: Download Reddit Corpus ==="

# Clone the scraper repo if it doesn't exist
if [ ! -d "$PROJECT_DIR/lifecap-scraper-reddit" ]; then
    echo "Cloning lifecap-scraper-reddit..."
    cd "$PROJECT_DIR"
    git clone git@github.com:bitplane/lifecap-scraper-reddit.git
    cd lifecap-scraper-reddit
else
    echo "lifecap-scraper-reddit already exists, updating..."
    cd "$PROJECT_DIR/lifecap-scraper-reddit"
    git pull
fi

# Create corpus data directory
mkdir -p "$CORPUS_DIR"

# Prompt for usernames and download data
echo ""
echo "Enter Reddit usernames to download (press Enter with empty input to finish):"

while true; do
    read -r -p "Username: " username
    if [ -z "$username" ]; then
        break
    fi

    echo "Downloading data for $username..."
    # Run the scraper (assuming it outputs to data/ directory)
    # You'll need to adjust this command based on how the scraper works
    python3 scrape.py "$username" || echo "Failed to download $username, continuing..."

    # Copy the JSON file to our corpus directory
    if [ -f "data/$username.json" ]; then
        cp "data/$username.json" "$CORPUS_DIR/"
        echo "✓ Downloaded $username.json"
    else
        echo "✗ No data file found for $username"
    fi
done

echo ""
echo "Downloaded files:"
ls -la "$CORPUS_DIR"/*.json 2>/dev/null || echo "No JSON files found"

echo ""
echo "Step 1 complete. Corpus data saved to: $CORPUS_DIR"