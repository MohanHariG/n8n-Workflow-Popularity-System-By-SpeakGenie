import requests

BASE = "https://community.n8n.io"

# fetch latest topics
r = requests.get(f"{BASE}/latest.json")
r.raise_for_status()
topics = r.json().get("topic_list", {}).get("topics", [])
print("Found topics:", len(topics))
for t in topics[:5]:
    print(t["id"], t["title"])

# fetch details for the first topic
if topics:
    tid = topics[0]["id"]
    rd = requests.get(f"{BASE}/t/{tid}.json")
    rd.raise_for_status()
    topic_json = rd.json()
    print("Title:", topic_json.get("title"))
    print("views:", topic_json.get("views"))
    print("posts_count:", topic_json.get("posts_count"))
    print("posters count:", len(topic_json.get("posters", [])))
