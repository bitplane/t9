"""CLI commands for corpus generation."""

from pathlib import Path

from .scraper import RedditScraper
from .extractor import CommentExtractor
from .processor import CorpusProcessor


def cmd_scrape(args) -> int:
    """Scrape Reddit user data.

    Args:
        args: Parsed command line arguments

    Returns:
        Exit code
    """
    try:
        scraper = RedditScraper(args.output_dir)

        if args.interactive:
            results = scraper.interactive_scrape()
        else:
            results = scraper.scrape_users(args.usernames)

        if not results:
            print("No data was scraped successfully.")
            return 1

        return 0

    except ImportError as e:
        print(f"Error: {e}")
        print("Install corpus dependencies with: pip install t9[corpus]")
        return 1
    except Exception as e:
        print(f"Scraping failed: {e}")
        return 1


def cmd_extract(args) -> int:
    """Extract and clean comments from JSON files.

    Args:
        args: Parsed command line arguments

    Returns:
        Exit code
    """
    try:
        # Find JSON files
        json_files = []
        for path in args.input:
            path = Path(path)
            if path.is_dir():
                json_files.extend(path.glob("*.json"))
            elif path.is_file() and path.suffix == ".json":
                json_files.append(path)
            else:
                print(f"Warning: Skipping non-JSON file: {path}")

        if not json_files:
            print("Error: No JSON files found")
            return 1

        # Extract and clean comments
        extractor = CommentExtractor()
        extractor.process_json_files(json_files, args.output)

        return 0

    except Exception as e:
        print(f"Comment extraction failed: {e}")
        return 1


def cmd_process(args) -> int:
    """Process corpus text to create frequency wordlist.

    Args:
        args: Parsed command line arguments

    Returns:
        Exit code
    """
    try:
        processor = CorpusProcessor()
        result = processor.process_corpus_file(
            corpus_file=args.corpus, wordlist_file=args.wordlist, output_file=args.output
        )

        print(f"\n✓ Success! Generated frequency wordlist: {result}")
        return 0

    except Exception as e:
        print(f"Corpus processing failed: {e}")
        return 1


def cmd_generate(args) -> int:
    """Complete corpus generation pipeline.

    Args:
        args: Parsed command line arguments

    Returns:
        Exit code
    """
    try:
        # Step 1: Scrape Reddit data
        if not args.skip_scrape:
            print("=== Step 1: Scraping Reddit Data ===")
            scraper = RedditScraper(args.work_dir / "json")

            if args.usernames:
                json_files = scraper.scrape_users(args.usernames)
            else:
                json_files = scraper.interactive_scrape()

            if not json_files:
                print("No data was scraped. Cannot continue.")
                return 1
        else:
            # Use existing JSON files
            json_dir = args.work_dir / "json"
            json_files = list(json_dir.glob("*.json"))
            if not json_files:
                print(f"No JSON files found in {json_dir}")
                return 1

        # Step 2: Extract comments
        print("\n=== Step 2: Extracting Comments ===")
        extractor = CommentExtractor()
        comments_file = args.work_dir / "comments.txt"
        extractor.process_json_files(json_files, comments_file)

        # Step 3: Process corpus
        print("\n=== Step 3: Processing Corpus ===")
        processor = CorpusProcessor()
        result = processor.process_corpus_file(
            corpus_file=comments_file, wordlist_file=args.wordlist, output_file=args.output
        )

        print(f"\n✓ Complete! Generated frequency wordlist: {result}")
        return 0

    except ImportError as e:
        print(f"Error: {e}")
        print("Install corpus dependencies with: pip install t9[corpus]")
        return 1
    except Exception as e:
        print(f"Corpus generation failed: {e}")
        return 1


def add_corpus_commands(subparsers) -> None:
    """Add corpus subcommands to argument parser.

    Args:
        subparsers: ArgumentParser subparsers object
    """
    corpus_parser = subparsers.add_parser("corpus", help="Corpus generation tools")
    corpus_subparsers = corpus_parser.add_subparsers(dest="corpus_command", help="Corpus commands")

    # Scrape command
    scrape_parser = corpus_subparsers.add_parser("scrape", help="Scrape Reddit user data")
    scrape_parser.add_argument("usernames", nargs="*", help="Reddit usernames to scrape")
    scrape_parser.add_argument(
        "-o",
        "--output-dir",
        type=Path,
        default="corpus-data",
        help="Directory to save JSON files (default: corpus-data)",
    )
    scrape_parser.add_argument(
        "-i", "--interactive", action="store_true", help="Interactive mode - prompt for usernames"
    )
    scrape_parser.set_defaults(func=cmd_scrape)

    # Extract command
    extract_parser = corpus_subparsers.add_parser("extract", help="Extract comments from JSON files")
    extract_parser.add_argument("input", nargs="+", help="JSON files or directories containing JSON files")
    extract_parser.add_argument(
        "-o", "--output", type=Path, required=True, help="Output text file for cleaned comments"
    )
    extract_parser.set_defaults(func=cmd_extract)

    # Process command
    process_parser = corpus_subparsers.add_parser("process", help="Process corpus to create frequency wordlist")
    process_parser.add_argument("corpus", type=Path, help="Input corpus text file")
    process_parser.add_argument(
        "-w", "--wordlist", type=Path, help="Dictionary wordlist file (default: system dictionary)"
    )
    process_parser.add_argument(
        "-o", "--output", type=Path, help="Output wordlist file (default: auto-detect from locale)"
    )
    process_parser.set_defaults(func=cmd_process)

    # Generate command (complete pipeline)
    generate_parser = corpus_subparsers.add_parser("generate", help="Complete corpus generation pipeline")
    generate_parser.add_argument("usernames", nargs="*", help="Reddit usernames to scrape")
    generate_parser.add_argument(
        "-w", "--wordlist", type=Path, help="Dictionary wordlist file (default: system dictionary)"
    )
    generate_parser.add_argument(
        "-o", "--output", type=Path, help="Output wordlist file (default: auto-detect from locale)"
    )
    generate_parser.add_argument(
        "--work-dir",
        type=Path,
        default=Path("corpus-work"),
        help="Working directory for intermediate files (default: corpus-work)",
    )
    generate_parser.add_argument(
        "--skip-scrape", action="store_true", help="Skip scraping, use existing JSON files in work directory"
    )
    generate_parser.set_defaults(func=cmd_generate)
