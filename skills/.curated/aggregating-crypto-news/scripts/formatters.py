#!/usr/bin/env python3
"""
News Formatters - Output Formatting for Crypto News

Format news results for table, JSON, and CSV output.

Author: Jeremy Longshore <jeremy@intentsolutions.io>
Version: 2.0.0
License: MIT
"""

import json
import csv
import io
from datetime import datetime, timedelta, timezone
from typing import Dict, Any


class NewsFormatter:
    """Format crypto news results for various output types."""

    def format(self, result: Dict[str, Any], format_type: str = "table") -> str:
        """
        Format news results.

        Args:
            result: Dictionary with articles and meta
            format_type: Output format (table, json, csv)

        Returns:
            Formatted output string
        """
        if format_type == "json":
            return self._format_json(result)
        elif format_type == "csv":
            return self._format_csv(result)
        else:
            return self._format_table(result)

    def _format_table(self, result: Dict[str, Any]) -> str:
        """Format results as aligned table."""
        lines = []
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        meta = result.get("meta", {})

        # Header
        lines.append("=" * 90)
        lines.append(f"  CRYPTO NEWS AGGREGATOR{' ' * 42}Updated: {timestamp}")
        lines.append("=" * 90)

        articles = result.get("articles", [])
        if articles:
            lines.append("")
            period = meta.get("period", "24h")
            lines.append(f"  TOP CRYPTO NEWS ({period})")
            lines.append("-" * 90)
            lines.append(f"  {'Rank':<6}{'Source':<16}{'Title':<44}{'Age':<10}{'Score':>8}")
            lines.append("-" * 90)

            for article in articles:
                rank = article.get("rank", "-")
                source = article.get("source", "Unknown")[:14]
                title = article.get("title", "")[:42]
                age = self._format_age(article.get("published"))
                score = f"{article.get('relevance_score', 0):.1f}"

                lines.append(f"  {rank:<6}{source:<16}{title:<44}{age:<10}{score:>8}")

            lines.append("-" * 90)

        else:
            lines.append("")
            lines.append("  No articles found matching your criteria.")
            lines.append("")

        # Summary
        lines.append("")
        shown = meta.get("shown", 0)
        sources = meta.get("sources_checked", 0)
        total = meta.get("after_filter", 0)

        lines.append(f"  Summary: {shown} articles shown | Attempted: {sources} sources | Matched: {total}")

        lines.append(
            f"  Feed health: {meta.get('sources_succeeded', 0)} fetched | "
            f"{meta.get('sources_failed', 0)} failed | {meta.get('sources_disabled', 0)} disabled | "
            f"{meta.get('sources_configured', sources)} configured"
        )
        for health in meta.get("feed_health", []):
            if health["status"] != "ok":
                lines.append(f"  {health['source']}: {health['status']} — {health.get('reason', '')}")
            elif health.get("articles_in_window") == 0:
                lines.append(
                    f"  {health['source']}: no dated articles in window; "
                    f"latest={health.get('latest_published') or 'unknown'}"
                )

        # Filters applied
        filters = meta.get("filters", {})
        filter_parts = []
        if filters.get("coins"):
            filter_parts.append(f"coins={','.join(filters['coins'])}")
        if filters.get("category"):
            filter_parts.append(f"category={filters['category']}")
        if filters.get("min_score"):
            filter_parts.append(f"min_score={filters['min_score']}")

        if filter_parts:
            lines.append(f"  Filters: {', '.join(filter_parts)}")

        lines.append("=" * 90)

        return "\n".join(lines)

    def _format_json(self, result: Dict[str, Any]) -> str:
        """Format results as JSON."""
        # Prepare articles for JSON serialization
        output = {"articles": [], "meta": result.get("meta", {})}

        for article in result.get("articles", []):
            serializable = {
                "rank": article.get("rank"),
                "title": article.get("title"),
                "url": article.get("url"),
                "source": article.get("source"),
                "published": None,
                "age": self._format_age(article.get("published")),
                "category": article.get("category"),
                "relevance_score": article.get("relevance_score"),
                "coins_mentioned": article.get("coins_mentioned", []),
                "summary": article.get("summary", "")[:200],
            }

            # Convert datetime to ISO format
            pub = article.get("published")
            if pub:
                serializable["published"] = pub.isoformat()

            output["articles"].append(serializable)

        # Add timestamp
        output["meta"]["generated_at"] = datetime.now(timezone.utc).isoformat()

        return json.dumps(output, indent=2)

    def _format_csv(self, result: Dict[str, Any]) -> str:
        """Format results as CSV."""
        output = io.StringIO()

        fieldnames = [
            "rank",
            "title",
            "url",
            "source",
            "published",
            "age",
            "category",
            "relevance_score",
            "coins_mentioned",
        ]

        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()

        for article in result.get("articles", []):
            pub = article.get("published")
            published_str = pub.isoformat() if pub else ""

            writer.writerow(
                {
                    "rank": article.get("rank", ""),
                    "title": article.get("title", ""),
                    "url": article.get("url", ""),
                    "source": article.get("source", ""),
                    "published": published_str,
                    "age": self._format_age(pub),
                    "category": article.get("category", ""),
                    "relevance_score": article.get("relevance_score", ""),
                    "coins_mentioned": ",".join(article.get("coins_mentioned", [])),
                }
            )

        return output.getvalue()

    def _format_age(self, published: datetime) -> str:
        """Format datetime as human-readable age."""
        if not published:
            return "unknown"

        now = datetime.now(timezone.utc)
        if published.tzinfo is None:
            published = published.replace(tzinfo=timezone.utc)
        age = now - published

        if age < timedelta(minutes=1):
            return "just now"
        elif age < timedelta(hours=1):
            minutes = int(age.total_seconds() / 60)
            return f"{minutes}m ago"
        elif age < timedelta(hours=24):
            hours = int(age.total_seconds() / 3600)
            return f"{hours}h ago"
        elif age < timedelta(days=7):
            days = int(age.total_seconds() / 86400)
            return f"{days}d ago"
        else:
            return published.strftime("%Y-%m-%d")


def format_article_detail(article: Dict[str, Any]) -> str:
    """Format a single article with full details."""
    lines = []

    lines.append(f"Title: {article.get('title', 'Unknown')}")
    lines.append(f"Source: {article.get('source', 'Unknown')}")
    lines.append(f"URL: {article.get('url', '')}")

    pub = article.get("published")
    if pub:
        lines.append(f"Published: {pub.strftime('%Y-%m-%d %H:%M:%S UTC')}")

    lines.append(f"Category: {article.get('category', 'Unknown')}")
    lines.append(f"Score: {article.get('relevance_score', 0):.1f}")

    coins = article.get("coins_mentioned", [])
    if coins:
        lines.append(f"Coins: {', '.join(coins)}")

    summary = article.get("summary", "")
    if summary:
        lines.append("")
        lines.append("Summary:")
        lines.append(summary)

    return "\n".join(lines)
