"""Text processing and frequency-based wordlist generation."""

import re
from collections import Counter
from pathlib import Path
from typing import List, Optional, Set

from ..utils import read_wordlist, get_system_wordlist, get_locale


class CorpusProcessor:
    """Processes text corpus to create frequency-ordered wordlists."""

    def __init__(self):
        """Initialize corpus processor."""
        # Sentence ending punctuation
        self.sentence_endings = re.compile(r"[?.!:] ")
        # Word delimiters for tokenization
        self.word_delimiters = re.compile(r"[ ,;/\"]+")
        # Trailing punctuation to remove
        self.trailing_punct = re.compile(r"[.,:;!?()\[\]]*$")
        # Lines starting with punctuation or numbers
        self.invalid_start = re.compile(r"^[[:punct:]0-9]")

    def split_sentences(self, text: str) -> str:
        """Split text on sentence endings and remove first word from each line.

        This helps avoid proper noun vs sentence-start capitalization issues.

        Args:
            text: Input text

        Returns:
            Text with sentences split and first words removed
        """
        # Split on sentence endings
        sentences = self.sentence_endings.split(text)

        # Remove first word from each sentence fragment
        processed_sentences = []
        for sentence in sentences:
            words = sentence.strip().split()
            if len(words) > 1:  # Keep sentences with more than just first word
                processed_sentences.append(" ".join(words[1:]))

        return "\n".join(processed_sentences)

    def tokenize_text(self, text: str) -> List[str]:
        """Tokenize text into individual words.

        Args:
            text: Input text

        Returns:
            List of tokenized words
        """
        # First split sentences to handle capitalization
        processed_text = self.split_sentences(text)

        # Split by word delimiters
        words = self.word_delimiters.split(processed_text)

        # Clean and filter words
        cleaned_words = []
        for word in words:
            if not word.strip():
                continue

            # Remove trailing punctuation
            cleaned = self.trailing_punct.sub("", word)
            if not cleaned:
                continue

            # Skip words starting with punctuation or numbers
            if self.invalid_start.match(cleaned):
                continue

            cleaned_words.append(cleaned)

        return cleaned_words

    def count_word_frequencies(self, words: List[str]) -> Counter:
        """Count word frequencies (case-insensitive).

        Args:
            words: List of words

        Returns:
            Counter with word frequencies
        """
        # Convert to lowercase for counting
        lowercase_words = [word.lower() for word in words]
        return Counter(lowercase_words)

    def load_dictionary_words(self, wordlist_file: Optional[Path] = None) -> Set[str]:
        """Load dictionary words (case-insensitive).

        Args:
            wordlist_file: Optional path to wordlist file, uses system dict if None

        Returns:
            Set of dictionary words in lowercase
        """
        if wordlist_file:
            if not wordlist_file.exists():
                raise FileNotFoundError(f"Wordlist file not found: {wordlist_file}")
            print(f"Loading dictionary from: {wordlist_file}")
            words = set(word.lower() for word in read_wordlist(wordlist_file))
        else:
            # Use system dictionary
            system_dict = get_system_wordlist()
            if not system_dict:
                raise FileNotFoundError("No system dictionary found at /usr/share/dict/words")
            print(f"Loading system dictionary from: {system_dict}")
            words = set(word.lower() for word in read_wordlist(system_dict))

        print(f"✓ Loaded {len(words)} dictionary words")
        return words

    def create_frequency_wordlist(
        self, corpus_frequencies: Counter, dictionary_words: Set[str], output_file: Path
    ) -> int:
        """Create frequency-ordered wordlist.

        Args:
            corpus_frequencies: Word frequency counter from corpus
            dictionary_words: Set of valid dictionary words (lowercase)
            output_file: Output file path

        Returns:
            Total number of words written
        """
        print("Creating frequency-ordered wordlist...")

        written_words = set()

        with open(output_file, "w", encoding="utf-8") as f:
            # First pass: write corpus words that exist in dictionary (by frequency)
            corpus_found = 0
            for word, count in corpus_frequencies.most_common():
                if word in dictionary_words:
                    f.write(word + "\n")
                    written_words.add(word)
                    corpus_found += 1

            print(f"✓ Wrote {corpus_found} corpus words found in dictionary")

            # Second pass: write remaining dictionary words not in corpus
            dict_remaining = 0
            for word in sorted(dictionary_words):
                if word not in written_words:
                    f.write(word + "\n")
                    dict_remaining += 1

            print(f"✓ Wrote {dict_remaining} additional dictionary words")

        total_words = corpus_found + dict_remaining
        print(f"✓ Total words in output: {total_words}")

        return total_words

    def process_corpus_file(
        self, corpus_file: Path, wordlist_file: Optional[Path] = None, output_file: Optional[Path] = None
    ) -> Path:
        """Complete corpus processing pipeline.

        Args:
            corpus_file: Input corpus text file
            wordlist_file: Optional dictionary wordlist file
            output_file: Optional output file path

        Returns:
            Path to generated frequency wordlist
        """
        if not corpus_file.exists():
            raise FileNotFoundError(f"Corpus file not found: {corpus_file}")

        # Determine output file
        if not output_file:
            language, region = get_locale()
            if language and region:
                output_file = Path(f"{language}-{region}-frequency.words")
            elif language:
                output_file = Path(f"{language}-frequency.words")
            else:
                output_file = Path("frequency.words")
            print(f"Auto-detected output filename: {output_file}")

        # Load corpus text
        print(f"Loading corpus from: {corpus_file}")
        with open(corpus_file, "r", encoding="utf-8") as f:
            corpus_text = f.read()

        # Tokenize and count frequencies
        print("Tokenizing corpus...")
        words = self.tokenize_text(corpus_text)
        print(f"✓ Extracted {len(words)} total words")

        corpus_frequencies = self.count_word_frequencies(words)
        print(f"✓ Found {len(corpus_frequencies)} unique words")

        # Load dictionary
        dictionary_words = self.load_dictionary_words(wordlist_file)

        # Create frequency wordlist
        self.create_frequency_wordlist(corpus_frequencies, dictionary_words, output_file)

        print(f"\n✓ Frequency-ordered wordlist created: {output_file}")

        # Show top 10 words for verification
        print("\nTop 10 most frequent words:")
        with open(output_file, "r", encoding="utf-8") as f:
            for i, line in enumerate(f):
                if i >= 10:
                    break
                print(f"{i+1:2d}. {line.strip()}")

        return output_file
