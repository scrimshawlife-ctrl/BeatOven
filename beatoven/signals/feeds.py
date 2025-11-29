"""
Feed Ingestion - RSS, Atom, JSON APIs
"""

import feedparser
import requests
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

from beatoven.signals import (
    SignalDocument,
    SignalNormalizer,
    SourceType,
    SourceCategory,
    SourceGroup,
)

logger = logging.getLogger(__name__)


class FeedIngester:
    """
    Ingest RSS/Atom/JSON feeds and normalize to SignalDocuments
    """

    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "BeatOven/1.0 Signal Intake"
        })

    def ingest_rss_feed(
        self,
        url: str,
        category: SourceCategory
    ) -> List[SignalDocument]:
        """Fetch and parse RSS/Atom feed"""
        try:
            logger.info(f"Fetching RSS feed: {url}")
            feed = feedparser.parse(url)

            if feed.bozo:
                logger.warning(f"Feed parse warning for {url}: {feed.bozo_exception}")

            documents = []
            for entry in feed.entries:
                doc = SignalNormalizer.normalize_feed_item(
                    entry,
                    SourceType.RSS_FEED,
                    category
                )
                documents.append(doc)

            logger.info(f"Ingested {len(documents)} items from {url}")
            return documents

        except Exception as e:
            logger.error(f"Failed to ingest RSS feed {url}: {e}")
            return []

    def ingest_json_api(
        self,
        url: str,
        category: SourceCategory,
        item_path: Optional[str] = None
    ) -> List[SignalDocument]:
        """
        Fetch JSON API and extract items.
        item_path: JSONPath to items array (e.g., "data.items")
        """
        try:
            logger.info(f"Fetching JSON API: {url}")
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()

            # Navigate to items if path provided
            if item_path:
                for key in item_path.split("."):
                    data = data.get(key, [])

            items = data if isinstance(data, list) else [data]

            documents = []
            for item in items:
                doc = SignalNormalizer.normalize_feed_item(
                    item,
                    SourceType.JSON_API,
                    category
                )
                documents.append(doc)

            logger.info(f"Ingested {len(documents)} items from JSON API")
            return documents

        except Exception as e:
            logger.error(f"Failed to ingest JSON API {url}: {e}")
            return []

    def ingest_source_group(self, group: SourceGroup) -> List[SignalDocument]:
        """Ingest all sources in a group"""
        if not group.enabled:
            logger.info(f"Skipping disabled group: {group.name}")
            return []

        all_docs = []
        for source_url in group.sources:
            # Detect source type from URL or use group category
            if source_url.endswith('.json') or '/api/' in source_url:
                docs = self.ingest_json_api(source_url, group.category)
            else:
                docs = self.ingest_rss_feed(source_url, group.category)

            all_docs.extend(docs)

        logger.info(f"Group '{group.name}': ingested {len(all_docs)} total documents")
        return all_docs


# Predefined source group templates
PREDEFINED_GROUPS = [
    SourceGroup(
        id="world_news",
        name="World News",
        category=SourceCategory.WORLD_NEWS,
        sources=[
            "https://feeds.bbci.co.uk/news/world/rss.xml",
            "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
        ],
        poll_interval_minutes=30,
    ),
    SourceGroup(
        id="us_news",
        name="US News",
        category=SourceCategory.US_NEWS,
        sources=[
            "https://rss.nytimes.com/services/xml/rss/nyt/US.xml",
            "https://feeds.npr.org/1001/rss.xml",
        ],
        poll_interval_minutes=30,
    ),
    SourceGroup(
        id="technology",
        name="Technology",
        category=SourceCategory.TECHNOLOGY,
        sources=[
            "https://feeds.arstechnica.com/arstechnica/index",
            "https://www.theverge.com/rss/index.xml",
        ],
        poll_interval_minutes=60,
    ),
    SourceGroup(
        id="ai_ml",
        name="AI & Machine Learning",
        category=SourceCategory.AI_ML,
        sources=[
            "https://blog.openai.com/rss/",
            "https://deepmind.google/blog/rss.xml",
        ],
        poll_interval_minutes=120,
    ),
    SourceGroup(
        id="crypto",
        name="Crypto Markets",
        category=SourceCategory.CRYPTO_MARKETS,
        sources=[
            "https://cointelegraph.com/rss",
            "https://decrypt.co/feed",
        ],
        poll_interval_minutes=30,
    ),
    SourceGroup(
        id="nba",
        name="NBA",
        category=SourceCategory.NBA,
        sources=[
            "https://www.espn.com/espn/rss/nba/news",
        ],
        poll_interval_minutes=60,
    ),
    SourceGroup(
        id="music",
        name="Music Industry",
        category=SourceCategory.MUSIC_INDUSTRY,
        sources=[
            "https://pitchfork.com/rss/news/",
            "https://www.billboard.com/feed/",
        ],
        poll_interval_minutes=120,
    ),
]


def get_predefined_groups() -> List[SourceGroup]:
    """Get all predefined source groups"""
    return PREDEFINED_GROUPS.copy()


def get_group_by_category(category: SourceCategory) -> Optional[SourceGroup]:
    """Find predefined group by category"""
    for group in PREDEFINED_GROUPS:
        if group.category == category:
            return group
    return None


__all__ = [
    "FeedIngester",
    "PREDEFINED_GROUPS",
    "get_predefined_groups",
    "get_group_by_category",
]
