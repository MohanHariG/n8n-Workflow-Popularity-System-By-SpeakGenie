# collectors/discourse_collector.py
import os, time, random, requests, json
from db import SessionLocal
from api.models import Workflow
from utils import normalize_title

BASE = os.getenv("DISCOURSE_BASE", "https://community.n8n.io")

_session = requests.Session()
_session.headers.update({
    "User-Agent": "n8n-popularity-collector/1.0 (+https://github.com/you)",
    "Accept": "application/json"
})

def _get_with_retries(url, params=None, max_retries=5, timeout=30):
    attempt = 0
    backoff = 1.0
    while attempt < max_retries:
        attempt += 1
        try:
            resp = _session.get(url, params=params, timeout=timeout)
            resp.raise_for_status()
            return resp
        except requests.exceptions.RequestException as e:
            code = None
            if hasattr(e, 'response') and e.response is not None:
                code = e.response.status_code
            print(f"[discourse GET] attempt {attempt} failed for {url}: {repr(e)}")
            # if non-retriable 4xx (except 429), break
            if code and 400 <= code < 500 and code != 429:
                print(f"[discourse] non-retriable HTTP {code} for {url}")
                break
            # backoff: add jitter, longer wait for 429
            sleep = backoff + random.random() * backoff
            if code == 429:
                sleep = max(sleep, 20 + random.random() * 10)
            time.sleep(sleep)
            backoff *= 2
    return None

def get_latest_topics(page=0):
    url = f"{BASE}/latest.json"
    r = _get_with_retries(url, params={"page": page}, max_retries=5, timeout=35)
    if not r:
        raise RuntimeError(f"Failed to fetch latest topics from {BASE} after retries.")
    try:
        return r.json().get("topic_list", {}).get("topics", [])
    except Exception as e:
        print("Error parsing latest.json:", e)
        return []

def get_topic_details(topic_id):
    url = f"{BASE}/t/{topic_id}.json"
    r = _get_with_retries(url, max_retries=5, timeout=40)
    if not r:
        raise RuntimeError(f"Failed to fetch topic {topic_id} from {BASE} after retries.")
    return r.json()

def upsert_topic(topic_json, country="global"):
    session = SessionLocal()
    try:
        title = topic_json.get("title", "unknown")
        normalized = normalize_title(title)
        views = int(topic_json.get("views") or 0)
        posts_count = int(topic_json.get("posts_count") or 0)
        replies = posts_count - 1 if posts_count > 0 else 0
        contributors = len(topic_json.get("posters", []) or [])
        likes = 0
        for p in topic_json.get("post_stream", {}).get("posts", []) or []:
            if "action_counts" in p:
                likes += int(p["action_counts"].get("like", 0) or 0)
            elif "like_count" in p:
                likes += int(p.get("like_count", 0) or 0)
            elif "actions_summary" in p:
                for a in p["actions_summary"]:
                    if a.get("id") == 2:
                        likes += a.get("count", 0) or 0
        slug = topic_json.get("slug")
        tid = topic_json.get("id")
        source_url = f"{BASE}/t/{slug}/{tid}" if slug and tid else topic_json.get("url")
        evidence = {"topic_id": tid, "views": views, "replies": replies, "likes": likes, "contributors": contributors}

        wf = session.query(Workflow).filter_by(platform="Forum", normalized_name=normalized, country=country).first()
        if wf:
            wf.views = max(wf.views or 0, views)
            wf.likes = max(wf.likes or 0, likes)
            wf.replies = max(wf.replies or 0, replies)
            wf.contributors = max(wf.contributors or 0, contributors)
            wf.evidence = evidence
            wf.source_url = source_url
            wf.workflow_name = title
        else:
            wf = Workflow(
                workflow_name=title,
                normalized_name=normalized,
                platform="Forum",
                country=country,
                evidence=evidence,
                views=views,
                likes=likes,
                comments=0,
                replies=replies,
                contributors=contributors,
                source_url=source_url
            )
            session.add(wf)
        session.commit()
        return True
    except Exception as e:
        session.rollback()
        print("Error in upsert_topic:", repr(e))
        raise
    finally:
        session.close()
