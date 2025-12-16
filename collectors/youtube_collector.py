# collectors/youtube_collector.py
import os, requests, json, time
from db import SessionLocal
from api.models import Workflow
from utils import normalize_title

YOUTUBE_KEY = os.getenv("YOUTUBE_API_KEY")
SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
VIDEO_URL = "https://www.googleapis.com/youtube/v3/videos"

def search_videos(query, region_code='US', max_results=25):
    params = {
        "part": "snippet",
        "q": query,
        "type": "video",
        "maxResults": max_results,
        "regionCode": region_code,
        "key": YOUTUBE_KEY
    }
    r = requests.get(SEARCH_URL, params=params, timeout=15)
    r.raise_for_status()
    items = r.json().get("items", [])
    return [it["id"]["videoId"] for it in items if it.get("id", {}).get("videoId")]

def fetch_video_stats(video_ids):
    if not video_ids:
        return []
    params = {
        "part": "statistics,snippet",
        "id": ",".join(video_ids),
        "key": YOUTUBE_KEY
    }
    r = requests.get(VIDEO_URL, params=params, timeout=15)
    r.raise_for_status()
    return r.json().get("items", [])

def upsert_video(item, country='US'):
    session = SessionLocal()
    try:
        vid = item.get("id")
        stats = item.get("statistics", {})
        views = int(stats.get("viewCount", 0))
        likes = int(stats.get("likeCount", 0))
        comments = int(stats.get("commentCount", 0))
        title = item.get("snippet", {}).get("title", "Untitled")
        normalized = normalize_title(title)
        source_url = f"https://youtube.com/watch?v={vid}"

        wf = session.query(Workflow).filter_by(platform='YouTube', normalized_name=normalized, country=country).first()
        evidence = {"video_id": vid, "publishedAt": item.get("snippet", {}).get("publishedAt")}
        if wf:
            wf.views = max(wf.views or 0, views)
            wf.likes = max(wf.likes or 0, likes)
            wf.comments = max(wf.comments or 0, comments)
            wf.evidence = evidence
            wf.source_url = source_url
            wf.workflow_name = title
        else:
            wf = Workflow(
                workflow_name=title,
                normalized_name=normalized,
                platform='YouTube',
                country=country,
                evidence=evidence,
                views=views,
                likes=likes,
                comments=comments,
                source_url=source_url
            )
            session.add(wf)
        session.commit()
        return True
    except Exception as e:
        session.rollback()
        print("Error upserting video:", e)
        raise
    finally:
        session.close()
