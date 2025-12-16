# collectors/trends_collector.py
import os
import json
import time
import random
from pytrends.request import TrendReq
from db import SessionLocal
from api.models import Workflow
from utils import normalize_title

# pytrends session builder (vary UA slightly to reduce identical fingerprint)
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko)",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko)"
]

def build_pytrends_session():
    ua = random.choice(USER_AGENTS)
    return TrendReq(hl='en-US', tz=360, requests_args={"headers": {"User-Agent": ua}})

def get_trend(query, geo='US', timeframe='today 3-m', max_retries=5):
    """
    Safer pytrends fetch with exponential backoff and jitter.
    Returns a dict with trend metrics or None if it cannot fetch.
    """
    attempt = 0
    backoff = 1.0
    while attempt < max_retries:
        attempt += 1
        try:
            pytrends = build_pytrends_session()
            pytrends.build_payload([query], timeframe=timeframe, geo=geo)
            df = pytrends.interest_over_time()
            if df.empty:
                return None
            series = df[query].tolist()
            recent = float(df[query].tail(30).mean()) if len(df) >= 1 else 0.0
            if len(df) >= 60:
                previous = float(df[query].head(30).mean())
            elif len(df) > 30:
                previous = float(df[query].head(len(df)-30).mean())
            else:
                previous = recent
            change_pct = ((recent - previous) / previous * 100.0) if previous and previous != 0 else 0.0
            # polite pause
            time.sleep(0.5 + random.random() * 0.8)
            return {
                "query": query,
                "geo": geo,
                "timeframe": timeframe,
                "avg_recent": recent,
                "change_pct": change_pct,
                "series": series
            }
        except Exception as e:
            # print error and backoff
            print(f"pytrends attempt {attempt} error for {query} {geo} : {e}")
            sleep_time = backoff + random.random() * backoff
            time.sleep(sleep_time)
            backoff *= 2
    print(f"pytrends permanently failed for {query} {geo} after {max_retries} attempts.")
    return None

def upsert_trend(query, trend_obj, country='US'):
    """
    Insert or update a Workflow row for the given query + trend data.
    Stores trend data in 'evidence' JSON and writes avg_recent into 'views' as a numeric proxy.
    """
    session = SessionLocal()
    try:
        workflow_name = query
        normalized = normalize_title(workflow_name)
        evidence = {"type": "google_trends", "payload": trend_obj}

        wf = session.query(Workflow).filter_by(platform="Google", normalized_name=normalized, country=country).first()
        if wf:
            wf.views = max(int(wf.views or 0), int(trend_obj.get("avg_recent", 0)))
            wf.evidence = evidence
            wf.workflow_name = workflow_name
        else:
            wf = Workflow(
                workflow_name=workflow_name,
                normalized_name=normalized,
                platform="Google",
                country=country,
                evidence=evidence,
                views=int(trend_obj.get("avg_recent", 0)),
                likes=0,
                comments=0,
                replies=0,
                contributors=0,
                source_url=None
            )
            session.add(wf)
        session.commit()
        return True
    except Exception as e:
        session.rollback()
        print("Error in upsert_trend:", e)
        raise
    finally:
        session.close()
