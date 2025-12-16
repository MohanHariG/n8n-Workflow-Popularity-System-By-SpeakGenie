import time
import random

from collectors.youtube_collector import search_videos, fetch_video_stats, upsert_video
from collectors.discourse_collector import get_latest_topics, get_topic_details, upsert_topic
from collectors.trends_collector import get_trend, upsert_trend

# Queries to track across YouTube / Forum / Trends (you can add/remove)
QUERIES = [
    "n8n gmail", "n8n slack", "n8n google sheets", 
    "n8n whatsapp", "n8n airtable",
    "n8n tutorial", "n8n integration", "n8n automation"
]

# We disable trends because Google returns 429 errors during heavy scraping
RUN_TRENDS = False


# -----------------------------------------------------------
# YOUTUBE COLLECTOR
# -----------------------------------------------------------
def run_youtube():
    print("\n--- Running YouTube Collector ---")
    for geo in ["US", "IN"]:
        for q in QUERIES:
            try:
                print(f"Searching YouTube for '{q}' in {geo}...")
                vids = search_videos(q, region_code=geo, max_results=10)
                if not vids:
                    print(" - No videos found.")
                    continue

                items = fetch_video_stats(vids)
                for it in items:
                    upsert_video(it, country=geo)
                    time.sleep(0.5)
            except Exception as e:
                print("YT error:", q, geo, e)
                time.sleep(1)


# -----------------------------------------------------------
# FORUM COLLECTOR
# -----------------------------------------------------------
def run_forum():
    print("\n--- Running Forum Collector ---")
    try:
        topics = get_latest_topics()
        print(f"Found {len(topics)} topics.")
    except Exception as e:
        print("Forum fetch error (latest):", e)
        return

    for t in topics[:80]:
        tid = t.get("id")
        if not tid:
            continue
        try:
            print(f"Fetching topic {tid}...")
            td = get_topic_details(tid)
            upsert_topic(td, country="global")
            time.sleep(0.8 + random.random())
        except Exception as ex:
            print(f"Forum topic error for ID {tid}:", ex)
            time.sleep(2)
            continue


# -----------------------------------------------------------
# TRENDS COLLECTOR
# -----------------------------------------------------------
def run_trends():
    print("\n--- Running Trends Collector ---")
    for q in QUERIES:
        for geo in ["US", "IN"]:
            try:
                print(f"Fetching Google Trends for '{q}' [{geo}]...")
                tr = get_trend(q, geo=geo)
                if tr:
                    upsert_trend(q, tr, country=geo)
                time.sleep(3 + random.random()*2)
            except Exception as e:
                print("Trends error:", q, geo, e)
                time.sleep(5)


# -----------------------------------------------------------
# MAIN EXECUTION
# -----------------------------------------------------------
if __name__ == "__main__":
    print("Starting collectors...\n")

    run_youtube()
    run_forum()

    if RUN_TRENDS:
        run_trends()
    else:
        print("\nSkipping Trends Collector (RUN_TRENDS = False).")

    print("\nCollectors finished.")
