"""
Blog publisher: reads all posts/*.md (with YAML frontmatter), renders HTML for
each post, regenerates index.html and feed.rss, and copies static files into out/.

Usage:
    python3 publish.py            # build everything
    python3 publish.py <post.md>  # build a single post only (no index/feed update)

Each post must have a YAML frontmatter block with at least:
    ---
    title: "Post Title"
    date: YYYY-MM-DD
    ---
"""

import json
import os
import re
import shutil
import sys

from email import utils
from datetime import datetime, date, timezone
from xml.sax.saxutils import escape as xml_escape

import pystache
import pypandoc
import yaml


ROOT = os.path.dirname(os.path.abspath(__file__))
POSTS_DIR = os.path.join(ROOT, "posts")
OUT_DIR = os.path.join(ROOT, "out")

SITE_URL = "https://blog.isaacjennings.org"
SITE_NAME = "Isaac's Blog"
AUTHOR_NAME = "Isaac Jennings"
AUTHOR_URL = "https://isaacjennings.org"
SITE_DESCRIPTION = "The personal blog of Isaac Jennings"
EXCERPT_LEN = 155
FM_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.DOTALL)

STATIC_FILES = [
    "style.css",
    "head.svg",
    "CNAME",
    "charter_regular-webfont.eot",
    "charter_regular-webfont.woff",
    "charter_italic-webfont.eot",
    "charter_italic-webfont.woff",
]


def ensure_pandoc():
    try:
        pypandoc.get_pandoc_version()
    except OSError:
        sys.exit("pandoc is required. Install it with: brew install pandoc")


# ---------------------------------------------------------------------------
# Frontmatter parsing
# ---------------------------------------------------------------------------

def split_frontmatter(md):
    m = FM_RE.match(md)
    if not m:
        return {}, md
    meta = yaml.safe_load(m.group(1)) or {}
    return meta, md[m.end():]


# ---------------------------------------------------------------------------
# Post helpers
# ---------------------------------------------------------------------------

def stem(filename):
    """'Some_Post.md' → 'Some_Post'"""
    return os.path.basename(filename)[:-3]


def out_file(filename):
    return stem(filename) + ".html"


def to_date(value):
    """Coerce a frontmatter date value to a Python date."""
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        return date.fromisoformat(value)
    raise ValueError(f"Cannot parse date: {value!r}")


def rfc2822(d):
    """Format a date as RFC 2822 for RSS pubDate."""
    dt = datetime(d.year, d.month, d.day, tzinfo=timezone.utc)
    return utils.format_datetime(dt)


def make_excerpt(body, limit=EXCERPT_LEN):
    """Plain-text excerpt of a markdown body for meta descriptions."""
    text = pypandoc.convert_text(body, "plain", format="md")
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) <= limit:
        return text
    cut = text[:limit].rsplit(" ", 1)[0].rstrip(" .,;:—-")
    return cut + "…"


def build_jsonld(title, description, url, post_date):
    """schema.org BlogPosting as a script-tag-safe JSON string."""
    data = {
        "@context": "https://schema.org",
        "@type": "BlogPosting",
        "headline": title,
        "description": description,
        "url": url,
        "mainEntityOfPage": url,
        "datePublished": post_date.isoformat(),
        "author": {"@type": "Person", "name": AUTHOR_NAME, "url": AUTHOR_URL},
        "publisher": {"@type": "Person", "name": AUTHOR_NAME, "url": AUTHOR_URL},
    }
    # Escape "<" so the payload can never break out of the <script> element.
    return json.dumps(data, ensure_ascii=False).replace("<", "\\u003c")


def get_post(filename):
    path = os.path.join(POSTS_DIR, filename)
    with open(path, encoding="utf-8") as f:
        contents = f.read()

    meta, body = split_frontmatter(contents)

    post_date = to_date(meta["date"]) if "date" in meta else date.fromtimestamp(os.stat(path).st_mtime)
    title = meta.get("title") or stem(filename).replace("_", " ")
    description = meta.get("description") or make_excerpt(body)
    url = f"{SITE_URL}/{out_file(filename)}"

    return {
        "filename": filename,
        "out_file": out_file(filename),
        "title": title,
        "description": description,
        "url": url,
        "jsonld": build_jsonld(title, description, url, post_date),
        "date": str(post_date),
        "date_and_time": rfc2822(post_date),
        "post": pypandoc.convert_text(body, "html", format="md"),
        "_date_obj": post_date,
    }


def get_posts():
    today = date.today()
    os.makedirs(POSTS_DIR, exist_ok=True)
    filenames = sorted(f for f in os.listdir(POSTS_DIR) if f.endswith(".md"))
    posts = [get_post(f) for f in filenames]
    posts = [p for p in posts if p["_date_obj"] <= today]
    posts.sort(key=lambda p: p["_date_obj"], reverse=True)
    return posts


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------

def render_post(tpl, post):
    html = pystache.render(tpl, post)
    with open(os.path.join(OUT_DIR, post["out_file"]), "w+", encoding="utf-8") as f:
        f.write(html)


def render_index(tpl, posts):
    html = pystache.render(tpl, {
        "posts": posts,
        "has_posts": bool(posts),
    })
    with open(os.path.join(OUT_DIR, "index.html"), "w+", encoding="utf-8") as f:
        f.write(html)


def render_feed(tpl, posts):
    build_date = rfc2822(date.today())
    xml = pystache.render(tpl, {"date": build_date, "posts": posts})
    with open(os.path.join(OUT_DIR, "feed.rss"), "w+", encoding="utf-8") as f:
        f.write(xml)


def render_sitemap(posts):
    entries = [(f"{SITE_URL}/", date.today())]
    entries += [(p["url"], p["_date_obj"]) for p in posts]
    urls = "\n".join(
        f"  <url>\n    <loc>{xml_escape(loc)}</loc>\n"
        f"    <lastmod>{lastmod.isoformat()}</lastmod>\n  </url>"
        for loc, lastmod in entries
    )
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{urls}\n</urlset>\n"
    )
    with open(os.path.join(OUT_DIR, "sitemap.xml"), "w+", encoding="utf-8") as f:
        f.write(xml)


def render_robots():
    txt = f"User-agent: *\nAllow: /\n\nSitemap: {SITE_URL}/sitemap.xml\n"
    with open(os.path.join(OUT_DIR, "robots.txt"), "w+", encoding="utf-8") as f:
        f.write(txt)


def copy_static():
    os.makedirs(OUT_DIR, exist_ok=True)
    for name in STATIC_FILES:
        src = os.path.join(ROOT, name)
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(OUT_DIR, name))

    assets_src = os.path.join(ROOT, "assets")
    assets_dst = os.path.join(OUT_DIR, "assets")
    if os.path.isdir(assets_src):
        shutil.copytree(assets_src, assets_dst, dirs_exist_ok=True)

    blargl_src = os.path.join(ROOT, "blargl")
    blargl_dst = os.path.join(OUT_DIR, "blargl")
    if os.path.isdir(blargl_src):
        shutil.copytree(
            blargl_src,
            blargl_dst,
            dirs_exist_ok=True,
            ignore=shutil.ignore_patterns("src", "elm-package.json", "build.sh"),
        )


# ---------------------------------------------------------------------------
# Entry points
# ---------------------------------------------------------------------------

def build_all():
    ensure_pandoc()
    if os.path.isdir(OUT_DIR):
        shutil.rmtree(OUT_DIR)
    os.makedirs(OUT_DIR)
    posts = get_posts()
    print(f"Building {len(posts)} posts into {os.path.relpath(OUT_DIR, ROOT)}/...")

    with open(os.path.join(ROOT, "layout.html"), encoding="utf-8") as f:
        post_tpl = f.read()
    for post in posts:
        render_post(post_tpl, post)

    with open(os.path.join(ROOT, "index_layout.html"), encoding="utf-8") as f:
        index_tpl = f.read()
    render_index(index_tpl, posts)
    print("  index.html written")

    with open(os.path.join(ROOT, "feed_tpl.rss"), encoding="utf-8") as f:
        feed_tpl = f.read()
    render_feed(feed_tpl, posts)
    print("  feed.rss written")

    render_sitemap(posts)
    print("  sitemap.xml written")

    render_robots()
    print("  robots.txt written")

    copy_static()
    print("  static files copied")


def build_one(target):
    """Render a single post file (path or bare filename inside posts/)."""
    ensure_pandoc()
    os.makedirs(OUT_DIR, exist_ok=True)
    filename = os.path.basename(target)
    if not filename.endswith(".md"):
        filename += ".md"
    post = get_post(filename)

    with open(os.path.join(ROOT, "layout.html"), encoding="utf-8") as f:
        tpl = f.read()
    render_post(tpl, post)
    copy_static()
    print(f"  {os.path.relpath(OUT_DIR, ROOT)}/{post['out_file']} written")


if __name__ == "__main__":
    if len(sys.argv) == 1:
        build_all()
    elif len(sys.argv) == 2:
        build_one(sys.argv[1])
    else:
        print(__doc__)
        sys.exit(1)
