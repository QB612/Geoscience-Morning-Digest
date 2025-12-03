# scripts/fetch_rss.py
import feedparser
import json
import os
from datetime import datetime

# -------------------------
# 配置 RSS 列表 & 文件路径
# -------------------------
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

# -------------------------
# 加载已收录论文
# -------------------------
def load_seen():
    os.makedirs("state", exist_ok=True)
    if not os.path.exists(SEEN_FILE):
        return []
    try:
        with open(SEEN_FILE, "r", encoding="utf-8") as f:
            data = f.read().strip()
            if not data:
                return []
            return json.loads(data)
    except Exception as e:
        print(f"读取 seen.json 失败: {e}")
        return []

# -------------------------
# 保存论文
# -------------------------
def save_seen(seen_list):
    os.makedirs("state", exist_ok=True)
    with open(SEEN_FILE, "w", encoding="utf-8") as f:
        json.dump(seen_list, f, ensure_ascii=False, indent=2)

# -------------------------
# 抓取 RSS
# -------------------------
def fetch_new_entries():
    print("开始抓取 RSS...")
    seen_list = load_seen()
    seen_uids = {p['uid'] for p in seen_list}

    new_entries = []
    today_str = datetime.now().strftime("%Y-%m-%d")

    for url in RSS_FEEDS:
        print(f"\n解析 RSS: {url}")
        feed = feedparser.parse(url)
        source_name = feed.feed.get("title", "Unknown Source")
        entries = feed.entries
        print(f"  -> 发现 {len(entries)} 条论文")

        for entry in entries:
            uid = entry.get("id") or entry.get("link")
            if not uid or uid in seen_uids:
                continue

            paper = {
                "uid": uid,
                "title": entry.get("title", "未知标题"),
                "authors": [a.get("name") for a in entry.get("authors", [])] if entry.get("authors") else [],
                "source": source_name,
                "link": entry.get("link", ""),
                "summary": entry.get("summary", "").strip(),
                "date": today_str
            }

            seen_list.append(paper)
            new_entries.append(paper)
            seen_uids.add(uid)

    print(f"\n抓取完成: 新增 {len(new_entries)} 条论文")
    save_seen(seen_list)
    return new_entries

# -------------------------
# 主函数
# -------------------------
if __name__ == "__main__":
    new_papers = fetch_new_entries()
    print("done")
