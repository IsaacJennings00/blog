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

1. **Title** — the headline. It becomes both the `<title>` of the page and the filename, with spaces turned into underscores. `A New Home` saves as `posts/A_New_Home.md` and publishes at `/A_New_Home.html`.
2. **Date** — `YYYY-MM-DD`, defaulting to today. The index lists posts newest first. A date in the future is treated as unpublished until that day.
3. **Left pane** — the Markdown body. Do not put the title in as a `# heading`; the site template already renders the title above the post.
4. **Right pane** — the live preview. This is the same Charter typesetting the published post uses.

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

Put image files in `assets/` before you save, then link them as `/assets/filename.png`.

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

If you open `/blargl/` on the live site instead of localhost, Save cannot write to disk (there is no server API in production). It downloads the `.md` file instead. Move that file into `posts/` on your machine and run `python3 publish.py`.

## Put it online

`out/` is the whole website. After a save, deploy that folder to whatever hosts [blog.isaacjennings.org](https://blog.isaacjennings.org).

If GitHub Pages is connected to this repo, pushing the new `posts/*.md` to `main` is enough: the deploy workflow builds `out/` and publishes it.

### Checklist

- [ ] Title and date filled in
- [ ] Body written and previewed in the right pane
- [ ] Images in `assets/` and linked as `/assets/…`
- [ ] Saved from blargl (or `python3 publish.py` after a manual edit)
- [ ] Checked the post at `http://127.0.0.1:8000/Your_Title.html`
- [ ] Deployed `out/` (or pushed to `main`)
