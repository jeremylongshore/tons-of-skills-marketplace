#!/usr/bin/env python3
"""
Crypto News Aggregator - Main CLI Entry Point

Aggregate breaking cryptocurrency news from multiple RSS sources.

Author: Jeremy Longshore <jeremy@intentsolutions.io>
Version: 2.0.0
License: MIT
"""

import argparse
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import List, Dict, Any

# Add scripts directory to path for local imports
SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

from feed_fetcher import FeedFetcher
from feed_parser import FeedParser
from scorer import NewsScorer
from formatters import NewsFormatter


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Aggregate breaking cryptocurrency news from multiple sources",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                                # Default scan (24h, top 20)
  %(prog)s --coin BTC --period 4h         # Bitcoin news, past 4 hours
  %(prog)s --category defi                # DeFi category only
  %(prog)s --format json --output news.json  # Export to JSON
        """,
    )

    # Filtering options
    parser.add_argument("--coin", type=str, help="Filter by single coin symbol (e.g., BTC, ETH)")
    parser.add_argument("--coins", type=str, help="Filter by multiple coins (comma-separated, e.g., BTC,ETH,SOL)")
    parser.add_argument(
        "--category",
        type=str,
        choices=["market", "defi", "nft", "regulatory", "layer1", "layer2", "exchange", "security"],
        help="Filter by news category",
    )
    parser.add_argument(
        "--period",
        type=str,
        choices=["1h", "4h", "24h", "7d"],
        default="24h",
        help="Time window for news (default: 24h)",
    )

    # Output options
    parser.add_argument("--top", type=int, default=20, help="Number of results to return (default: 20)")
    parser.add_argument("--min-score", type=float, default=0, help="Minimum relevance score (default: 0)")
    parser.add_argument(
        "--sort-by",
        type=str,
        choices=["relevance", "recency"],
        default="relevance",
        help="Sort results by (default: relevance)",
    )

    # Format and export
    parser.add_argument(
        "--format",
        "-f",
        type=str,
        choices=["table", "json", "csv"],
        default="table",
        help="Output format (default: table)",
    )
    parser.add_argument("--output", "-o", type=str, help="Output file path (default: stdout)")

    # Debug options
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output")
    parser.add_argument("--version", action="version", version="%(prog)s 2.0.0")

    return parser.parse_args()


def get_time_threshold(period: str) -> datetime:
    """Convert period string to datetime threshold."""
    now = datetime.now(timezone.utc)
    if period == "1h":
        return now - timedelta(hours=1)
    elif period == "4h":
        return now - timedelta(hours=4)
    elif period == "24h":
        return now - timedelta(hours=24)
    elif period == "7d":
        return now - timedelta(days=7)
    else:
        return now - timedelta(hours=24)


def load_sources() -> List[Dict[str, Any]]:
    """Load RSS sources from config."""
    config_path = SCRIPT_DIR.parent / "config" / "sources.yaml"

    import yaml

    # A broken/missing config must not silently replace the configured source set.
    try:
        with config_path.open() as handle:
            config = yaml.safe_load(handle)
    except yaml.YAMLError as error:
        raise ValueError("Invalid sources YAML") from error
    sources = config.get("sources") if isinstance(config, dict) else None
    if not isinstance(sources, list) or not sources:
        raise ValueError("sources.yaml must contain a nonempty sources list")
    names = set()
    for source in sources:
        if not isinstance(source, dict) or not all(
            isinstance(source.get(key), str) and source[key].strip() for key in ("name", "url")
        ):
            raise ValueError("Each feed needs a name and URL")
        if source["name"] in names or not source["url"].startswith("https://"):
            raise ValueError("Feed names must be unique and URLs must use HTTPS")
        if "enabled" in source and not isinstance(source["enabled"], bool):
            raise ValueError("Feed enabled must be boolean")
        names.add(source["name"])
    return sources


def main() -> None:
    """Main entry point."""
    args = parse_args()

    # Parse coin filters
    coins = []
    if args.coin:
        coins = [args.coin.upper()]
    elif args.coins:
        coins = [c.strip().upper() for c in args.coins.split(",")]

    # Get time threshold
    time_threshold = get_time_threshold(args.period)

    # Load sources
    try:
        sources = load_sources()
    except (ImportError, OSError, ValueError) as error:
        print(f"Cannot load feed configuration: {type(error).__name__}", file=sys.stderr)
        raise SystemExit(1) from error

    if args.verbose:
        print(f"Loaded {len(sources)} sources", file=sys.stderr)

    # Initialize components
    fetcher = FeedFetcher(timeout=10, verbose=args.verbose)
    parser = FeedParser()
    scorer = NewsScorer()
    formatter = NewsFormatter()

    # Fetch feeds
    if args.verbose:
        print("Fetching feeds...", file=sys.stderr)

    raw_feeds = fetcher.fetch_all(sources)

    if args.verbose:
        print(f"Fetched {len(raw_feeds)} feeds successfully", file=sys.stderr)

    # Parse feeds into articles
    all_articles = []
    for source_name, feed_content in raw_feeds.items():
        source_info = next((s for s in sources if s["name"] == source_name), {})
        articles = parser.parse_feed(
            feed_content,
            source_name=source_name,
            source_category=source_info.get("category", "market"),
            source_quality=source_info.get("quality", 5),
        )
        all_articles.extend(articles)
        health = next(row for row in fetcher.diagnostics if row["source"] == source_name)
        health["articles_parsed"] = len(articles)
        dates = [article["published"] for article in articles if article.get("published")]
        health["latest_published"] = max(dates).isoformat() if dates else None
        health["undated_articles"] = len(articles) - len(dates)
        health["articles_in_window"] = sum(time_threshold <= date <= datetime.now(timezone.utc) for date in dates)

    if args.verbose:
        print(f"Parsed {len(all_articles)} total articles", file=sys.stderr)

    # Deduplicate
    unique_articles = parser.deduplicate(all_articles)

    if args.verbose:
        print(f"After deduplication: {len(unique_articles)} articles", file=sys.stderr)

    # Score articles
    for article in unique_articles:
        article["relevance_score"] = scorer.calculate_score(
            title=article.get("title", ""),
            summary=article.get("summary", ""),
            source_quality=article.get("source_quality", 5),
            published=article.get("published"),
        )

    # Apply filters
    filtered = []
    for article in unique_articles:
        # Time filter
        pub_date = article.get("published")
        if pub_date is None or pub_date < time_threshold or pub_date > datetime.now(timezone.utc):
            continue

        # Coin filter
        if coins:
            text = f"{article.get('title', '')} {article.get('summary', '')}".upper()
            if not any(
                coin in article.get("coins_mentioned", []) or re.search(r"\b" + re.escape(coin) + r"\b", text)
                for coin in coins
            ):
                continue

        # Category filter
        if args.category and article.get("category") != args.category:
            # Also check for category keywords in content
            category_keywords = {
                "defi": ["defi", "yield", "lending", "dex", "liquidity"],
                "nft": ["nft", "opensea", "blur", "collection", "mint"],
                "regulatory": ["sec", "regulation", "congress", "law", "compliance"],
                "exchange": ["binance", "coinbase", "kraken", "listing", "delist"],
                "security": ["hack", "exploit", "vulnerability", "audit", "breach"],
                "layer1": ["ethereum", "solana", "bitcoin", "cardano", "avalanche"],
                "layer2": ["arbitrum", "optimism", "polygon", "zksync", "base"],
            }
            keywords = category_keywords.get(args.category, [])
            text = f"{article.get('title', '')} {article.get('summary', '')}".lower()
            if not any(kw in text for kw in keywords):
                continue

        # Score filter
        if article.get("relevance_score", 0) < args.min_score:
            continue

        filtered.append(article)

    if args.verbose:
        print(f"After filtering: {len(filtered)} articles", file=sys.stderr)

    # Sort
    if args.sort_by == "relevance":
        filtered.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
    else:
        filtered.sort(key=lambda x: x.get("published") or datetime.min.replace(tzinfo=timezone.utc), reverse=True)

    for health in fetcher.diagnostics:
        health["articles_matched"] = sum(article["source"] == health["source"] for article in filtered)

    # Limit results
    result_articles = filtered[: args.top]

    # Add ranks
    for i, article in enumerate(result_articles, 1):
        article["rank"] = i

    # Prepare result
    result = {
        "articles": result_articles,
        "meta": {
            "period": args.period,
            "sources_checked": sum(row["status"] != "disabled" for row in fetcher.diagnostics),
            "sources_configured": len(sources),
            "sources_succeeded": len(raw_feeds),
            "sources_failed": sum(row["status"] == "failed" for row in fetcher.diagnostics),
            "sources_disabled": sum(row["status"] == "disabled" for row in fetcher.diagnostics),
            "feed_health": fetcher.diagnostics,
            "total_fetched": len(all_articles),
            "after_dedup": len(unique_articles),
            "after_filter": len(filtered),
            "shown": len(result_articles),
            "filters": {"coins": coins if coins else None, "category": args.category, "min_score": args.min_score},
        },
    }

    for health in fetcher.diagnostics:
        if health["status"] == "failed":
            print(f"Feed failed: {health['source']}: {health['reason']}", file=sys.stderr)
    if not raw_feeds:
        print("No usable feeds fetched; this is a source failure, not an empty news result.", file=sys.stderr)

    # Format output
    output = formatter.format(result, format_type=args.format)

    # Write output
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            f.write(output)
        print(f"Output written to {output_path}", file=sys.stderr)
    else:
        print(output)

    if not raw_feeds:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
