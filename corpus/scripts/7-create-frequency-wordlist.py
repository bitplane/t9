#!/usr/bin/env python3
"""
Step 7: Create frequency-ordered wordlist from corpus
"""

import sys
import argparse
from pathlib import Path
from collections import Counter

# Add the t9 package to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from t9.utils import get_system_wordlist, get_locale, read_wordlist


def load_corpus_frequencies(corpus_file):
    """Load corpus and return word frequencies (case-insensitive)."""
    print(f"Loading corpus from: {corpus_file}")

    frequencies = Counter()

    with open(corpus_file, "r", encoding="utf-8") as f:
        for line in f:
            word = line.strip().lower()
            if word:
                frequencies[word] += 1

    print(f"✓ Loaded {len(frequencies)} unique words from corpus")
    return frequencies


def load_dictionary_words(wordlist_file):
    """Load dictionary words into a case-insensitive set."""
    if wordlist_file:
        wordlist_path = Path(wordlist_file)
        if not wordlist_path.exists():
            print(f"Error: Wordlist file not found: {wordlist_file}")
            return None
        print(f"Loading dictionary from: {wordlist_file}")
        words = set(word.lower() for word in read_wordlist(wordlist_path))
    else:
        # Use system dictionary
        system_dict = get_system_wordlist()
        if not system_dict:
            print("Error: No system dictionary found at /usr/share/dict/words")
            return None
        print(f"Loading system dictionary from: {system_dict}")
        words = set(word.lower() for word in read_wordlist(system_dict))

    print(f"✓ Loaded {len(words)} dictionary words")
    return words


def create_frequency_wordlist(corpus_frequencies, dictionary_words, output_file):
    """Create frequency-ordered wordlist."""
    print("Creating frequency-ordered wordlist...")

    # Get corpus words sorted by frequency (most common first)
    corpus_words_by_freq = [word for word, count in corpus_frequencies.most_common()]

    written_words = set()

    with open(output_file, "w", encoding="utf-8") as f:
        # First pass: write corpus words that exist in dictionary (by frequency)
        corpus_found = 0
        for word in corpus_words_by_freq:
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


def main():
    parser = argparse.ArgumentParser(description="Create frequency-ordered wordlist from corpus")
    parser.add_argument("corpus_file", help="Cleaned corpus file (one word per line)")
    parser.add_argument("-w", "--wordlist", help="Dictionary wordlist file (default: system dictionary)")
    parser.add_argument("-o", "--output", help="Output wordlist file (default: auto-detect locale)")

    args = parser.parse_args()

    # Determine output file
    if args.output:
        output_file = args.output
    else:
        # Auto-detect locale for output filename
        language, region = get_locale()
        if language and region:
            output_file = f"{language}-{region}.words"
        elif language:
            output_file = f"{language}.words"
        else:
            output_file = "frequency.words"

        print(f"Auto-detected output filename: {output_file}")

    # Check corpus file exists
    corpus_path = Path(args.corpus_file)
    if not corpus_path.exists():
        print(f"Error: Corpus file not found: {args.corpus_file}")
        return 1

    try:
        # Load corpus frequencies
        corpus_frequencies = load_corpus_frequencies(corpus_path)

        # Load dictionary words
        dictionary_words = load_dictionary_words(args.wordlist)
        if dictionary_words is None:
            return 1

        # Create frequency wordlist
        create_frequency_wordlist(corpus_frequencies, dictionary_words, output_file)

        print(f"\n✓ Frequency-ordered wordlist created: {output_file}")

        # Show top 10 words for verification
        print("\nTop 10 most frequent words:")
        with open(output_file, "r") as f:
            for i, line in enumerate(f):
                if i >= 10:
                    break
                print(f"{i+1:2d}. {line.strip()}")

        return 0

    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
