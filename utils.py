# utils.py
import re
from rapidfuzz import fuzz

def normalize_title(title: str) -> str:
    t = (title or "").lower()
    t = re.sub(r'[^a-z0-9\s]', ' ', t)
    t = re.sub(r'\s+', ' ', t).strip()
    return t

def is_similar(a: str, b: str, threshold=85) -> bool:
    try:
        return fuzz.partial_ratio(a, b) >= threshold
    except Exception:
        return False
