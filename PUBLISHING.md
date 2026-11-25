# Publishing with blargl

blargl is a distraction-free, split-pane Markdown editor. You type Markdown on the left and see the rendered post on the right, with a live word count. It is the writing tool for this blog.

## Start the editor

From this directory:

```sh
make serve
```

Then open [http://127.0.0.1:8000/blargl/](http://127.0.0.1:8000/blargl/).

The homepage of the blog is [http://127.0.0.1:8000/](http://127.0.0.1:8000/). Leave the server running while you write.

## Write

1. **Title** — the headline. It becomes both the `<title>` of the local preview and the filename, with spaces turned into underscores. `A New Home` saves as `posts/A_New_Home.md`, previews locally at `/A_New_Home.html`, and publishes through Sky at `https://isaacjennings.org/blog/a-new-home`.
2. **Date** — `YYYY-MM-DD`, defaulting to today. The index lists posts newest first. A date in the future is treated as unpublished until that day.
3. **Left pane** — the Markdown body. Do not put the title in as a `# heading`; the site template already renders the title above the post.
4. **Right pane** — the local Markdown preview. The published page uses Sky's primary UI and typography.

Drafts autosave to the browser. Refreshing the tab does not lose work.

### Markdown that works

| You write | You get |
|---|---|
| blank-line-separated paragraphs | paragraphs |
| `*italics*` / `**bold**` | italics / bold |
| `[text](https://url)` | a link |
| `## Heading` | a section heading |
| `- item` / `1. item` | lists |
| `` `code` `` and fenced ` ``` ` blocks | inline and block code |
| `![alt](/assets/file.png)` | an image |
| `> quote` | a block quote |

For local previews, put image files in `assets/` and link them as `/assets/filename.png`. For production, upload images through Sky and use the returned URL; the post publisher does not sync local assets.

## Publish locally

Click **Save post**, or press ⌘S (Mac) / Ctrl+S (Windows/Linux).

On localhost that:

1. Writes `posts/Your_Title.md` with YAML frontmatter
2. Runs the static generator
3. Makes the post appear on the homepage and in `feed.rss`

Open the URL shown in the status bar (for example `/A_New_Home.html`) to read the generated page. Saving again with the same title overwrites the same file, which is how you edit.

The file on disk looks like this:

```markdown
---
title: "A New Home"
date: 2026-09-17
---

The first paragraph of the post…
```

You can also create or edit `posts/*.md` in any text editor and run `python3 publish.py`. blargl is optional; it is just the comfortable way to get that file written.

Use blargl locally; the production site is Sky, not the standalone static preview.

## Put it online

The public blog is [isaacjennings.org/blog](https://isaacjennings.org/blog), inside the Sky (sora-to-ki) site. `out/` is only a standalone local preview; **never rsync it to a production web root**.

Preview post changes without writing local files or changing the server:

```sh
make dry-run
```

Publish new and edited posts:

```sh
make publish
```

This copies published Markdown to `../sky/content/posts/`, upserts posts in the live Sky database on `root@home`, and clears Nitro's ISR cache. Future-dated posts are skipped. It does not delete posts or deploy frontend code. Override the SSH target with `HOST=user@server`.

### Build or deploy Sky UI changes

`make build` builds the Sky frontend into `../sky/.output/`, strips source maps, recompresses assets, and updates the Nitro asset manifest. It requires the Node/pnpm versions declared in `../sky/package.json`; it does not publish posts.

```sh
make build
```

Use **Blog — Deploy frontend to home** only for reviewed Sky UI changes. It builds the frontend, tags a rollback image, and recreates the frontend container. Routine post publishing only needs `make dry-run` and `make publish`.

For the old standalone preview generator, use `make static-build`. Saving in blargl still rebuilds that local preview.

### Warp workflows

The local definitions in `~/.warp/workflows/` use these commands:

- **Blog — Build site:** `make -C ~/Documents/isaacjennings.org/blog build`
- **Blog — Deploy dry run:** `make -C ~/Documents/isaacjennings.org/blog dry-run`
- **Blog — Publish to home:** `make -C ~/Documents/isaacjennings.org/blog publish`
- **Blog — Write (blargl editor):** keep using the local editor; save previews locally, then publish with the command above.

Synced Warp Drive workflows are separate from local YAML definitions. Edit any saved Build, Dry run, or Publish workflow to use the commands above. Remove the old `rsync .../out/ ...` publish command; it bypasses Sky. The retired blog subdomain redirects to the main site.

### Checklist

- [ ] Title and date filled in
- [ ] Body written and previewed in the right pane
- [ ] Production images uploaded through Sky; local `assets/` are not synced by the post publisher
- [ ] Saved from blargl (or `python3 publish.py` after a manual edit)
- [ ] Checked the post at `http://127.0.0.1:8000/Your_Title.html`
- [ ] Reviewed `make dry-run` and published with `make publish`
- [ ] Checked `https://isaacjennings.org/blog/your-title`
