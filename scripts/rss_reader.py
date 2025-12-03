# scripts/rss_reader.py
import feedparser
import json
import os
from datetime import datetime

RSS_FEEDS = [
    "http://www.nature.com/nature/current_issue/rss",
    "https://www.science.org/action/showFeed?type=etoc&feed=rss&jc=science",
    "https://www.science.org/action/showFeed?type=etoc&feed=rss&jc=sciadv",
    "https://www.nature.com/ngeo.rss",
    "https://www.nature.com/ncomms.rss",
    "https://www.nature.com/natrevearthenviron.rss",
    "https://www.pnas.org/action/showFeed?type=searchTopic&taxonomyCode=topic&tagCode=earth-sci",
    "https://www.annualreviews.org/rss/content/journals/earth/latestarticles?fmt=rss",
    "https://rss.sciencedirect.com/publication/science/00128252",
    "https://rss.sciencedirect.com/publication/science/0012821X",
    "https://agupubs.onlinelibrary.wiley.com/feed/19448007/most-recent",
    "https://agupubs.onlinelibrary.wiley.com/feed/21699356/most-recent",
    "https://agupubs.onlinelibrary.wiley.com/feed/15252027/most-recent",
    "https://rss.sciencedirect.com/publication/science/00167037"
]

SEEN_FILE = "state/seen.json"

today = datetime.now().strftime("%Y-%m-%d")

# -------------------------
# Load / Save Seen IDs
# -------------------------
def load_seen():
    if not os.path.exists(SEEN_FILE):
        return []
    try:
        with open(SEEN_FILE, "r", encoding="utf-8") as f:
            data = f.read().strip()
            return json.loads(data) if data else []
    except Exception as e:
        print(f"读取 seen.json 出错: {e}")
        return []

def save_seen(seen_list):
    os.makedirs(os.path.dirname(SEEN_FILE), exist_ok=True)
    with open(SEEN_FILE, "w", encoding="utf-8") as f:
        json.dump(seen_list, f, indent=2, ensure_ascii=False)

# -------------------------
# Fetch RSS Feeds
# -------------------------
def fetch_new_entries():
    seen = load_seen()
    seen_ids = {p.get("id") for p in seen if "id" in p}

    new_entries = []

    for url in RSS_FEEDS:
        print(f"解析 RSS: {url}")
        feed = feedparser.parse(url)
        source_name = feed.feed.get("title", "未知来源")

        for entry in feed.entries:
            uid = entry.get("id") or entry.get("link")
            if not uid or uid in seen_ids:
                continue

            # 安全获取作者列表
            authors = []
            if "authors" in entry:
                for a in entry.authors:
                    name = a.get("name")
                    if name:
                        authors.append(name)

            new_entry = {
                "id": uid,
                "title": entry.get("title", "未知标题"),
                "link": entry.get("link", ""),
                "authors": authors,
                "summary": entry.get("summary", "").strip(),
                "source": source_name,
                "date": today
            }

            new_entries.append(new_entry)
            seen_ids.add(uid)
            seen.append(new_entry)

    save_seen(seen)
    print(f"共抓取 {len(new_entries)} 篇新论文")
    return new_entries

# -------------------------
# Main
# -------------------------
if __name__ == "__main__":
    new_papers = fetch_new_entries()
    if not new_papers:
        print("今日无新增论文。")
    else:
        print("新增论文列表：")
        for p in new_papers:
            print(f"- {p['title']} ({p['source']})")
