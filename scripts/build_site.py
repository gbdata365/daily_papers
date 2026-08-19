# -*- coding: utf-8 -*-
"""
Daily Papers 아카이브 사이트 빌드 스크립트.

새 날짜를 추가하려면:
1. downloads/ 아래에 해당 날짜 논문들의 {베이스파일명}_summary_new.md 를 준비한다
   (paper-analyzer 에이전트로 생성, 파일명 규칙은 .claude/agents/paper-analyzer_new.md 참고)
2. data/day_config/{날짜}.json 파일을 추가한다 (arxiv_id -> 메타데이터, 아래 CONFIG_SCHEMA 참고)
   파이썬 소스(이 파일)는 건드리지 않는다 — 자동화 스크립트/에이전트가 데이터 파일만 쓰면 된다.
3. `py -3 scripts/build_site.py` 실행 -> papers/*.html, data/{date}.json, data/index.json 생성/갱신
"""
import glob
import json
import os
import re

import markdown

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOWNLOADS = os.path.join(BASE, "downloads")
PAPERS_DIR = os.path.join(BASE, "papers")
DATA_DIR = os.path.join(BASE, "data")
DAY_CONFIG_DIR = os.path.join(DATA_DIR, "day_config")

os.makedirs(PAPERS_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(DAY_CONFIG_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# 날짜별 논문 메타데이터는 data/day_config/{YYYY-MM-DD}.json 에 저장한다.
# 각 파일: { arxiv_id: {
#   "base": downloads/ 안의 파일 베이스명 (확장자 제외, "_summary_new.md" 앞부분)
#   "rank", "category", "category_label", "upvote"
#   "en_title": 원제목(영문, arXiv 그대로)
#   "ko_title": 한글 번역 제목
# }, ... }
# ---------------------------------------------------------------------------


def load_day_configs():
    configs = {}
    for path in sorted(glob.glob(os.path.join(DAY_CONFIG_DIR, "*.json"))):
        date = os.path.splitext(os.path.basename(path))[0]
        with open(path, "r", encoding="utf-8") as f:
            configs[date] = json.load(f)
    return configs

PAGE_TEMPLATE = """<meta charset="UTF-8">
<title>{title_tag}</title>
<style>
  :root{{
    --bg:#ffffff; --bg-alt:#f5f5f7; --text:#1d1d1f; --text-secondary:#6e6e73;
    --accent:#0071e3; --accent-hover:#0077ed; --line: rgba(0,0,0,0.08);
    --font: -apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text", "Segoe UI", Roboto, "Malgun Gothic", "Apple SD Gothic Neo", Helvetica, Arial, sans-serif;
    --font-mono: ui-monospace, "SF Mono", SFMono-Regular, Menlo, Consolas, monospace;
  }}
  *{{ box-sizing:border-box; }}
  body{{ margin:0; background:var(--bg); color:var(--text); font-family:var(--font); line-height:1.6; -webkit-font-smoothing:antialiased; }}
  a{{ color:var(--accent); text-decoration:none; }}
  a:hover{{ text-decoration:underline; }}
  .wrap{{ max-width:760px; margin:0 auto; padding:0 24px; }}

  #nav{{ position:sticky; top:0; z-index:10; height:52px; display:flex; align-items:center;
    background:rgba(255,255,255,0.85); backdrop-filter:saturate(180%) blur(20px);
    -webkit-backdrop-filter:saturate(180%) blur(20px); border-bottom:1px solid var(--line); }}
  #nav .wrap{{ display:flex; align-items:center; justify-content:space-between; max-width:900px; }}
  #nav .back{{ font-size:0.86rem; color:var(--text-secondary); font-weight:500; }}
  #nav .back:hover{{ color:var(--text); }}
  #nav .brand{{ font-weight:600; font-size:0.92rem; }}

  header.article-head{{ padding: 3.4rem 0 2.2rem; border-bottom:1px solid var(--line); }}
  .kicker-row{{ display:flex; align-items:center; gap:0.6rem; flex-wrap:wrap; margin-bottom:1rem; }}
  .rank{{ font-family:var(--font-mono); font-size:0.78rem; color:var(--text-secondary); }}
  .cat-tag{{ font-size:0.72rem; font-weight:600; color:var(--accent); background:rgba(0,113,227,0.1); border-radius:980px; padding:0.25rem 0.7rem; }}
  .upvote-tag{{ font-family:var(--font-mono); font-size:0.78rem; font-weight:600; color:var(--accent); }}
  h1.article-title{{ font-size:clamp(1.5rem,2vw + 1rem,2.1rem); font-weight:700; letter-spacing:-0.01em; line-height:1.35; margin:0; }}
  .article-title-ko{{ margin-top:0.6rem; font-size:clamp(1.15rem,1.4vw + 0.8rem,1.5rem); font-weight:600; color:var(--text-secondary); letter-spacing:-0.01em; line-height:1.4; }}
  .article-sub{{ margin-top:1.1rem; font-size:1.02rem; color:var(--text-secondary); }}
  .meta-links{{ margin-top:1.4rem; display:flex; gap:1.4rem; flex-wrap:wrap; font-size:0.86rem; }}

  article.body{{ padding: 2.6rem 0 5rem; font-size:1rem; }}
  article.body h2{{ font-size:1.32rem; font-weight:700; margin:2.4rem 0 1rem; letter-spacing:-0.01em; }}
  article.body h2:first-child{{ margin-top:0; }}
  article.body p{{ margin:0.9rem 0; color:var(--text); }}
  article.body ul{{ margin:0.9rem 0; padding-left:1.3rem; }}
  article.body li{{ margin:0.5rem 0; color:var(--text); }}
  article.body li p {{ margin: 0; display:inline; }}
  article.body strong{{ font-weight:600; }}
  article.body code{{ font-family:var(--font-mono); background:var(--bg-alt); padding:0.1rem 0.35rem; border-radius:5px; font-size:0.88em; }}

  .back-bottom{{ margin-top:2rem; padding-top:2rem; border-top:1px solid var(--line); }}
  footer{{ padding:2rem 0; border-top:1px solid var(--line); }}
  footer .wrap{{ display:flex; justify-content:space-between; flex-wrap:wrap; gap:0.8rem; color:var(--text-secondary); font-size:0.78rem; }}
</style>

<nav id="nav">
  <div class="wrap">
    <a class="back" href="../index.html">← 목록으로</a>
    <span class="brand">Daily Papers</span>
  </div>
</nav>

<header class="article-head">
  <div class="wrap">
    <div class="kicker-row">
      <span class="rank">{rank} · Daily Papers {date}</span>
      <span class="cat-tag">{cat_label}</span>
      <span class="upvote-tag">▲ {upvote}</span>
    </div>
    <h1 class="article-title">{en_title}</h1>
    <p class="article-title-ko">{ko_title}</p>
    <p class="article-sub">{one_liner}</p>
    <div class="meta-links">
      <a href="https://huggingface.co/papers/{arxiv_id}" target="_blank" rel="noopener">Hugging Face 페이지 →</a>
      <a href="https://arxiv.org/abs/{arxiv_id}" target="_blank" rel="noopener">arXiv 원문 →</a>
    </div>
  </div>
</header>

<article class="body">
  <div class="wrap">
{body_html}
    <div class="back-bottom">
      <a href="../index.html">← Daily Papers 목록으로 돌아가기</a>
    </div>
  </div>
</article>

<footer>
  <div class="wrap">
    <span>출처: <a href="https://huggingface.co/papers/{arxiv_id}" target="_blank" rel="noopener">huggingface.co/papers/{arxiv_id}</a> · {date}</span>
    <span>my-design 시스템 적용</span>
  </div>
</footer>
"""


def extract_one_liner(md_text):
    m = re.search(r"## 한 줄 요약\s*\n+(.+?)\n", md_text)
    return m.group(1).strip() if m else ""


def strip_top_heading(md_text):
    lines = md_text.split("\n")
    if lines and lines[0].startswith("# "):
        lines = lines[1:]
    return "\n".join(lines).strip()


def build():
    day_configs = load_day_configs()
    dates = sorted(day_configs.keys(), reverse=True)

    for date, papers in day_configs.items():
        day_list = []
        for arxiv_id, meta in papers.items():
            md_path = os.path.join(DOWNLOADS, f"{meta['base']}_summary_new.md")
            with open(md_path, "r", encoding="utf-8") as f:
                md_text = f.read()

            one_liner = extract_one_liner(md_text)
            body_html = markdown.markdown(strip_top_heading(md_text), extensions=["extra"])

            html = PAGE_TEMPLATE.format(
                title_tag=meta["ko_title"].split(":")[0].split(",")[0].strip(),
                rank=meta["rank"],
                cat_label=meta["category_label"],
                upvote=meta["upvote"],
                en_title=meta["en_title"],
                ko_title=meta["ko_title"],
                one_liner=one_liner,
                arxiv_id=arxiv_id,
                date=date,
                body_html=body_html,
            )
            out_path = os.path.join(PAPERS_DIR, f"{arxiv_id}_new.html")
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(html)

            day_list.append({
                "arxiv_id": arxiv_id,
                "rank": meta["rank"],
                "category": meta["category"],
                "category_label": meta["category_label"],
                "upvote": int(meta["upvote"]),
                "en_title": meta["en_title"],
                "ko_title": meta["ko_title"],
                "one_liner": one_liner,
                "hf_url": f"https://huggingface.co/papers/{arxiv_id}",
                "arxiv_url": f"https://arxiv.org/abs/{arxiv_id}",
                "detail_url": f"papers/{arxiv_id}_new.html",
            })

        day_list.sort(key=lambda p: p["upvote"], reverse=True)
        day_path = os.path.join(DATA_DIR, f"{date}.json")
        with open(day_path, "w", encoding="utf-8") as f:
            json.dump({"date": date, "papers": day_list}, f, ensure_ascii=False, indent=2)
        print("wrote", day_path, f"({len(day_list)} papers)")

    index_path = os.path.join(DATA_DIR, "index.json")
    with open(index_path, "w", encoding="utf-8") as f:
        json.dump({"dates": dates}, f, ensure_ascii=False, indent=2)
    print("wrote", index_path, dates)


if __name__ == "__main__":
    build()
