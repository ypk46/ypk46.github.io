"""Sync posts from a Medium RSS feed into data/posts.json and the generated blocks of the site.

Medium's feed only carries the 10 most recent posts, so posts.json keeps every post it has seen
and is never pruned: it is the archive.

Generated blocks (everything between each pair of markers is rewritten):
  index.html          medium          the latest posts on Home
  writing/index.html  medium-latest   the latest post card
  writing/index.html  medium-archive  every other post, grouped by year

Usage: python3 scripts/medium.py <medium-username> [latest-count]
"""

import html
import json
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime
from itertools import groupby

POSTS = "data/posts.json"
MAX_TAGS = 3
# Medium category slugs are lowercase; restore the acronyms we know about.
ACRONYMS = {"ai": "AI", "ml": "ML", "llm": "LLM", "llms": "LLMs", "api": "API", "aws": "AWS"}


def fetch_posts(username):
    req = urllib.request.Request(
        f"https://medium.com/feed/@{username}", headers={"User-Agent": "Mozilla/5.0"}
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        root = ET.fromstring(resp.read())
    posts = []
    for item in root.iter("item"):
        description = item.findtext("description", "")
        snippet = re.search(r'class="medium-feed-snippet">(.*?)</p>', description, re.S)
        image = re.search(r'<img src="([^"]+)"', description)
        posts.append(
            {
                "id": item.findtext("guid", "").rsplit("/", 1)[-1],
                "title": item.findtext("title", "").strip(),
                "url": item.findtext("link", "").split("?")[0],
                "date": parsedate_to_datetime(item.findtext("pubDate")).date().isoformat(),
                "tags": [c.text for c in item.findall("category") if c.text],
                "summary": html.unescape(snippet.group(1)).strip() if snippet else "",
                "image": image.group(1) if image else "",
            }
        )
    return posts


def merge(known, fetched):
    by_id = {p["id"]: p for p in known}
    by_id.update({p["id"]: p for p in fetched})
    return sorted(by_id.values(), key=lambda p: p["date"], reverse=True)


def esc(text):
    return html.escape(text, quote=True)


def humanize(tag):
    words = [ACRONYMS.get(w, w) for w in tag.split("-")]
    first = words[0]
    words[0] = first if first in ACRONYMS.values() else first.capitalize()
    return " ".join(words)


def render_rows(posts):
    if not posts:
        return '<p class="muted">No posts yet.</p>'
    rows = []
    for p in posts:
        summary = f'\n        <span class="post-summary">{esc(p["summary"])}</span>' if p["summary"] else ""
        rows.append(
            f"""  <li>
    <a class="post-row" href="{esc(p["url"])}">
      <time class="post-date" datetime="{p["date"]}">{p["date"]}</time>
      <span class="post-body">
        <span class="post-title">{esc(p["title"])}</span>{summary}
      </span>
      <span class="post-arrow" aria-hidden="true">↗</span>
    </a>
  </li>"""
        )
    return '<ul class="posts">\n' + "\n".join(rows) + "\n</ul>"


def render_latest(post):
    if not post:
        return ""
    summary = f'\n  <p class="lead">{esc(post["summary"])}</p>' if post["summary"] else ""
    tags = "".join(f"<li>{esc(humanize(t))}</li>" for t in post["tags"][:MAX_TAGS])
    tags = f'\n  <ul class="tags" aria-label="Tags">{tags}</ul>' if tags else ""
    return f"""<article class="card latest">
  <div class="latest-meta">
    <div class="label">
      <span class="label-accent">Latest</span>
      <time datetime="{post["date"]}">{post["date"]}</time>
    </div>
    <span class="mono-link mono-link-ink" aria-hidden="true">Read on Medium ↗</span>
  </div>
  <h2><a class="card-link" href="{esc(post["url"])}">{esc(post["title"])}</a></h2>{summary}{tags}
</article>"""


def render_archive(posts):
    """Every post but the latest, grouped by year. The latest still counts toward its year."""
    groups = []
    for year, in_year in groupby(posts, key=lambda p: p["date"][:4]):
        in_year = list(in_year)
        shown = [p for p in in_year if p is not posts[0]]
        if not shown:
            continue
        label = '\n    <p class="label label-accent">Archive</p>' if not groups else ""
        count = f'{len(in_year)} post{"" if len(in_year) == 1 else "s"}'
        rows = render_rows(shown).replace("\n", "\n  ")
        groups.append(
            f"""<section class="archive-year split" aria-labelledby="year-{year}">
  <div class="split-label">{label}
    <h2 class="section-title" id="year-{year}">{year}</h2>
    <p class="count">{count}</p>
  </div>
  {rows}
</section>"""
        )
    return "\n".join(groups)


def replace_block(page, name, body):
    """Replace what sits between <!-- name:start --> and <!-- name:end -->, keeping their indentation."""
    start, end = f"<!-- {name}:start -->", f"<!-- {name}:end -->"
    pattern = re.compile(r"^([ \t]*)" + re.escape(start) + r".*?" + re.escape(end), re.S | re.M)

    def block(match):
        indent = match.group(1)
        lines = [indent + line if line else line for line in body.splitlines()]
        return "\n".join([indent + start, *lines, indent + end])

    page, count = pattern.subn(block, page)
    if count != 1:
        sys.exit(f"Expected one {name} block, found {count}")
    return page


def write_blocks(path, blocks):
    with open(path) as f:
        page = f.read()
    for name, body in blocks.items():
        page = replace_block(page, name, body)
    with open(path, "w") as f:
        f.write(page)


def main():
    username = sys.argv[1].lstrip("@")
    latest = int(sys.argv[2]) if len(sys.argv) > 2 else 3

    try:
        with open(POSTS) as f:
            known = json.load(f)
    except FileNotFoundError:
        known = []
    posts = merge(known, fetch_posts(username))
    with open(POSTS, "w") as f:
        json.dump(posts, f, indent=2, ensure_ascii=False)
        f.write("\n")

    write_blocks("index.html", {"medium": render_rows(posts[:latest])})
    write_blocks(
        "writing/index.html",
        {
            "medium-latest": render_latest(posts[0] if posts else None),
            "medium-archive": render_archive(posts),
        },
    )


if __name__ == "__main__":
    main()
