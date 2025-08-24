"""Command-line interface for PY9 T9 text input system."""

import argparse
import sys
from pathlib import Path

from . import maket9
from .demo import run_demo as demo_function


def run_demo(dict_file=None):
    """Run the T9 demo application."""
    return demo_function(dict_file)


def generate_dict(wordlist, output, language="Unknown", comment=""):
    """
    Generate a T9 dictionary from a wordlist file.
    """
    if not Path(wordlist).exists():
        print(f"Wordlist file not found: {wordlist}")
        return 1

    print(f"Generating dictionary from {wordlist}...")
    print(f"Output: {output}")
    print(f"Language: {language}")
    print(f"Comment: {comment}")

    try:
        # Call the generation function
        maket9.makedict(wordlist, output, language, comment)
        print(f"Dictionary successfully created: {output}")
        return 0

    except Exception as e:
        print(f"Dictionary generation failed: {e}")
        return 1


def main():
    """
    Main CLI entry point.
    """
    parser = argparse.ArgumentParser(description="PY9 T9 predictive text system", prog="py9")

    parser.add_argument("--version", action="version", version="%(prog)s 0.2.0")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Generate command
    gen_parser = subparsers.add_parser("generate", aliases=["gen"], help="Generate T9 dictionary from wordlist")
    gen_parser.add_argument("wordlist", help="Path to wordlist file (one word per line)")
    gen_parser.add_argument("-o", "--output", required=True, help="Output dictionary file path")
    gen_parser.add_argument("-l", "--language", default="Unknown", help="Language name for dictionary metadata")
    gen_parser.add_argument("-c", "--comment", default="", help="Comment for dictionary metadata")

    # Demo command
    demo_parser = subparsers.add_parser("demo", help="Run T9 demo application")
    demo_parser.add_argument("dictionary", nargs="?", help="Path to dictionary file (optional)")

    args = parser.parse_args()

    # If no command specified, run demo by default
    if args.command is None:
        print("No command specified, running demo...")
        return run_demo()

    if args.command in ("generate", "gen"):
        return generate_dict(args.wordlist, args.output, args.language, args.comment)
    elif args.command == "demo":
        return run_demo(args.dictionary)

    return 0


if __name__ == "__main__":
    sys.exit(main())
