#!/usr/bin/env python3
"""
News Scorer - Relevance Scoring for Crypto News

Calculate relevance scores based on keywords, source quality, and recency.

Author: Jeremy Longshore <jeremy@intentsolutions.io>
Version: 2.0.0
License: MIT
"""

from datetime import datetime, timedelta, timezone
from typing import Optional, List, Dict


class NewsScorer:
    """Calculate relevance scores for crypto news articles."""

    def __init__(self):
        """Initialize news scorer with keyword weights."""
        # High-impact keywords (market-moving)
        self.high_impact_keywords = {
            "hack": 15,
            "exploit": 15,
            "breach": 12,
            "stolen": 12,
            "listing": 10,
            "delist": 12,
            "sec": 12,
            "lawsuit": 10,
            "settlement": 10,
            "partnership": 8,
            "acquisition": 10,
            "merger": 10,
            "etf": 12,
            "approval": 10,
            "rejection": 10,
            "all-time high": 10,
            "ath": 8,
            "crash": 10,
            "surge": 8,
            "plunge": 8,
            "rally": 8,
            "dump": 8,
            "pump": 8,
            "airdrop": 10,
            "fork": 10,
            "upgrade": 8,
            "mainnet": 8,
            "launch": 8,
            "bankruptcy": 12,
            "insolvent": 12,
            "freeze": 10,
            "halting": 10,
        }

        # Medium-impact keywords
        self.medium_impact_keywords = {
            "bitcoin": 5,
            "ethereum": 5,
            "defi": 4,
            "nft": 4,
            "regulation": 6,
            "institutional": 5,
            "whale": 6,
            "binance": 4,
            "coinbase": 4,
            "stablecoin": 5,
            "usdt": 4,
            "usdc": 4,
            "layer 2": 4,
            "rollup": 4,
            "yield": 4,
            "staking": 4,
            "validator": 4,
            "governance": 4,
            "proposal": 4,
            "vote": 4,
        }

        # Negative keywords (reduce score for promotional content)
        self.negative_keywords = {
            "sponsored": -10,
            "partner content": -10,
            "advertisement": -15,
            "promotion": -5,
            "giveaway": -5,
            "free": -3,
            "sign up": -3,
            "discount": -5,
        }

    def calculate_score(
        self, title: str, summary: str = "", source_quality: int = 5, published: Optional[datetime] = None
    ) -> float:
        """
        Calculate relevance score for an article.

        Args:
            title: Article title
            summary: Article summary/description
            source_quality: Source quality rating (1-10)
            published: Publication datetime

        Returns:
            Relevance score (0-100)
        """
        text = f"{title} {summary}".lower()
        score = 0.0

        # Base score from source quality (0-30 points)
        score += source_quality * 3

        # Keyword scoring (0-50 points)
        keyword_score = 0.0

        # High-impact keywords
        for keyword, weight in self.high_impact_keywords.items():
            if keyword in text:
                keyword_score += weight

        # Medium-impact keywords
        for keyword, weight in self.medium_impact_keywords.items():
            if keyword in text:
                keyword_score += weight

        # Negative keywords
        for keyword, weight in self.negative_keywords.items():
            if keyword in text:
                keyword_score += weight  # weight is negative

        # Cap keyword score
        keyword_score = min(50, max(0, keyword_score))
        score += keyword_score

        # Recency bonus (0-20 points)
        if published:
            recency_score = self._calculate_recency_score(published)
            score += recency_score

        # Ensure score is in range
        score = min(100, max(0, score))

        return round(score, 1)

    def _calculate_recency_score(self, published: datetime) -> float:
        """Calculate recency bonus based on publication time."""
        now = datetime.now(timezone.utc)
        if published.tzinfo is None:
            published = published.replace(tzinfo=timezone.utc)
        age = now - published

        if age < timedelta(hours=1):
            return 20  # Very fresh
        elif age < timedelta(hours=4):
            return 15
        elif age < timedelta(hours=12):
            return 10
        elif age < timedelta(hours=24):
            return 5
        elif age < timedelta(days=3):
            return 2
        else:
            return 0

    def explain_score(
        self, title: str, summary: str = "", source_quality: int = 5, published: Optional[datetime] = None
    ) -> Dict[str, any]:
        """
        Generate explanation of score components.

        Args:
            title: Article title
            summary: Article summary
            source_quality: Source quality rating
            published: Publication datetime

        Returns:
            Dictionary with score breakdown
        """
        text = f"{title} {summary}".lower()

        explanation = {
            "base_score": source_quality * 3,
            "source_quality": source_quality,
            "keywords_found": [],
            "negative_keywords_found": [],
            "keyword_score": 0,
            "recency_score": 0,
            "final_score": 0,
        }

        # Find matching keywords
        keyword_score = 0.0

        for keyword, weight in self.high_impact_keywords.items():
            if keyword in text:
                explanation["keywords_found"].append({"keyword": keyword, "weight": weight})
                keyword_score += weight

        for keyword, weight in self.medium_impact_keywords.items():
            if keyword in text:
                explanation["keywords_found"].append({"keyword": keyword, "weight": weight})
                keyword_score += weight

        for keyword, weight in self.negative_keywords.items():
            if keyword in text:
                explanation["negative_keywords_found"].append({"keyword": keyword, "weight": weight})
                keyword_score += weight

        explanation["keyword_score"] = min(50, max(0, keyword_score))

        if published:
            explanation["recency_score"] = self._calculate_recency_score(published)

        explanation["final_score"] = self.calculate_score(title, summary, source_quality, published)

        return explanation


def get_market_moving_keywords() -> List[str]:
    """Return list of market-moving keywords for highlighting."""
    return [
        "hack",
        "exploit",
        "breach",
        "stolen",
        "listing",
        "delist",
        "sec",
        "lawsuit",
        "etf",
        "approval",
        "rejection",
        "all-time high",
        "ath",
        "crash",
        "surge",
        "airdrop",
        "fork",
        "upgrade",
        "mainnet",
        "bankruptcy",
        "insolvent",
        "freeze",
        "halting",
    ]
