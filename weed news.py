import feedparser
import hashlib
import pandas as pd
import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta, timezone
from dateutil import parser as date_parser
from typing import List, Dict

# Topics and RSS feed config
DEFAULT_TOPICS = [
    "cannabis legalization USA",
    "marijuana rescheduling Schedule III DEA",
    "SAFER Banking Act cannabis",
    "cannabis ETF MSOS",
    "multi-state operators cannabis",
    "cannabis banking reform Congress",
]

RSS_FEEDS = {
    "cannabis legalization USA": [
        "https://news.google.com/rss/search?q=cannabis+legalization+USA",
        "https://www.marijuanamoment.net/feed/",
        "https://www.cannabisbusinesstimes.com/rss/",
        "https://www.bing.com/news/search?q=cannabis+legalization+USA&format=rss",
    ]
}

GENERAL_RSS_FEEDS = [
    "https://feeds.reuters.com/reuters/topNews",
    "https://feeds.apnews.com/apf-topnews",
    "https://www.npr.org/rss/rss.php?id=1001",
    "https://news.yahoo.com/rss/",
    "https://www.cbsnews.com/latest/rss/us",
]

KEYWORDS = ["marijuana", "weed", "THC", "CBD", "rescheduling", "SAFER Banking"]

class NewsConfig:
    def __init__(self, topics=None, max_articles_per_topic=50):
        self.topics = topics if topics else DEFAULT_TOPICS
        self.max_articles_per_topic = max_articles_per_topic

def extract_article_body(url: str) -> str:
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, "html.parser")

        blocks = []
        for p in soup.select("p"):
            text = p.get_text(" ", strip=True)
            if text and len(text) > 60:
                blocks.append(text)

        body = " ".join(blocks)
        body = re.sub(r"\s+", " ", body).strip()
        return body if body else None
    except Exception:
        return None

def hashish(s: str) -> str:
    return hashlib.sha1(s.encode("utf-8", errors="ignore")).hexdigest()[:12]

def parse_feed(url: str, topic: str, seen: set, max_age: datetime, max_articles: int) -> List[Dict]:
    print(f"🔄 Fetching feed for topic '{topic}': {url}")
    feed = feedparser.parse(url)
    entries = feed.entries[:max_articles] if getattr(feed, "entries", None) else []
    print(f"📰 Found {len(entries)} entries in feed.")

    result = []
    for e in entries:
        title = getattr(e, "title", "") or ""
        link = getattr(e, "link", "") or ""
        source = getattr(getattr(e, "source", None), "title", "") or getattr(e, "publisher", "") or ""
        published = getattr(e, "published", "") or getattr(e, "updated", "") or ""

        try:
            published_dt = date_parser.parse(published)
            if published_dt.tzinfo is None:
                published_dt = published_dt.replace(tzinfo=timezone.utc)
            if published_dt < max_age:
                print(f"⏳ Skipped old article: {title}")
                continue
        except Exception:
            print(f"⚠️ Skipped unparseable date for: {title}")
            continue

        key = hashish(title + "|" + link)
        if key in seen or not title:
            continue
        seen.add(key)

        print(f"✅ Accepted article: {title}")
        result.append({
            "Topic": topic,
            "Title": title,
            "Link": link,
            "Source": source,
            "Published": published,
            "Key": key,
        })
    return result

def collect_news(cfg: NewsConfig) -> pd.DataFrame:
    rows = []
    seen: set = set()
    max_age = datetime.now(timezone.utc) - timedelta(days=60)

    for topic in cfg.topics:
        rss_urls = RSS_FEEDS.get(topic, [f"https://news.google.com/rss/search?q={topic.replace(' ', '+')}"])
        for rss_url in rss_urls:
            rows.extend(parse_feed(rss_url, topic, seen, max_age, cfg.max_articles_per_topic))

    for rss_url in GENERAL_RSS_FEEDS:
        print(f"🌐 Checking general feed: {rss_url}")
        feed = feedparser.parse(rss_url)
        entries = feed.entries[:cfg.max_articles_per_topic] if getattr(feed, "entries", None) else []
        print(f"📰 Found {len(entries)} general entries.")

        for e in entries:
            title = getattr(e, "title", "") or ""
            if not any(k.lower() in title.lower() for k in KEYWORDS):
                continue
            link = getattr(e, "link", "") or ""
            source = getattr(getattr(e, "source", None), "title", "") or getattr(e, "publisher", "") or ""
            published = getattr(e, "published", "") or getattr(e, "updated", "") or ""

            try:
                published_dt = date_parser.parse(published)
                if published_dt.tzinfo is None:
                    published_dt = published_dt.replace(tzinfo=timezone.utc)
                if published_dt < max_age:
                    continue
            except Exception:
                continue

            key = hashish(title + "|" + link)
            if key in seen:
                continue
            seen.add(key)

            rows.append({
                "Topic": "(general)",
                "Title": title,
                "Link": link,
                "Source": source,
                "Published": published,
                "Key": key,
            })

    return pd.DataFrame(rows)

if __name__ == "__main__":
    print("🔎 Collecting news…")
    config = NewsConfig()
    df = collect_news(config)

    if df.empty:
        print("No news items found. Try increasing --max-articles or adjusting topics.")
    else:
        df.to_csv("cannabis_news_results.csv", index=False)
        print(f"✅ Saved {len(df)} articles to cannabis_news_results.csv")