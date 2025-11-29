"""
BeatOven Signals Intake System
Multi-source signal ingestion and normalization
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from datetime import datetime
from enum import Enum
import hashlib


class SourceType(Enum):
    """Signal source types"""
    RSS_FEED = "rss_feed"
    ATOM_FEED = "atom_feed"
    JSON_API = "json_api"
    HTML_SCRAPE = "html_scrape"
    TEXT_FILE = "text_file"
    PDF_FILE = "pdf_file"
    EPUB_FILE = "epub_file"
    AUDIO_FILE = "audio_file"
    CALENDAR = "calendar"
    TASKS = "tasks"
    JOURNAL = "journal"
    LITERATURE = "literature"
    PROMPT = "user_prompt"


class SourceCategory(Enum):
    """Predefined source groupings"""
    WORLD_NEWS = "world_news"
    US_NEWS = "us_news"
    TECHNOLOGY = "technology"
    AI_ML = "ai_ml"
    FINANCIAL_MARKETS = "financial_markets"
    CRYPTO_MARKETS = "crypto_markets"
    SPORTS_GENERAL = "sports_general"
    NBA = "nba"
    NFL = "nfl"
    MLB = "mlb"
    NHL = "nhl"
    ESPORTS = "esports"
    MUSIC_INDUSTRY = "music_industry"
    CINEMA_TV = "cinema_tv"
    LITERATURE_POETRY = "literature_poetry"
    MYTHOLOGY_RELIGION = "mythology_religion"
    PHILOSOPHY = "philosophy"
    ACADEMIC_RESEARCH = "academic_research"
    SCIENCE_GENERAL = "science_general"
    SCIENCE_PHYSICS = "science_physics"
    SCIENCE_BIO_NEURO = "science_bio_neuro"
    CLIMATE_WEATHER = "climate_weather"
    LA_LOCAL = "la_local"
    GLOBAL_CULTURE = "global_culture"
    INTERNET_MEME_CULTURE = "internet_meme_culture"
    HEALTH_BIOSECURITY = "health_biosecurity"
    GEOPOLITICS = "geopolitics"
    PERSONAL_CALENDAR = "personal_calendar"
    PERSONAL_TASKS = "personal_tasks"
    UPLOADED_LITERATURE = "uploaded_literature"
    UPLOADED_AUDIO = "uploaded_audio"
    JOURNALS_NOTES = "journals_notes"
    CUSTOM = "custom"


@dataclass
class SignalDocument:
    """
    Unified representation of all ingested signals.
    Everything normalizes to this structure.
    """
    id: str
    source_type: SourceType
    source_category: SourceCategory
    title: str
    content: str
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Symbolic features (computed)
    resonance: float = 0.0
    density: float = 0.0
    drift: float = 0.0
    tension: float = 0.0
    contrast: float = 0.0
    emotional_index: float = 0.0  # Hσ from PsyFi
    entropy_deviation: float = 0.0

    # Provenance
    provenance_hash: str = ""

    def compute_provenance(self) -> str:
        """Generate deterministic provenance hash"""
        content_str = f"{self.id}:{self.source_type.value}:{self.title}:{self.content[:1000]}"
        hash_bytes = hashlib.sha256(content_str.encode()).digest()
        self.provenance_hash = hash_bytes.hex()[:16]
        return self.provenance_hash

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary"""
        return {
            "id": self.id,
            "source_type": self.source_type.value,
            "source_category": self.source_category.value,
            "title": self.title,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
            "symbolic_fields": {
                "resonance": self.resonance,
                "density": self.density,
                "drift": self.drift,
                "tension": self.tension,
                "contrast": self.contrast,
                "emotional_index": self.emotional_index,
                "entropy_deviation": self.entropy_deviation,
            },
            "provenance_hash": self.provenance_hash,
        }


@dataclass
class SourceGroup:
    """Group of related signal sources"""
    id: str
    name: str
    category: SourceCategory
    sources: List[str] = field(default_factory=list)  # URLs or file paths
    enabled: bool = True
    poll_interval_minutes: int = 60

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category.value,
            "sources": self.sources,
            "enabled": self.enabled,
            "poll_interval_minutes": self.poll_interval_minutes,
        }


class SignalNormalizer:
    """
    Normalize all input types to SignalDocument.
    Each source type has a specific normalization method.
    """

    @staticmethod
    def normalize_text(
        text: str,
        source_type: SourceType,
        category: SourceCategory,
        title: str = "Untitled",
        metadata: Optional[Dict[str, Any]] = None
    ) -> SignalDocument:
        """Normalize plain text"""
        doc_id = hashlib.md5(f"{title}:{text[:100]}".encode()).hexdigest()[:12]

        doc = SignalDocument(
            id=doc_id,
            source_type=source_type,
            source_category=category,
            title=title,
            content=text,
            timestamp=datetime.now(),
            metadata=metadata or {},
        )
        doc.compute_provenance()
        return doc

    @staticmethod
    def normalize_feed_item(
        item: Dict[str, Any],
        source_type: SourceType,
        category: SourceCategory
    ) -> SignalDocument:
        """Normalize RSS/Atom/JSON feed item"""
        title = item.get("title", "Untitled")
        content = item.get("description") or item.get("summary") or item.get("content", "")
        link = item.get("link", "")
        published = item.get("published") or item.get("pubDate") or datetime.now()

        if isinstance(published, str):
            # Try to parse datetime string
            try:
                from dateutil import parser
                published = parser.parse(published)
            except:
                published = datetime.now()

        doc_id = hashlib.md5(f"{title}:{link}".encode()).hexdigest()[:12]

        doc = SignalDocument(
            id=doc_id,
            source_type=source_type,
            source_category=category,
            title=title,
            content=content,
            timestamp=published,
            metadata={"link": link, "raw_item": item},
        )
        doc.compute_provenance()
        return doc

    @staticmethod
    def normalize_calendar_event(
        event: Dict[str, Any],
        category: SourceCategory = SourceCategory.PERSONAL_CALENDAR
    ) -> SignalDocument:
        """Normalize calendar event (ICS or JSON)"""
        title = event.get("summary") or event.get("title", "Event")
        description = event.get("description", "")
        location = event.get("location", "")
        start_time = event.get("dtstart") or event.get("start", datetime.now())

        if isinstance(start_time, str):
            try:
                from dateutil import parser
                start_time = parser.parse(start_time)
            except:
                start_time = datetime.now()

        content = f"{description}\nLocation: {location}" if location else description
        doc_id = hashlib.md5(f"cal:{title}:{start_time}".encode()).hexdigest()[:12]

        doc = SignalDocument(
            id=doc_id,
            source_type=SourceType.CALENDAR,
            source_category=category,
            title=title,
            content=content,
            timestamp=start_time,
            metadata=event,
        )
        doc.compute_provenance()
        return doc

    @staticmethod
    def normalize_task(
        task: Dict[str, Any],
        category: SourceCategory = SourceCategory.PERSONAL_TASKS
    ) -> SignalDocument:
        """Normalize task/to-do item"""
        title = task.get("title") or task.get("summary", "Task")
        description = task.get("description", "")
        due_date = task.get("due") or task.get("dueDate", datetime.now())
        priority = task.get("priority", "normal")

        if isinstance(due_date, str):
            try:
                from dateutil import parser
                due_date = parser.parse(due_date)
            except:
                due_date = datetime.now()

        content = f"{description}\nPriority: {priority}"
        doc_id = hashlib.md5(f"task:{title}:{due_date}".encode()).hexdigest()[:12]

        doc = SignalDocument(
            id=doc_id,
            source_type=SourceType.TASKS,
            source_category=category,
            title=title,
            content=content,
            timestamp=due_date,
            metadata=task,
        )
        doc.compute_provenance()
        return doc


__all__ = [
    "SourceType",
    "SourceCategory",
    "SignalDocument",
    "SourceGroup",
    "SignalNormalizer",
]
