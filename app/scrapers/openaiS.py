from datetime import datetime,timezone,timedelta
from typing import Optional
from pydantic import BaseModel
import feedparser

class OpenAIArticle(BaseModel):
    title: str
    description: str
    url: str
    published_at: datetime
    category: Optional[str] = None

class OpenAIScraper:
    def __init__(self):
        self.rss_url = "https://openai.com/news/rss.xml"

    def get_articles(self, hours: int = 24) -> list[OpenAIArticle]:
        feed = feedparser.parse(self.rss_url)

        if not feed.entries:
            return []

        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
        articles = []

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
            # print(published_parsed)
            articles.append(
                OpenAIArticle(
                    title=entry.get("title", ""),
                    description=entry.get("description", ""),
                    url=entry.get("link", ""),
                    published_at=published_time,
                    category=(
                        entry.get("tags", [{}])[0].get("term")
                        if entry.get("tags")
                        else None
                    ),
                )
            )

        return articles
    
if __name__ == "__main__":
    scraper = OpenAIScraper()
    articles:list[OpenAIArticle] = scraper.get_articles(hours=100)
    print("-" * 50)
    for a in articles:
        print(a.title)
        print(a.url)
        print(a.published_at)
        print("-" * 50)
