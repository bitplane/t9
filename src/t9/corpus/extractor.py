"""Comment extraction and cleaning from Reddit JSON data."""

import html
import json
import re
from pathlib import Path
from typing import Iterator, List


class CommentExtractor:
    """Extracts and cleans Reddit comments from JSON files."""

    def __init__(self):
        """Initialize comment extractor."""
        # Regex patterns for markdown cleaning
        self.markdown_patterns = [
            # Remove code blocks (4+ spaces)
            (re.compile(r"^    .*$", re.MULTILINE), ""),
            # Remove inline code
            (re.compile(r"`[^`]*`"), ""),
            # Remove links but keep text: [text](url) -> text
            (re.compile(r"\[([^\]]*)\]\([^)]*\)"), r"\1"),
            # Remove bold/italic formatting
            (re.compile(r"\*\*([^*]*)\*\*"), r"\1"),
            (re.compile(r"__([^_]*)__"), r"\1"),
            (re.compile(r"\*([^*]*)\*"), r"\1"),
            (re.compile(r"_([^_]*)_"), r"\1"),
            # Remove strikethrough
            (re.compile(r"~~([^~]*)~~"), r"\1"),
            # Remove headers
            (re.compile(r"^#+\s*", re.MULTILINE), ""),
            # Remove bullet points
            (re.compile(r"^[*+-]\s*", re.MULTILINE), ""),
            # Remove numbered lists
            (re.compile(r"^\d+\.\s*", re.MULTILINE), ""),
            # Remove horizontal rules
            (re.compile(r"---+"), ""),
            # Remove table formatting
            (re.compile(r"\|[^|]*\|"), ""),
            # Remove superscript
            (re.compile(r"\^[^\s]*"), ""),
            # Remove Reddit user/subreddit references
            (re.compile(r"/u/[^\s]*"), ""),
            (re.compile(r"/r/[^\s]*"), ""),
        ]

    def extract_comments_from_file(self, json_file: Path) -> Iterator[str]:
        """Extract comment text from a single JSON file.

        Args:
            json_file: Path to JSON file containing Reddit data

        Yields:
            Raw comment text strings
        """
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Handle nested JSON structure - look for objects with 'body' field
            for comment_text in self._extract_bodies_recursive(data):
                yield comment_text

        except Exception as e:
            print(f"Warning: Failed to process {json_file}: {e}")

    def _extract_bodies_recursive(self, obj) -> Iterator[str]:
        """Recursively extract 'body' fields from nested JSON structure.

        Args:
            obj: JSON object to search

        Yields:
            Comment body text strings
        """
        if isinstance(obj, dict):
            if "body" in obj and isinstance(obj["body"], str):
                yield obj["body"]

            for value in obj.values():
                yield from self._extract_bodies_recursive(value)

        elif isinstance(obj, list):
            for item in obj:
                yield from self._extract_bodies_recursive(item)

    def extract_comments_from_files(self, json_files: List[Path]) -> Iterator[str]:
        """Extract comment text from multiple JSON files.

        Args:
            json_files: List of JSON file paths

        Yields:
            Raw comment text strings
        """
        for json_file in json_files:
            yield from self.extract_comments_from_file(json_file)

    def clean_comment(self, comment: str) -> str:
        """Clean a single comment by removing quotes, decoding entities, and cleaning markdown.

        Args:
            comment: Raw comment text

        Returns:
            Cleaned comment text
        """
        # Skip quoted text (lines starting with >)
        if comment.strip().startswith(">"):
            return ""

        # Decode HTML entities
        comment = html.unescape(comment)

        # Remove markdown formatting
        for pattern, replacement in self.markdown_patterns:
            comment = pattern.sub(replacement, comment)

        # Remove extra whitespace and empty lines
        lines = [line.strip() for line in comment.split("\n")]
        lines = [line for line in lines if line]

        return " ".join(lines)

    def extract_and_clean_comments(self, json_files: List[Path]) -> List[str]:
        """Extract and clean all comments from JSON files.

        Args:
            json_files: List of JSON file paths

        Returns:
            List of cleaned comment strings
        """
        cleaned_comments = []

        print(f"Extracting comments from {len(json_files)} files...")

        for comment in self.extract_comments_from_files(json_files):
            cleaned = self.clean_comment(comment)
            if cleaned:  # Only keep non-empty comments
                cleaned_comments.append(cleaned)

        print(f"✓ Extracted {len(cleaned_comments)} cleaned comments")
        return cleaned_comments

    def save_comments(self, comments: List[str], output_file: Path) -> None:
        """Save cleaned comments to a text file.

        Args:
            comments: List of cleaned comment strings
            output_file: Path to output file
        """
        with open(output_file, "w", encoding="utf-8") as f:
            for comment in comments:
                f.write(comment + "\n")

        print(f"✓ Saved {len(comments)} comments to {output_file}")

    def process_json_files(self, json_files: List[Path], output_file: Path) -> Path:
        """Complete processing pipeline: extract, clean, and save comments.

        Args:
            json_files: List of input JSON files
            output_file: Path to output text file

        Returns:
            Path to saved output file
        """
        comments = self.extract_and_clean_comments(json_files)
        self.save_comments(comments, output_file)
        return output_file
