# test_fetch.py — full verbose test for forum + DB connectivity
import os, json, time
from dotenv import load_dotenv
load_dotenv()

import requests
from db import SessionLocal, engine
from api.models import Workflow
from sqlalchemy import text

BASE = os.getenv("DISCOURSE_BASE", "https://community.n8n.io")

def test_forum():
    print("1) Testing forum latest.json fetch...")
    try:
        r = requests.get(f"{BASE}/latest.json", timeout=25)
        r.raise_for_status()
        data = r.json()
        topics = data.get("topic_list", {}).get("topics", [])
        print(" - latest.json fetched. topics found:", len(topics))
        if topics:
            sample = topics[0]
            print(" - sample topic id/title:", sample.get("id"), sample.get("title")[:80])
            tid = sample.get("id")
            print("2) Fetching topic details for id", tid)
            rd = requests.get(f"{BASE}/t/{tid}.json", timeout=30)
            rd.raise_for_status()
            tj = rd.json()
            print(" - topic title:", tj.get("title"))
            print(" - views:", tj.get("views"))
            print(" - posts_count:", tj.get("posts_count"))
        return True
    except Exception as e:
        print("Forum test failed:", repr(e))
        return False

def test_db():
    print("3) Testing DB connection and table count...")
    try:
        session = SessionLocal()
        # safer: use scalar() which returns a single value, or use index 0
        res = session.execute(text("SELECT COUNT(*) FROM workflows")).fetchone()
        if res is None:
            print(" - Query returned no rows.")
        else:
            # res may be a tuple like (42,) or a mapping depending on DB driver
            try:
                count = res[0]
            except Exception:
                # fallback if it's a mapping
                count = res.get('c') if isinstance(res, dict) else res
            print(" - workflows table count:", count)
        session.close()
        return True
    except Exception as e:
        print("DB test failed:", repr(e))
        return False

  

if __name__ == "__main__":
    print("Starting test script")
    ok1 = test_forum()
    ok2 = test_db()
    print("Tests finished. forum_ok =", ok1, ", db_ok =", ok2)
