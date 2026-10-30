#!/usr/bin/env python3
"""
Feed Parser - RSS Feed Parsing and Normalization

Parse RSS/Atom feeds and normalize entries to common schema.

Author: Jeremy Longshore <jeremy@intentsolutions.io>
Version: 2.0.0
License: MIT
"""

import sys
import re
import html
import io
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import List, Dict, Any, Optional
from difflib import SequenceMatcher

try:
    import feedparser
except ImportError:
    print("Error: feedparser library required. Install with: pip install feedparser", file=sys.stderr)
    sys.exit(1)


class FeedParser:
    """Parse RSS/Atom feeds and normalize to common schema."""

    def __init__(self):
        """Initialize feed parser."""
        self.html_tag_pattern = re.compile(r"<[^>]+>")

    def parse_feed(
        self, content: str, source_name: str = "Unknown", source_category: str = "market", source_quality: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Parse RSS/Atom feed content into article list.

        Args:
            content: Raw feed XML content
            source_name: Name of the source
            source_category: Default category for this source
            source_quality: Quality score (1-10)

        Returns:
            List of normalized article dictionaries
        """
        articles = []

        try:
            # Keep fetched/cache content as data, never a URL or filename.
            feed = feedparser.parse(io.BytesIO(content.encode("utf-8")))

            for entry in feed.entries:
                article = self._parse_entry(
                    entry, source_name=source_name, source_category=source_category, source_quality=source_quality
                )
                if article:
                    articles.append(article)

        except Exception:
            pass

        return articles

    def _parse_entry(
        self, entry: Any, source_name: str, source_category: str, source_quality: int
    ) -> Optional[Dict[str, Any]]:
        """
        Parse a single feed entry.

        Args:
            entry: feedparser entry object
            source_name: Name of the source
            source_category: Default category
            source_quality: Quality score

        Returns:
            Normalized article dictionary or None if invalid
        """
        # Extract title
        title = entry.get("title", "")
        if not title:
            return None

        title = self._clean_text(title)

        # Extract URL
        url = entry.get("link", "")
        if not url:
            return None

        # Extract summary
        summary = ""
        if "summary" in entry:
            summary = self._clean_text(entry.summary)
        elif "description" in entry:
            summary = self._clean_text(entry.description)
        elif "content" in entry and entry.content:
            summary = self._clean_text(entry.content[0].get("value", ""))

        # Truncate summary if too long
        if len(summary) > 500:
            summary = summary[:500] + "..."

        # Extract published date
        published = self._parse_date(entry)

        # Detect coins mentioned
        coins_mentioned = self._detect_coins(f"{title} {summary}")

        # Detect category from content
        category = self._detect_category(f"{title} {summary}", source_category)

        return {
            "title": title,
            "url": url,
            "source": source_name,
            "source_quality": source_quality,
            "published": published,
            "summary": summary,
            "category": category,
            "coins_mentioned": coins_mentioned,
        }

    def _clean_text(self, text: str) -> str:
        """Remove HTML tags and clean whitespace."""
        if not text:
            return ""

        # Decode HTML entities
        text = html.unescape(text)

        # Remove HTML tags
        text = self.html_tag_pattern.sub("", text)

        # Normalize whitespace
        text = " ".join(text.split())

        return text.strip()

    def _parse_date(self, entry: Any) -> Optional[datetime]:
        """Parse published date from entry."""
        # Try published_parsed first
        if hasattr(entry, "published_parsed") and entry.published_parsed:
            try:
                return datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
            except Exception:
                pass

        # Try updated_parsed
        if hasattr(entry, "updated_parsed") and entry.updated_parsed:
            try:
                return datetime(*entry.updated_parsed[:6], tzinfo=timezone.utc)
            except Exception:
                pass

        # Try parsing string dates
        for field in ["published", "updated", "date"]:
            date_str = entry.get(field)
            if date_str:
                for parse in (datetime.fromisoformat, parsedate_to_datetime):
                    try:
                        date = parse(date_str.replace("Z", "+00:00"))
                        if date.tzinfo is None:
                            date = date.replace(tzinfo=timezone.utc)
                        return date.astimezone(timezone.utc)
                    except (ValueError, TypeError, OverflowError):
                        continue

        return None

    def _detect_coins(self, text: str) -> List[str]:
        """Detect cryptocurrency symbols mentioned in text."""
        text_upper = text.upper()

        # Common coin patterns
        coins = []
        coin_patterns = [
            ("BTC", ["BITCOIN", "BTC"]),
            ("ETH", ["ETHEREUM", "ETH", "ETHER"]),
            ("SOL", ["SOLANA", "SOL"]),
            ("BNB", ["BINANCE", "BNB"]),
            ("XRP", ["RIPPLE", "XRP"]),
            ("ADA", ["CARDANO", "ADA"]),
            ("DOGE", ["DOGECOIN", "DOGE"]),
            ("DOT", ["POLKADOT", "DOT"]),
            ("AVAX", ["AVALANCHE", "AVAX"]),
            ("LINK", ["CHAINLINK", "LINK"]),
            ("MATIC", ["POLYGON", "MATIC"]),
            ("UNI", ["UNISWAP", "UNI"]),
            ("AAVE", ["AAVE"]),
            ("MKR", ["MAKER", "MKR"]),
            ("CRV", ["CURVE", "CRV"]),
            ("LDO", ["LIDO", "LDO"]),
            ("ARB", ["ARBITRUM", "ARB"]),
            ("OP", ["OPTIMISM", " OP "]),
        ]

        for symbol, patterns in coin_patterns:
            for pattern in patterns:
                if re.search(r"\b" + re.escape(pattern.strip()) + r"\b", text_upper):
                    if symbol not in coins:
                        coins.append(symbol)
                    break

        return coins

    def _detect_category(self, text: str, default: str) -> str:
        """Detect news category from content."""
        text_lower = text.lower()

        category_keywords = {
            "defi": ["defi", "yield farming", "liquidity pool", "dex", "lending protocol", "aave", "uniswap", "curve"],
            "nft": ["nft", "opensea", "blur", "collection", "mint", "pfp", "digital art"],
            "regulatory": ["sec", "cftc", "regulation", "congress", "senator", "compliance", "lawsuit", "settlement"],
            "exchange": ["binance", "coinbase", "kraken", "listing", "delist", "exchange", "trading pair"],
            "security": ["hack", "exploit", "vulnerability", "audit", "breach", "stolen", "attack", "rug pull"],
            "layer2": ["arbitrum", "optimism", "polygon", "zksync", "base", "layer 2", "l2", "rollup"],
        }

        for category, keywords in category_keywords.items():
            if any(kw in text_lower for kw in keywords):
                return category

        return default

    def deduplicate(self, articles: List[Dict[str, Any]], threshold: float = 0.8) -> List[Dict[str, Any]]:
        """
        Remove duplicate articles based on title similarity.

        Args:
            articles: List of article dictionaries
            threshold: Similarity threshold (0-1) for considering duplicates

        Returns:
            Deduplicated list of articles
        """
        if not articles:
            return []

        unique = []
        seen_titles = []

        for article in articles:
            title = article.get("title", "").lower()

            # Check similarity against all seen titles
            is_duplicate = False
            for seen in seen_titles:
                similarity = SequenceMatcher(None, title, seen).ratio()
                if similarity >= threshold:
                    is_duplicate = True
                    break

            if not is_duplicate:
                unique.append(article)
                seen_titles.append(title)

        return unique
