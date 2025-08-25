"""Reddit corpus data scraper using reddit-export package."""

import json
from pathlib import Path
from typing import List, Optional

try:
    import reddit_export.scrape as reddit_scraper
except ImportError:
    reddit_scraper = None


class RedditScraper:
    """Scraper for downloading Reddit user comment data."""

    def __init__(self, output_dir: Path):
        """Initialize scraper with output directory.

        Args:
            output_dir: Directory to save scraped JSON files
        """
        if reddit_scraper is None:
            raise ImportError("reddit-export package not installed. Install with: pip install reddit-export")

        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def scrape_user(self, username: str) -> Optional[Path]:
        """Scrape comments for a single Reddit user.

        Args:
            username: Reddit username to scrape

        Returns:
            Path to saved JSON file, or None if failed
        """
        print(f"Scraping Reddit user: {username}")

        try:
            # Use reddit-export to scrape user data
            data = reddit_scraper.scrape_user_comments(username)

            if not data:
                print(f"No data found for user: {username}")
                return None

            # Save to JSON file
            output_file = self.output_dir / f"{username}.json"
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            print(f"✓ Saved {len(data)} items to {output_file}")
            return output_file

        except Exception as e:
            print(f"✗ Failed to scrape {username}: {e}")
            return None

    def scrape_users(self, usernames: List[str]) -> List[Path]:
        """Scrape comments for multiple Reddit users.

        Args:
            usernames: List of Reddit usernames to scrape

        Returns:
            List of paths to saved JSON files
        """
        results = []

        for username in usernames:
            result = self.scrape_user(username)
            if result:
                results.append(result)

        print(f"\n✓ Successfully scraped {len(results)}/{len(usernames)} users")
        return results

    def get_scraped_files(self) -> List[Path]:
        """Get list of all scraped JSON files in output directory.

        Returns:
            List of JSON file paths
        """
        return list(self.output_dir.glob("*.json"))

    def interactive_scrape(self) -> List[Path]:
        """Interactive scraping - prompt for usernames.

        Returns:
            List of paths to saved JSON files
        """
        usernames = []

        print("Enter Reddit usernames to scrape (press Enter with empty input to finish):")

        while True:
            username = input("Username: ").strip()
            if not username:
                break
            usernames.append(username)

        if not usernames:
            print("No usernames provided.")
            return []

        return self.scrape_users(usernames)
