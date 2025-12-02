import feedparser
from datetime import datetime
import markdownify

# 你的全部 RSS 列表
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

# 输出文件路径
OUTPUT_FILE = "output/daily.md"

def fetch_rss(feed_url):
    """抓取单个 RSS 源"""
    try:
        feed = feedparser.parse(feed_url)
        return feed
    except Exception as e:
        print(f"Error fetching {feed_url}: {e}")
        return None

def generate_markdown(feeds):
    """生成 Markdown 摘要"""
    today = datetime.utcnow().strftime("%Y-%m-%d")

    md = f"# 📚 Daily RSS Summary — {today}\n"
    md += "自动抓取主要地学期刊 & 综合科学期刊最新文章。\n\n"

    for feed in feeds:
        if not feed or not feed.entries:
            continue

        feed_title = feed.feed.get("title", "Untitled Feed")
        md += f"\n---\n\n## 📰 {feed_title}\n"

        for entry in feed.entries[:10]:  # 每个源最多取 10 篇
            title = entry.get("title", "No title")
            link = entry.get("link", "#")
            summary_html = entry.get("summary", "")
            summary_md = markdownify.markdownify(summary_html, strip=['a'])

            md += f"### [{title}]({link})\n"
            md += f"{summary_md}\n\n"

    return md

def main():
    print("Fetching RSS feeds...")
    feeds = [fetch_rss(url) for url in RSS_FEEDS]

    print("Generating markdown...")
    md_content = generate_markdown(feeds)

    print(f"Writing output to {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(md_content)

    print("Done.")

if __name__ == "__main__":
    main()
