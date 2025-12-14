from datetime import datetime, timedelta, timezone
from typing import Optional
import feedparser
from pydantic import BaseModel
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound

class Transcript(BaseModel):
    text: str 

class ChannelVideo(BaseModel):
    video_id: str
    channel_id: str
    title: str
    url: str
    description: str
    published_at: datetime
    transcript : Optional[str] = None



class YouTubeScraper:
    def __init__(self):
        self.transcript_api = YouTubeTranscriptApi()

    @staticmethod
    def get_rss_url(channel_id: str) -> str:
        return f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"

    @staticmethod
    def extract_video_url(video_id: str) -> str:
        return f"https://www.youtube.com/watch?v={video_id}"

    def get_latest_videos(self,channel_id: str, hours: int = 24,) -> list[dict]:
        rss_url = self.get_rss_url(channel_id)
        feed = feedparser.parse(rss_url)

        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
        videos = []

        for entry in feed.entries:
            published_at = datetime.fromisoformat(
                entry.published.replace("Z", "+00:00")
            )

            if published_at < cutoff:
                continue

            video_id = entry.yt_videoid

            videos.append(
                ChannelVideo(
                    video_id=video_id,
                    channel_id=channel_id,
                    title=entry.title,
                    url=self.extract_video_url(video_id),
                    description=getattr(entry, "description", ""),
                    published_at=published_at,
                )
            )

        return videos


    def get_transcript(self,video_id: str) -> Optional[str]:

        try:
            ytt_api  = YouTubeTranscriptApi()
            transcript = ytt_api.fetch(video_id)
            return " ".join([item.text for item in transcript])
        except (TranscriptsDisabled, NoTranscriptFound):
            return None
        except Exception as e:
            print("Transcript error:", type(e).__name__, e)
            return None


    def scrape_channel(self,channel_id: str, hours: int = 24) -> list[dict]:

        videos = self.get_latest_videos(channel_id, hours)

        for video in videos:
            video.transcript = self.get_transcript(video.video_id)

        return videos

if __name__ == "__main__":
    scraper = YouTubeScraper()
    CHANNEL_ID = "UCUzqsHTec5ZkJU5S4Tmhweg"

    channel_vids:list[ChannelVideo] = scraper.scrape_channel(CHANNEL_ID, hours=144)

    for video in channel_vids:
        print("-" * 50)
        print(video.title)
        print(video.url, "ID =", video.video_id)
        print(video.published_at)
        print(
            video.transcript[:200] + "..."
            if video.transcript
            else "No transcript"
        )
    print("-" * 50)