# BeatOven Signals Intake System

## Overview

The BeatOven Signals Intake System is a universal multi-source signal ingestion and normalization framework. It processes diverse inputs—RSS feeds, JSON APIs, text files, PDFs, calendar events, task lists, and uploaded audio—into a unified symbolic representation that drives generative output.

## Architecture

```
┌─────────────────────────────────────────┐
│        Signal Sources                    │
│  RSS • Atom • JSON • HTML • Text • PDF  │
│  Calendar • Tasks • Audio • Literature   │
└─────────────────┬───────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│     Signal Normalization Layer           │
│   → SignalDocument (Unified Format)     │
└─────────────────┬───────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│    Symbolic Interpretation              │
│  Resonance • Density • Drift • Tension  │
│  Contrast • Emotional Index (Hσ)        │
└─────────────────┬───────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│      Generative Engines                 │
│  Rhythm • Harmony • Timbre • Motion     │
└─────────────────────────────────────────┘
```

## Source Types

### Feed Ingestion
- **RSS Feeds**: Standard RSS 2.0 format
- **Atom Feeds**: Atom 1.0 format
- **JSON APIs**: Custom JSON endpoints with configurable item paths

### File Uploads
- **Text Files**: `.txt`, `.md` (plain text, markdown)
- **PDF Documents**: Extracted text from PDFs
- **EPUB**: E-book format (future)
- **Audio Files**: Metadata extraction from audio uploads

### Personal Data
- **Calendar**: ICS format, JSON calendar events
- **Tasks**: To-do lists, task management formats
- **Journals**: Personal notes and journal entries
- **Literature**: Uploaded books, poetry, essays

## Source Categories

BeatOven provides 30+ predefined source categories:

### News & Current Events
- World News
- US News
- Technology
- AI/ML
- Financial Markets
- Crypto Markets
- Geopolitics
- Climate/Weather
- LA Local News

### Sports
- Sports (General)
- NBA
- NFL
- MLB
- NHL
- eSports

### Culture & Arts
- Music Industry
- Cinema/TV
- Literature/Poetry
- Internet/Meme Culture
- Global Culture

### Academic & Science
- Academic Research
- Science (General)
- Science (Physics)
- Science (Biology/Neuroscience)
- Mythology/Religion
- Philosophy

### Personal
- Personal Calendar
- Personal Tasks
- Uploaded Literature
- Uploaded Audio
- Journals/Notes

### Custom
- User-defined categories

## SignalDocument Structure

All inputs normalize to this unified structure:

```python
@dataclass
class SignalDocument:
    id: str
    source_type: SourceType
    source_category: SourceCategory
    title: str
    content: str
    timestamp: datetime
    metadata: Dict[str, Any]

    # Symbolic features (computed)
    resonance: float  # 0.0-1.0
    density: float    # 0.0-1.0
    drift: float      # 0.0-1.0
    tension: float    # 0.0-1.0
    contrast: float   # 0.0-1.0
    emotional_index: float  # Hσ from PsyFi
    entropy_deviation: float

    provenance_hash: str
```

## Source Grouping

Sources are organized into groups for batch ingestion:

```python
@dataclass
class SourceGroup:
    id: str
    name: str
    category: SourceCategory
    sources: List[str]  # URLs or file paths
    enabled: bool
    poll_interval_minutes: int
```

Example groups:
- **World News**: BBC, NYT World feeds
- **Technology**: Ars Technica, The Verge
- **AI/ML**: OpenAI Blog, DeepMind Blog
- **NBA**: ESPN NBA feed

## API Endpoints

### Ingest Signal
```http
POST /signals/ingest
Content-Type: application/json

{
  "source_url": "https://example.com/feed.rss",
  "source_category": "TECHNOLOGY"
}
```

Or ingest text directly:
```http
POST /signals/ingest
Content-Type: application/json

{
  "source_text": "Text content here...",
  "source_category": "CUSTOM",
  "title": "My Document"
}
```

### Get Source Groups
```http
GET /signals/groups
```

Returns all predefined source groups.

### Get Categories
```http
GET /signals/categories
```

Returns list of all available source categories.

## Usage Examples

### Python: Ingest RSS Feed

```python
from beatoven.signals.feeds import FeedIngester
from beatoven.signals import SourceCategory

ingester = FeedIngester()
docs = ingester.ingest_rss_feed(
    "https://feeds.bbci.co.uk/news/world/rss.xml",
    SourceCategory.WORLD_NEWS
)

for doc in docs:
    print(f"{doc.title}")
    print(f"  Resonance: {doc.resonance:.2f}")
    print(f"  Density: {doc.density:.2f}")
    print(f"  Tension: {doc.tension:.2f}")
```

### Python: Normalize Text

```python
from beatoven.signals import SignalNormalizer, SourceType, SourceCategory

doc = SignalNormalizer.normalize_text(
    "The markets surged today on positive economic data...",
    SourceType.TEXT_FILE,
    SourceCategory.FINANCIAL_MARKETS,
    "Market Update"
)

print(doc.to_dict())
```

### Python: Ingest Source Group

```python
from beatoven.signals.feeds import FeedIngester, get_predefined_groups

ingester = FeedIngester()
groups = get_predefined_groups()

# Ingest all technology sources
tech_group = next(g for g in groups if g.category.value == "technology")
docs = ingester.ingest_source_group(tech_group)

print(f"Ingested {len(docs)} documents from technology sources")
```

## Mobile UI Integration

The mobile app provides screens for signal management:

- **SignalsScreen**: View signal sources and recent ingestions
- **FeedsConfigScreen**: Configure source groups (future)
- **UploadsScreen**: Upload text/audio files (future)

Navigate to signals:
```typescript
navigation.navigate('Signals');
```

## Symbolic Interpretation

Signals are automatically analyzed for symbolic features:

1. **Resonance**: Derived from sentiment, emotional valence
2. **Density**: Based on information density, complexity
3. **Drift**: Temporal variation, topic shifts
4. **Tension**: Conflict markers, urgency indicators
5. **Contrast**: Dynamic range of content
6. **Emotional Index (Hσ)**: PsyFi emotional vector integration

These symbolic fields directly influence generative parameters.

## Polling & Background Ingestion

Source groups can poll automatically:

```python
# Configure poll interval
group.poll_interval_minutes = 30  # Poll every 30 minutes

# Background scheduler (future feature)
scheduler.add_group(group)
scheduler.start()
```

## Provenance

Every SignalDocument includes a deterministic provenance hash:

```python
doc.compute_provenance()
# Returns: "a3f7c2d9e8b1a4f2"
```

This ensures traceable lineage from source → signal → generation.

## Extension

Create custom source types:

```python
@dataclass
class CustomSource:
    def fetch(self) -> List[SignalDocument]:
        # Implement custom ingestion logic
        pass
```

Register with the intake system for seamless integration.

## Future Features

- PDF text extraction
- EPUB support
- HTML web scraping
- Calendar sync (Google, Apple)
- Task integration (Todoist, Things)
- Audio metadata analysis
- Real-time streaming sources
- Advanced NLP for symbolic extraction
