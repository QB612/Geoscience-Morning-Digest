# scripts/generate_digest.py
import os
import json
from datetime import datetime
from openai import OpenAI

# -------------------
OUTPUT_FILE = "output/daily_digest.txt"
SEEN_JSON_PATH = "state/seen.json"

today = datetime.now().strftime("%Y-%m-%d")

# -------------------
# 读取已抓取论文
if not os.path.exists(SEEN_JSON_PATH):
    print("seen.json 不存在，请先抓取 RSS。")
    exit(1)

with open(SEEN_JSON_PATH, "r", encoding="utf-8") as f:
    seen = json.load(f)

# 严格筛选今日新增
papers_data = [p for p in seen if isinstance(p, dict) and p.get("date") == today]

if not papers_data:
    print("今日没有新增论文。")
    digest_text = "今日没有新增论文。"
else:
    # -------------------
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
    if not DEEPSEEK_API_KEY:
        raise ValueError("请设置环境变量 DEEPSEEK_API_KEY")
    
    client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")
    
    # 构建论文简要列表
    papers_brief = "\n".join([
        f"{p.get('title','未知标题')} ({p.get('source','未知期刊')})"
        for p in papers_data
    ])
    
    system_prompt = (
        "你是一名地球科学领域科研助手。\n"
        "请根据以下论文列表生成科研日报。\n"
        "要求：\n"
        "1. 整体趋势提炼，6-8点。\n"
        "2. 按主题自动分类，表格形式：主题 | 代表论文 | 备注。\n"
        "3. 每篇论文一句话核心贡献。\n"
        "4. 输出文本格式，保留 AI 输出的所有三部分。\n"
        "5. 不要包含原始条目列表。"
    )

    user_prompt = f"今天日期：{today}\n新增论文列表：\n{papers_brief}"

    try:
        resp = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            stream=False
        )
        digest_text = resp.choices[0].message.content.strip()
    except Exception as e:
        digest_text = f"摘要生成失败: {e}"

# -------------------
# 构建最终文本
email_content = f"Daily Paper Digest — {today}\n"
email_content += f"今日新增论文：{len(papers_data)}\n\n"
email_content += "摘要整理：\n"
email_content += digest_text + "\n"

# -------------------
# 附录：原始文章信息
if papers_data:
    email_content += "\n---\n附录：原始文章信息\n"
    for i, p in enumerate(papers_data, 1):
        email_content += f"\n{i}. {p.get('title','未知标题')}\n"
        
        # ✅ 修复 authors 报错
        authors_list = [str(a) for a in p.get('authors', []) if a]  # 转为字符串并去掉 None
        authors_str = ', '.join(authors_list) if authors_list else '未知'
        email_content += f"   作者：{authors_str}\n"
        
        email_content += f"   期刊/来源：{p.get('source','未知')}\n"
        email_content += f"   链接：{p.get('link','')}\n"
        if p.get("summary"):
            email_content += f"   摘要：{p['summary']}\n"

# -------------------
# 写入文件
os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write(email_content)

print(f"日报已生成：{OUTPUT_FILE}")
