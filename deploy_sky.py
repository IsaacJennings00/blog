"""
Sync published posts/*.md into ../sky/content/posts/ and the live sky
(sora-to-ki) SQLite database on root@home, then clear Nitro's ISR cache.

Usage:
    python3 deploy_sky.py            # sync posts to ../sky and publish to root@home
    python3 deploy_sky.py --dry-run  # preview NEW / UPDATED / UNCHANGED against root@home
    python3 deploy_sky.py --host root@home
"""

import argparse
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
from datetime import date

import publish

SKY_POSTS_DIR = os.path.normpath(os.path.join(publish.ROOT, "..", "sky", "content", "posts"))

REMOTE_SCRIPT = r"""
import json, sqlite3, sys, urllib.request

payload = json.load(sys.stdin)
dry_run = payload["dry_run"]
posts = payload["posts"]

db_path = "/var/lib/docker/volumes/isaacjennings_backend-db/_data/db.sqlite"
conn = sqlite3.connect(db_path, timeout=10)
existing = {
    slug: (pid, title, content, excerpt)
    for pid, slug, title, content, excerpt in conn.execute(
        "SELECT id, slug, title, content, excerpt FROM posts WHERE slug IS NOT NULL"
    ).fetchall()
}

changed = 0
for p in posts:
    slug = p["slug"]
    title = p["title"]
    body = p["body"]
    excerpt = p["excerpt"]
    created = f"{p['date']} 12:00:00"

    cur = existing.get(slug)
    if cur is None:
        print(f"  + NEW       {p['date']}  {slug}  ({title})")
        changed += 1
        if not dry_run:
            with conn:
                conn.execute(
                    "INSERT INTO posts "
                    "(title, content, excerpt, status, author, created_at, updated_at, source_language, format, slug, title_en, content_en, excerpt_en) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (title, body, excerpt, "published", "Isaac Jennings", created, created, "en", "markdown", slug, title, body, excerpt),
                )
    elif (cur[1], cur[2], cur[3]) != (title, body, excerpt):
        print(f"  ~ UPDATED   {p['date']}  {slug}  ({title})")
        changed += 1
        if not dry_run:
            with conn:
                conn.execute(
                    "UPDATE posts SET title = ?, content = ?, excerpt = ?, title_en = ?, content_en = ?, excerpt_en = ?, updated_at = datetime('now') WHERE id = ?",
                    (title, body, excerpt, title, body, excerpt, cur[0]),
                )
    else:
        print(f"  = UNCHANGED {p['date']}  {slug}")

conn.close()

if dry_run:
    print(f"Dry run complete: {changed} post(s) would be added/updated out of {len(posts)}.")
elif changed > 0:
    secret_path = "/var/lib/docker/volumes/isaacjennings_revalidate-key/_data/secret"
    with open(secret_path, encoding="utf-8") as f:
        secret = f.read().strip()
    req = urllib.request.Request(
        "http://127.0.0.1:13579/_revalidate",
        method="POST",
        headers={"x-revalidate-secret": secret},
    )
    with urllib.request.urlopen(req, timeout=5) as resp:
        info = resp.read().decode("utf-8")
    print(f"Published {changed} change(s); ISR revalidated ({info}).")
else:
    print(f"All {len(posts)} post(s) already up to date on server.")
"""


def slug_for(filename: str) -> str:
    s = publish.stem(filename).lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


def load_published_posts():
    today = date.today()
    items = []
    for filename in sorted(f for f in os.listdir(publish.POSTS_DIR) if f.endswith(".md")):
        path = os.path.join(publish.POSTS_DIR, filename)
        with open(path, encoding="utf-8") as f:
            raw = f.read()
        meta, body_raw = publish.split_frontmatter(raw)
        post_date = (
            publish.to_date(meta["date"])
            if "date" in meta
            else date.fromtimestamp(os.stat(path).st_mtime)
        )
        if post_date > today:
            continue
        title = (meta.get("title") or publish.stem(filename).replace("_", " ")).strip()
        body = body_raw.strip()
        first_para = next((p for p in body.split("\n\n") if p.strip()), "")
        excerpt = first_para[:240]
        items.append(
            {
                "filename": filename,
                "path": path,
                "slug": slug_for(filename),
                "title": title,
                "date": post_date.isoformat(),
                "body": body,
                "excerpt": excerpt,
            }
        )
    items.sort(key=lambda p: p["date"], reverse=True)
    return items


def main():
    parser = argparse.ArgumentParser(description="Publish blog posts to sky on VPS.")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without modifying ../sky or VPS")
    parser.add_argument("--host", default="root@home", help="SSH target hosting sky (default: root@home)")
    args = parser.parse_args()

    posts = load_published_posts()
    if not args.dry_run and os.path.isdir(SKY_POSTS_DIR):
        for p in posts:
            shutil.copy2(p["path"], os.path.join(SKY_POSTS_DIR, p["filename"]))

    payload = json.dumps(
        {
            "dry_run": args.dry_run,
            "posts": [
                {
                    "slug": p["slug"],
                    "title": p["title"],
                    "date": p["date"],
                    "body": p["body"],
                    "excerpt": p["excerpt"],
                }
                for p in posts
            ],
        }
    )
    res = subprocess.run(
        ["ssh", args.host, f"python3 -c {shlex.quote(REMOTE_SCRIPT)}"],
        input=payload,
        text=True,
    )
    sys.exit(res.returncode)


if __name__ == "__main__":
    main()
