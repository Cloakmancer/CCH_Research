# Publishing the notes to GitHub Pages

One-time setup, then every future publish is `git push`.

Windows paths assume the project is at `E:\Project\CCH_Research`. Use PowerShell.

---

## How it works

You keep editing notes in `Claude outputs/` exactly as now. Nothing about the existing
workflow changes.

```
Claude outputs/*.md          ← you edit these (the only files you touch)
        │
        │  tools/sync_docs.py   copies them under clean URL-safe names,
        │                       rewrites GitHub-style anchors to MkDocs form
        ▼
docs/                        ← generated, git-ignored, never edit
        │
        │  mkdocs build        (runs automatically on GitHub)
        ▼
site/                        ← generated, git-ignored
        │
        ▼
https://USERNAME.github.io/REPONAME/
```

`1.ProjectStatud.md` and all PDFs are deliberately not published. To publish something new,
add one line to `MARKDOWN_MAP` in `tools/sync_docs.py` and one entry to `nav:` in `mkdocs.yml`.

---

## Step 1 — Check Git

```powershell
git --version
```

If that errors, install **Git for Windows** from <https://git-scm.com/download/win>. Accept the
defaults; they include Git Credential Manager, which handles GitHub login through your browser
so you never deal with tokens by hand.

Then set your identity once:

```powershell
git config --global user.name  "Ashutosh"
git config --global user.email "ashuadhi10962@gmail.com"
```

---

## Step 2 — Create the repository on GitHub

On <https://github.com/new>:

- **Repository name:** `CCH_Research` (or anything; remember it as `REPONAME`)
- **Public**
- **Do not** tick "Add a README", ".gitignore" or "license" — the repo must be empty, otherwise
  the first push conflicts

---

## Step 3 — Point the config at your repo

Open `mkdocs.yml` and replace `USERNAME` and `REPONAME` on the `site_url` and `repo_url` lines
with your GitHub username and the repository name.

---

## Step 4 — First push

```powershell
cd E:\Project\CCH_Research
git init -b main
git add .
git status          # check the list: no .pdf, no docs/, no site/
git commit -m "Add research notes and MkDocs site"
git remote add origin https://github.com/USERNAME/REPONAME.git
git push -u origin main
```

A browser window will open for GitHub login on the first push.

`git status` should show roughly 20 files. If you see `CCH chat webprint.pdf` or a `docs/`
folder listed, stop — `.gitignore` is not being applied, and pushing a 22 MB binary into Git
history is not easily undone.

---

## Step 5 — Turn on Pages

In the repository on GitHub: **Settings → Pages → Build and deployment → Source**, choose
**GitHub Actions**. Not "Deploy from a branch" — the included workflow uses the Actions path.

Then go to the **Actions** tab. The build starts automatically and takes about a minute. When
it goes green, the site is at:

```
https://USERNAME.github.io/REPONAME/
```

Bookmark it on your phone. It works offline-ish once loaded and is fully searchable.

---

## Everyday use

Edit notes as usual, then:

```powershell
cd E:\Project\CCH_Research
git add .
git commit -m "Update revision notes"
git push
```

The site rebuilds itself within a minute or two. There is nothing else to run.

---

## Optional — preview locally before pushing

Worth doing the first time, so you see the site before it is public.

```powershell
E:\1.MINICONDA\python.exe -m pip install -r requirements-docs.txt
E:\1.MINICONDA\python.exe tools\sync_docs.py
E:\1.MINICONDA\python.exe -m mkdocs serve
```

Open <http://127.0.0.1:8000>. It live-reloads when you re-run the sync script. `Ctrl+C` to stop.

---

## Things worth knowing

**Public means public.** GitHub Pages on a free or Pro account is world-readable even from a
private repository. Before pushing anything new, check it contains no unpublished results,
supervisor correspondence, or licence-restricted data. Once pushed, assume it is permanent —
deleting a file does not remove it from Git history.

**PDFs are excluded** by `.gitignore`. They stay on your machine only, so they are not backed
up by this. Keep your own copy.

**Adding a page** takes two edits: `MARKDOWN_MAP` in `tools/sync_docs.py`, and `nav:` in
`mkdocs.yml`. Miss the second and the page still builds but is unreachable from the menu —
`--strict` will not catch that.

**If the Actions build fails**, open the failed run and read the red step. The usual causes are
a broken internal link (the build runs `--strict`, so a bad link is a hard error) and a file
listed in `MARKDOWN_MAP` that has been renamed.

**Maths.** KaTeX is enabled, so `$...$` and `$$...$$` render as LaTeX in any note you write
from now on. Existing notes use plain-text unicode symbols in indented blocks; those render
as-is and are unaffected.
