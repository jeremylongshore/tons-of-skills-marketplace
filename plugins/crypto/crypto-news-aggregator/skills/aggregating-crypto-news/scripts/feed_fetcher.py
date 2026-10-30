#!/usr/bin/env python3
"""Fetch RSS feeds concurrently with a per-source health receipt and UTC cache."""

import hashlib
import io
import json
import math
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin, urlsplit

import feedparser
import requests


class _ExplicitRedirectSession(requests.Session):
    def resolve_redirects(self, *args, **kwargs):
        # Requests otherwise prepares Response.next by consuming a redirect's
        # body, even with allow_redirects=False. Only our bounded loop redirects.
        return iter(())


class FeedFetcher:
    """Fetch enabled sources, retaining failures rather than hiding partial coverage."""

    def __init__(
        self,
        timeout=10,
        max_workers=10,
        cache_ttl=300,
        verbose=False,
        cache_dir=None,
        max_response_bytes=2 * 1024 * 1024,
        max_redirects=3,
    ):
        if type(timeout) not in (int, float) or not math.isfinite(timeout) or timeout <= 0:
            raise ValueError("Feed timeout must be finite and positive")
        if type(max_workers) is not int or not 1 <= max_workers <= 32:
            raise ValueError("Feed workers must be between 1 and 32")
        if type(max_response_bytes) is not int or not 1 <= max_response_bytes <= 8 * 1024 * 1024:
            raise ValueError("Feed response limit must be between 1 byte and 8 MiB")
        if type(max_redirects) is not int or not 0 <= max_redirects <= 5:
            raise ValueError("Feed redirect limit must be between 0 and 5")
        self.timeout = timeout
        self.max_workers = max_workers
        self.cache_ttl = cache_ttl
        self.verbose = verbose
        self.max_response_bytes = max_response_bytes
        self.max_redirects = max_redirects
        self.cache_dir = Path(cache_dir) if cache_dir is not None else Path(__file__).parent.parent / "data" / "cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.diagnostics = []

    def fetch_all(self, sources: List[Dict[str, Any]]) -> Dict[str, str]:
        """Return successful content by name; diagnostics cover every configured source."""
        results = {}
        receipts = {}
        self.diagnostics = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            pending = {}
            for index, source in enumerate(sources):
                if source.get("enabled", True) is False:
                    receipts[index] = {
                        "source": source["name"],
                        "url": source["url"],
                        "status": "disabled",
                        "reason": source.get("disabled_reason", "Disabled in configuration"),
                    }
                else:
                    pending[executor.submit(self._fetch_one, source)] = (index, source)
            for future in as_completed(pending):
                index, source = pending[future]
                try:
                    content, receipt = future.result()
                except Exception as error:
                    content, receipt = None, {"status": "failed", "reason": type(error).__name__}
                receipts[index] = {"source": source["name"], "url": source["url"], **receipt}
                if content is not None:
                    results[source["name"]] = content
        self.diagnostics = [receipts[index] for index in range(len(sources))]
        return results

    @staticmethod
    def _is_feed(content: str) -> bool:
        """A 200 HTML error page is not a successful feed, including when cached."""
        # A bare string can be interpreted as another URL or local filename.
        feed = feedparser.parse(io.BytesIO(content.encode("utf-8")))
        return bool(feed.version and (not feed.bozo or feed.entries))

    def _fetch_one(self, source):
        url = source.get("url", "")
        if not url:
            return None, {"status": "failed", "reason": "Missing feed URL"}
        if not self._safe_transport_url(url):
            return None, {"status": "failed", "reason": "Feed URL requires HTTPS without embedded credentials"}
        cached = self._get_cached(url)
        if cached is not None and self._is_feed(cached):
            return cached, {"status": "ok", "cached": True}
        try:
            content, status = self._read_bounded_feed(url)
            if not self._is_feed(content):
                return None, {
                    "status": "failed",
                    "http_status": status,
                    "reason": "Response is not a recognized RSS/Atom feed",
                }
            self._set_cached(url, content)
            return content, {"status": "ok", "cached": False, "http_status": status}
        except ValueError as error:
            return None, {"status": "failed", "reason": str(error)}
        except requests.exceptions.Timeout:
            return None, {"status": "failed", "reason": "Request timed out"}
        except requests.exceptions.HTTPError as error:
            code = error.response.status_code if error.response is not None else None
            return None, {"status": "failed", "http_status": code, "reason": f"HTTP {code}"}
        except requests.exceptions.RequestException as error:
            return None, {"status": "failed", "reason": type(error).__name__}

    @staticmethod
    def _safe_transport_url(url):
        try:
            parsed = urlsplit(url)
            return (
                isinstance(url, str)
                and not any(ord(c) < 33 or ord(c) == 127 for c in url)
                and parsed.scheme == "https"
                and bool(parsed.hostname)
                and parsed.username is None
                and parsed.password is None
                and parsed.port in (None, 443)
            )
        except (ValueError, TypeError, AttributeError):
            return False

    def _read_bounded_feed(self, url):
        # Configured hosts are operator-trusted; this is not a DNS/egress sandbox.
        deadline = time.monotonic() + self.timeout
        with _ExplicitRedirectSession() as client:
            # Never load .netrc, environment proxies or environment CA overrides.
            client.trust_env = False
            for redirect in range(self.max_redirects + 1):
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    raise requests.Timeout()
                client.cookies.clear()
                with client.get(
                    url,
                    timeout=min(self.timeout, remaining),
                    stream=True,
                    allow_redirects=False,
                    headers={
                        "User-Agent": "CryptoNewsAggregator/2.0 (RSS Feed Reader)",
                        "Accept": "application/rss+xml, application/atom+xml, application/xml, text/xml",
                    },
                ) as response:
                    if response.status_code in {301, 302, 303, 307, 308}:
                        target = urljoin(url, response.headers.get("Location", ""))
                        if not response.headers.get("Location") or not self._safe_transport_url(target):
                            raise ValueError("Feed redirect requires HTTPS without embedded credentials")
                        if redirect == self.max_redirects:
                            raise ValueError("Feed redirect limit exceeded")
                        url = target
                        continue
                    response.raise_for_status()
                    chunks = bytearray()
                    for chunk in response.iter_content(chunk_size=min(64 * 1024, self.max_response_bytes + 1)):
                        if time.monotonic() >= deadline:
                            raise requests.Timeout()
                        if len(chunks) + len(chunk) > self.max_response_bytes:
                            raise ValueError("Feed response exceeds configured byte limit")
                        chunks.extend(chunk)
                    try:
                        content = chunks.decode(response.encoding or "utf-8", errors="replace")
                    except LookupError:
                        raise ValueError("Feed declares an unsupported text encoding") from None
                    if len(content.encode("utf-8")) > self.max_response_bytes:
                        raise ValueError("Decoded feed exceeds configured byte limit")
                    return content, response.status_code
        raise ValueError("Feed redirect limit exceeded")

    def _get_cache_path(self, url: str) -> Path:
        return self.cache_dir / f"{hashlib.md5(url.encode()).hexdigest()}.json"

    def _get_cached(self, url: str) -> Optional[str]:
        try:
            limit = self.max_response_bytes * 6 + 4096
            with self._get_cache_path(url).open("rb") as handle:
                raw = handle.read(limit + 1)
            if len(raw) > limit:
                return None
            cached = json.loads(raw)
            cached_time = datetime.fromisoformat(cached["timestamp"])
            if cached_time.tzinfo is None:
                cached_time = cached_time.replace(tzinfo=timezone.utc)  # Legacy cache timestamps were UTC.
            age = datetime.now(timezone.utc) - cached_time
            if not timedelta(0) <= age <= timedelta(seconds=self.cache_ttl):
                return None
            content = cached.get("content")
            return (
                content
                if isinstance(content, str) and len(content.encode("utf-8")) <= self.max_response_bytes
                else None
            )
        except (OSError, ValueError, KeyError, TypeError):
            return None

    def _set_cached(self, url: str, content: str) -> None:
        try:
            self._get_cache_path(url).write_text(
                json.dumps(
                    {
                        "url": url,
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "content": content,
                    }
                )
            )
        except OSError:
            pass  # A cache-write failure does not invalidate a successful feed response.

    def clear_cache(self) -> int:
        count = 0
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                cache_file.unlink()
                count += 1
            except OSError:
                pass
        return count
