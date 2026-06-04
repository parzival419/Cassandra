"""
feed_to_csv_collector.py
------------------------
Collects cannabis-related news from RSS feeds, extracts article bodies,
scores sentiment with VADER, and saves results to CSV for downstream analysis.
"""

import feedparser
import hashlib
import os
import pandas as pd
import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta, timezone
from dateutil import parser as date_parser
from typing import List, Dict, Optional
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "data")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "cannabis_news_results.csv")

MAX_AGE_DAYS = 60
MAX_ARTICLES_PER_FEED = 30
BODY_FETCH_TIMEOUT = 10
MIN_PARAGRAPH_LENGTH = 60

KEYWORDS = [
    "marijuana", "cannabis", "weed", "THC", "CBD",
    "rescheduling", "Schedule III", "SAFER Banking",
    "MSO", "dispensary", "legalization"
]

# ---------------------------------------------------------------------------
# RSS Feed Map — one entry per topic, multiple feeds per topic
# ---------------------------------------------------------------------------

RSS_FEED_MAP: Dict[str, List[str]] = {
    "cannabis legalization USA": [
        "https://news.google.com/rss/search?q=cannabis+legalization+USA",
        "https://www.marijuanamoment.net/feed/",
        "https://www.cannabisbusinesstimes.com/rss/",
    ],
    "marijuana rescheduling Schedule III DEA": [
        "https://news.google.com/rss/search?q=marijuana+rescheduling+Schedule+III+DEA",
        "https://news.google.com/rss/search?q=DEA+cannabis+Schedule+III+2024",
    ],
    "SAFER Banking Act cannabis": [
        "https://news.google.com/rss/search?q=SAFER+Banking+Act+cannabis",
        "https://news.google.com/rss/search?q=cannabis+banking+reform+Congress",
    ],
    "cannabis ETF MSOS investment": [
        "https://news.google.com/rss/search?q=cannabis+ETF+MSOS+investment",
        "https://news.google.com/rss/search?q=cannabis+stocks+investor+outlook",
    ],
    "multi-state operators cannabis": [
        "https://news.google.com/rss/search?q=multi-state+operators+cannabis+MSO",
        "https://news.google.com/rss/search?q=cannabis+dispensary+earnings+revenue",
    ],
    "cannabis biomedical pharmaceutical": [
        "https://news.google.com/rss/search?q=cannabis+biomedical+clinical+trial",
        "https://news.google.com/rss/search?q=cannabinoid+pharmaceutical+FDA",
    ],
}

# General feeds scanned for keyword matches
GENERAL_RSS_FEEDS: List[str] = [
    "https://feeds.reuters.com/reuters/topNews",
    "https://feeds.apnews.com/apf-topnews",
    "https://www.npr.org/rss/rss.php?id=1001",
    "https://news.yahoo.com/rss/",
    "https://www.cbsnews.com/latest/rss/us",
]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

analyzer = SentimentIntensityAnalyzer()


def make_hash(s: str) -> str:
    """Short SHA1 fingerprint for deduplication."""
    return hashlib.sha1(s.encode("utf-8", errors="ignore")).hexdigest()[:12]


def score_sentiment(text: str) -> Dict[str, float]:
    """Run VADER on text; returns compound, pos, neu, neg scores."""
    if not text:
        return {"compound": 0.0, "pos": 0.0, "neu": 0.0, "neg": 0.0}
    scores = analyzer.polarity_scores(text)
    return {
        "compound": round(scores["compound"], 4),
        "pos": round(scores["pos"], 4),
        "neu": round(scores["neu"], 4),
        "neg": round(scores["neg"], 4),
    }


def sentiment_label(compound: float) -> str:
    """Convert VADER compound score to human-readable label."""
    if compound >= 0.05:
        return "positive"
    elif compound <= -0.05:
        return "negative"
    return "neutral"


def extract_article_body(url: str, timeout: int = BODY_FETCH_TIMEOUT) -> Optional[str]:
    """
    Fetch and extract the main text body of an article URL.
    Returns None on failure or if content is too thin.
    """
    try:
        headers = {"User-Agent": "Mozilla/5.0 (compatible; MarketIntelBot/2.0)"}
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")

        # Remove noise elements
        for tag in soup(["script", "style", "nav", "footer", "aside", "header"]):
            tag.decompose()

        paragraphs = [
            p.get_text(" ", strip=True)
            for p in soup.select("p")
            if len(p.get_text(strip=True)) > MIN_PARAGRAPH_LENGTH
        ]

        body = " ".join(paragraphs)
        body = re.sub(r"\s+", " ", body).strip()
        return body if len(body) > 200 else None

    except Exception:
        return None


def parse_entry(entry, topic: str, seen: set, max_age: datetime) -> Optional[Dict]:
    """
    Parse a single feedparser entry into a row dict.
    Returns None if the entry should be skipped.
    """
    title = (getattr(entry, "title", "") or "").strip()
    link = (getattr(entry, "link", "") or "").strip()
    published_raw = getattr(entry, "published", "") or getattr(entry, "updated", "") or ""
    source = (
        getattr(getattr(entry, "source", None), "title", "")
        or getattr(entry, "publisher", "")
        or ""
    ).strip()

    if not title or not link:
        return None

    # Date filter
    try:
        published_dt = date_parser.parse(published_raw)
        if published_dt.tzinfo is None:
            published_dt = published_dt.replace(tzinfo=timezone.utc)
        if published_dt < max_age:
            return None
    except Exception:
        return None

    # Deduplication
    key = make_hash(title + "|" + link)
    if key in seen:
        return None
    seen.add(key)

    return {
        "topic": topic,
        "title": title,
        "link": link,
        "source": source,
        "published": published_raw,
        "key": key,
    }


# ---------------------------------------------------------------------------
# Collection
# ---------------------------------------------------------------------------

def collect_topic_feeds(max_age: datetime, seen: set) -> List[Dict]:
    """Pull articles from all topic-specific RSS feeds."""
    rows = []
    for topic, urls in RSS_FEED_MAP.items():
        for url in urls:
            print(f"  → [{topic[:40]}] {url}")
            try:
                feed = feedparser.parse(url)
                entries = (feed.entries or [])[:MAX_ARTICLES_PER_FEED]
                for entry in entries:
                    row = parse_entry(entry, topic, seen, max_age)
                    if row:
                        rows.append(row)
            except Exception as e:
                print(f"    ⚠️  Feed error: {e}")
    return rows


def collect_general_feeds(max_age: datetime, seen: set) -> List[Dict]:
    """Scan general news RSS feeds and keep keyword-matching articles."""
    rows = []
    kw_lower = [k.lower() for k in KEYWORDS]
    for url in GENERAL_RSS_FEEDS:
        print(f"  → [general] {url}")
        try:
            feed = feedparser.parse(url)
            entries = (feed.entries or [])[:MAX_ARTICLES_PER_FEED]
            for entry in entries:
                title = (getattr(entry, "title", "") or "").lower()
                if not any(k in title for k in kw_lower):
                    continue
                row = parse_entry(entry, "(general)", seen, max_age)
                if row:
                    rows.append(row)
        except Exception as e:
            print(f"    ⚠️  Feed error: {e}")
    return rows


def enrich_with_body_and_sentiment(rows: List[Dict]) -> List[Dict]:
    """
    For each row, fetch the article body and compute VADER sentiment.
    Scores title-only sentiment as fallback when body fetch fails.
    """
    total = len(rows)
    for i, row in enumerate(rows, 1):
        print(f"  Enriching {i}/{total}: {row['title'][:60]}...")
        body = extract_article_body(row["link"])
        row["body"] = body or ""

        # Score on body if available, fall back to title
        text_to_score = body if body else row["title"]
        scores = score_sentiment(text_to_score)
        row["sentiment_compound"] = scores["compound"]
        row["sentiment_pos"] = scores["pos"]
        row["sentiment_neu"] = scores["neu"]
        row["sentiment_neg"] = scores["neg"]
        row["sentiment_label"] = sentiment_label(scores["compound"])
        row["body_fetched"] = bool(body)

    return rows


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    max_age = datetime.now(timezone.utc) - timedelta(days=MAX_AGE_DAYS)
    seen: set = set()

    print("\n📡 Collecting topic feeds...")
    rows = collect_topic_feeds(max_age, seen)

    print("\n🌐 Scanning general feeds for keyword matches...")
    rows += collect_general_feeds(max_age, seen)

    if not rows:
        print("\n❌ No articles collected. Check feed URLs or date range.")
        return

    print(f"\n✅ {len(rows)} articles collected. Enriching with body text and sentiment...")
    rows = enrich_with_body_and_sentiment(rows)

    df = pd.DataFrame(rows)

    # Reorder columns for readability
    col_order = [
        "topic", "title", "source", "published",
        "sentiment_label", "sentiment_compound",
        "sentiment_pos", "sentiment_neu", "sentiment_neg",
        "body_fetched", "body", "link", "key"
    ]
    df = df[[c for c in col_order if c in df.columns]]

    df.to_csv(OUTPUT_FILE, index=False)
    print(f"\n💾 Saved {len(df)} articles → {OUTPUT_FILE}")

    # Quick sentiment summary
    label_counts = df["sentiment_label"].value_counts()
    avg_compound = df["sentiment_compound"].mean()
    body_rate = df["body_fetched"].mean() * 100

    print("\n📊 Sentiment Summary:")
    for label, count in label_counts.items():
        print(f"   {label:10s}: {count}")
    print(f"   Avg compound score : {avg_compound:.4f}")
    print(f"   Body fetch success : {body_rate:.1f}%")


if __name__ == "__main__":
    main()
