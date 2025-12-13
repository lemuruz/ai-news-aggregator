from typing import List, Optional
from youtube_transcript_api import YouTubeTranscriptApi

def get_transcript(video_id: str) -> str | None:
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
    
if __name__ == "__main__":
    print(get_transcript("6HSSpAAXN6U"))