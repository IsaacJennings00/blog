# Isaac's Blog

A static blog for [blog.isaacjennings.org](https://blog.isaacjennings.org).
The generator, layout, and editor are adapted from [Veit Heller's blog](https://github.com/hellerve/blog).

Posts are Markdown files. `publish.py` turns them into HTML, an index, and an RSS feed. [blargl](blargl/) is the split-pane Markdown editor used to write and save those files.

## First-time setup

You need Python 3 and [pandoc](https://pandoc.org):

```sh
brew install pandoc
make setup
```

## Preview locally

```sh
make serve
```

- Blog: http://127.0.0.1:8000/
- Editor: http://127.0.0.1:8000/blargl/

That builds the site into `out/` and serves it. Saving from the editor writes a file to `posts/` and rebuilds.

To build without serving: `make build` (or `python3 publish.py` inside the virtualenv).

The finished site is the `out/` folder. That is what you deploy.

## Writing a post

See [PUBLISHING.md](PUBLISHING.md) for the editor workflow. In short:

1. Open `/blargl/`
2. Give the post a title and write Markdown in the left pane
3. Save (the button, or ⌘S / Ctrl+S)
4. Deploy `out/`

Images go in `assets/` and are referenced as `/assets/your-file.png`.

## Deploying to blog.isaacjennings.org

`out/` is a plain static site. Point the `blog.isaacjennings.org` DNS record at whatever hosts that folder (GitHub Pages, Cloudflare Pages, Netlify, or a plain nginx/Caddy server).

If this repo is on GitHub with Pages enabled, `.github/workflows/deploy.yml` builds with pandoc and publishes `out/` on every push to `main`. Add a CNAME (or ALIAS/ANAME) for `blog` to the Pages hostname, and GitHub will pick up the `CNAME` file already in this repo.

## Layout of this repo

```
posts/           Markdown source, one file per post
assets/          images and files linked from posts
blargl/          the Markdown editor
publish.py       static site generator
serve.py         local preview + save-from-editor
layout.html      template for a single post
index_layout.html  template for the homepage
feed_tpl.rss     RSS template
style.css        post styles (Charter, same system as the original)
out/             generated site (not committed)
```

Post filenames become URLs: `posts/Going_Static.md` publishes at `/Going_Static.html`.
