import re
import feedparser
from dataclasses import dataclass
from typing import Optional


@dataclass
class Article:
    title: str
    description: str
    link: str
    source: str
    published: str
    image_url: Optional[str] = None


# India-specific RSS feeds (always relevant)
INDIA_FEEDS = [
    {"name": "BBC India", "url": "http://feeds.bbci.co.uk/news/world/asia/india/rss.xml"},
    {"name": "Times of India", "url": "https://timesofindia.indiatimes.com/rssfeedsdefault.cms"},
    {"name": "NDTV", "url": "https://feeds.feedburner.com/ndtvnews-latest"},
    {"name": "The Hindu", "url": "https://www.thehindu.com/news/?service=rss"},
    {"name": "Economic Times", "url": "https://economictimes.indiatimes.com/rssfeedsdefault.cms"},
]

# Global feeds — filtered for India relevance
GLOBAL_FEEDS = [
    {"name": "Reuters World", "url": "https://feeds.reuters.com/reuters/worldNews"},
    {"name": "Al Jazeera", "url": "https://www.aljazeera.com/xml/rss/all.xml"},
    {"name": "BBC World", "url": "http://feeds.bbci.co.uk/news/world/rss.xml"},
]

INDIA_KEYWORDS = [
    "india", "indian", "modi", "new delhi", "mumbai", "bangalore", "bengaluru",
    "chennai", "kolkata", "hyderabad", "pune", "delhi", "kashmir", "bjp",
    "congress party", "rupee", "rbi", "isro", "tata group", "infosys", "wipro",
    "reliance", "adani", "ambani", "indo-pacific", "south asia", "lok sabha",
    "rajya sabha", "india-china", "india-pakistan", "india-us", "india-russia",
    "hindutva", "gst india", "niti aayog", "make in india",
]


def clean_html(text: str) -> str:
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def is_india_related(title: str, description: str) -> bool:
    text = (title + " " + description).lower()
    return any(kw in text for kw in INDIA_KEYWORDS)


def parse_feed(feed_info: dict, filter_india: bool = False, max_items: int = 12) -> list[Article]:
    articles = []
    try:
        feed = feedparser.parse(feed_info["url"])
        for entry in feed.entries[:max_items]:
            title = clean_html(entry.get("title", "Untitled"))
            description = clean_html(
                entry.get("summary", entry.get("description", ""))
            )[:600]
            link = entry.get("link", "#")
            published = entry.get("published", entry.get("updated", ""))

            image_url = None
            if hasattr(entry, "media_thumbnail") and entry.media_thumbnail:
                image_url = entry.media_thumbnail[0].get("url")
            elif hasattr(entry, "media_content") and entry.media_content:
                image_url = entry.media_content[0].get("url")

            if filter_india and not is_india_related(title, description):
                continue

            articles.append(
                Article(
                    title=title,
                    description=description,
                    link=link,
                    source=feed_info["name"],
                    published=published,
                    image_url=image_url,
                )
            )
    except Exception as e:
        print(f"[news_fetcher] Error fetching {feed_info['name']}: {e}")
    return articles


def fetch_all_news(max_total: int = 30) -> list[Article]:
    all_articles: list[Article] = []

    for feed_info in INDIA_FEEDS:
        all_articles.extend(parse_feed(feed_info, filter_india=False, max_items=8))

    for feed_info in GLOBAL_FEEDS:
        all_articles.extend(parse_feed(feed_info, filter_india=True, max_items=15))

    # Deduplicate by title prefix
    seen: set[str] = set()
    unique: list[Article] = []
    for article in all_articles:
        key = article.title[:60].lower().strip()
        if key not in seen:
            seen.add(key)
            unique.append(article)

    return unique[:max_total]
