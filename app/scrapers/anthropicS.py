from datetime import datetime, timedelta, timezone
from typing import Optional
from pydantic import BaseModel
import feedparser
from docling.document_converter import DocumentConverter

class AnthropicArticle(BaseModel):
    title: str
    description: str
    url: str
    published_at: datetime
    category: Optional[str] = None  



class AnthropicScraper:
    def __init__(self):
        self.feeds = {
            "https://raw.githubusercontent.com/Olshansk/rss-feeds/main/feeds/feed_anthropic_news.xml",
            "https://raw.githubusercontent.com/Olshansk/rss-feeds/main/feeds/feed_anthropic_research.xml",
            "https://raw.githubusercontent.com/Olshansk/rss-feeds/main/feeds/feed_anthropic_engineering.xml",
        }
        self.converter = DocumentConverter()
    def get_articles(self, hours: int = 24) -> list[AnthropicArticle]:
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
        articles: list[AnthropicArticle] = []

        for feed_url in self.feeds:
            feed = feedparser.parse(feed_url)

            if not feed.entries:
                continue

            for entry in feed.entries:
                published_parsed = entry.get("published_parsed")
                if not published_parsed:
                    continue

                published_time = datetime(
                    *published_parsed[:6],
                    tzinfo=timezone.utc,
                )

                if published_time < cutoff_time:
                    continue

                articles.append(
                    AnthropicArticle(
                        title=entry.get("title", ""),
                        description=entry.get("description", ""),
                        url=entry.get("link", ""),
                        published_at=published_time,
                        category=entry.get("tags", [{}])[0].get("term") if entry.get("tags") else None
                    )
                )

        return articles
    
    def url_to_markdown(self, url: str) -> Optional[str]:
        try:
            result = self.converter.convert(url)
            return result.document.export_to_markdown()
        except Exception:
            return None
        
if __name__ == "__main__":
    scraper = AnthropicScraper()
    articles: list[AnthropicArticle] = scraper.get_articles(hours=24*6)
    print("-" * 50)
    for a in articles:

        print(a.title)
        print(a.url)
        print(a.published_at)
        print("-" * 50)

    markdown: str = scraper.url_to_markdown(articles[1].url)
    print(markdown)