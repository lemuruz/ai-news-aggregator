from datetime import datetime, timedelta, timezone
from typing import List, Optional
import feedparser
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound


def get_rss_url(channel_id: str) -> str:
    """
    Build YouTube RSS feed URL from channel ID
    """
    return f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"


def extract_vid_url(video_id: str) -> str:
    """
    Convert video ID to full YouTube URL
    """
    return f"https://www.youtube.com/watch?v={video_id}"


# def detect_live(entry) -> bool:
#     if "live" in entry.title.lower():
#         print(1)
#     elif "stream" in entry.title.lower():
#         print(2)
#     elif getattr(entry, "yt_livebroadcastcontent", "") == "live":
#         print(3)
#     return (
#         "live" in entry.title.lower()
#         or "stream" in entry.title.lower()
#         or getattr(entry, "yt_livebroadcastcontent", "") == "live"
#     )
# def classify_video_type(entry) -> str:
#     if detect_live(entry):
#         return "live"
#     return "video"



def get_latest_vids(channel_id: str, hours: int = 24) -> list[dict]:
    """
    Fetch latest videos from a YouTube channel RSS feed
    within the last `hours`
    """
    rss_url = get_rss_url(channel_id)
    feed = feedparser.parse(rss_url)

    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    videos = []

    for entry in feed.entries:
        published = datetime.fromisoformat(
            entry.published.replace("Z", "+00:00")
        )

        if published >= cutoff:
            video_id = entry.yt_videoid

            videos.append({
                "video_id": video_id,
                "title": entry.title,
                "published": published,
                "url": extract_vid_url(video_id),
                # "type": classify_video_type(entry),
            })

    return videos


def get_transcript(video_id: str) -> Optional[str]:
    """
    Fetch transcript text for a YouTube video.
    Returns None if transcript is unavailable.
    """
    try:
        ytt_api  = YouTubeTranscriptApi()
        transcript = ytt_api.fetch(video_id)
        return " ".join([item.text for item in transcript])
    except Exception:
        return None


def scrape_channel(channel_id: str, hours: int = 24) -> list[dict]:
    """
    Scrape a YouTube channel for recent videos
    and attach transcripts
    """
    videos = get_latest_vids(channel_id, hours)

    for video in videos:
        temp = get_transcript(video["video_id"])
        # print(temp)
        video["transcript"] = temp

    return videos

if __name__ == "__main__":
    CHANNEL_ID = "UCUzqsHTec5ZkJU5S4Tmhweg"

    data = scrape_channel(CHANNEL_ID, hours=144)

    for video in data:
        print("-" * 50)
        # print(video["type"])
        print(video["title"])
        print(video["url"],"ID =",video["video_id"])
        print(video["published"])
        print(video["transcript"][:200]+"...." if video["transcript"] else "No transcript")
        # print("-" * 50)
    print("-" * 50)