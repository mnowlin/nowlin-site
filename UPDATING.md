# Updating Your Website

Everything on the site is plain text. You can edit files directly on GitHub (click the file, then the pencil icon), commit, and the site rebuilds and goes live automatically in about two minutes. You never need to run anything on your own computer — but if you want to preview locally, see the last section.

## Before you publish: things to check once

1. **Homepage intro** — `content/_index.md`, the `intro:` line. It is a draft written for the new site; rewrite it in your own words (third person, 2–4 sentences).
2. **People page links** — the People page is **built automatically from the co-authors on your publications**, and its links were **found by web search**. Search can match the wrong person or an outdated page. Please open `data/coauthors.json` and check every entry; fix or delete anything wrong, and add links for anyone listed without one.
3. **Hidden notes** — search the `content/` folder for `NOTE FOR MATT`. Each note flags a place where your C.V. and BibTeX disagreed (volume numbers, a year, two typos). These notes never appear on the site.

## Add a new publication

1. On GitHub, open `content/publication/` and choose **Add file → Create new file**.
2. Name it `a-short-slug/index.md` (lowercase words joined by hyphens). **The folder name becomes the permanent web address** — `matthewcnowlin.com/publication/a-short-slug/` — so never rename it later.
3. Paste and fill in:

```yaml
---
title: "Full Title of the Paper"
date: 2026-03-01
authors: ["Matthew C. Nowlin", "Co-Author Name"]
publication_types: ["journal_article"]   # or book, chapter, conference_paper, book_review
publication: "Journal Name, 12(3): 45–67"
abstract: "Paste the abstract here."
doi: "10.1234/abcd"
links:
  - name: "Publisher's Version"
    url: "https://doi.org/10.1234/abcd"
tags: ["climate-energy"]   # research-area ids, see below
featured: false            # true = shown first on the homepage under its research areas
---
```

For a forthcoming paper add `status: forthcoming` and put “Forthcoming” at the end of `publication:`.

That's all. The paper appears on the Writings page, on its research areas on the homepage, in search, and in "See Also" on related pages — automatically.

**Research-area ids:** `policy-process`, `cultural-theory`, `climate-energy`, `nuclear`, `hazards`, `deliberation`, `governance`, `methods`. To also place a paper inside a sub-group of Theories of the Policy Process, add its folder name to the right `items` list in `data/research_areas.json`.

**Optional extras:**
- **Cover image:** upload `featured.jpg` into the paper's folder. If it is a publisher's image, add `image_credit: "Cover image from Publisher Name"`.
- **PDF:** upload the PDF to `static/files/`, then add a link `- name: "Article (PDF)"` with `url: "files/your-file.pdf"` (no leading slash).
- **Pin related work:** `related_papers: ["other-slug", "another-slug"]` puts those first under See Also.
- **Replication data:** `dataverse_url: "https://doi.org/10.7910/DVN/XXXX"` adds a Dataset link under See Also.

## Add a talk

Create `content/talk/a-short-slug/index.md`:

```yaml
---
title: "Talk Title"
date: 2026-04-01
authors: ["Matthew C. Nowlin"]
publication_types: ["presentation"]
event: "Host institution or event name"
location: "City, ST"
publication: "Host institution or event name, City, ST"
tags: ["climate-energy"]
---
```

It appears under the **Presentations** tab on the Writings page.

## Update your bio, C.V., teaching, or contact details

- **Bio & C.V. page:** `content/bio/index.md`
- **C.V. PDF:** after saving a new `nowlin-cv/nowlin-cv-short.pdf` (next to this repo in `04-RESOURCES`), run `bash scripts/sync-cv.sh` from the repo. It copies the PDF to `static/files/`, commits, and pushes (same filename keeps every link working). `scripts/com.nowlin.cv-sync.plist` can run this automatically via launchd, but only if `/bin/bash` has Full Disk Access, since background jobs can't read OneDrive otherwise.
- **Teaching:** `content/teaching/index.md`; upload syllabi to `static/files/`.
- **Contact page:** `content/contact/index.md`
- **Name, title, institution, email, profile links (header, footer, homepage):** the `owner:` block at the top of `hugo.yaml`.
- **Photo:** replace `static/images/matthew-nowlin.jpg` (a square image, about 480×480).

## Add or fix a person on the People page

People are discovered automatically from author lists — you don't add them by hand. To give someone a link, add a line to `data/coauthors.json`, using their name **exactly** as it appears in your publications:

```json
"Jane Doe": { "url": "https://janedoe.org", "type": "website" }
```

Prefer their own website, then their university page, then LinkedIn.

## Short links and redirects

`data/redirects.yaml` lists short addresses that forward elsewhere (for example `/vita` → `/bio/`). Add a `from:` / `to:` pair to create another. Old addresses from your previous site (`/publications.html`, `/teaching.html`, and so on) already forward to the new pages.

## Site options

In `hugo.yaml` under `mysite:`:
- `credit: false` — set to `true` to show a small “Created using GaryKing.org/mysite” line in the footer.
- `discovery: true` — an invisible line in the page source plus standard structured data for search engines. Set to `false` to remove.

## Going live (one time)

The site is hosted on **Netlify**. Every push to `main` on GitHub triggers a Netlify build, configured by `netlify.toml`.

## Previewing on your own computer (optional)

Install [Hugo extended](https://gohugo.io/installation/) (0.148.2 or newer; on a Mac, `brew install hugo`) and [Node.js](https://nodejs.org/), then in this folder run:

```
npm install
hugo server
```

and open <http://localhost:1313>. (Site search only works after a full build: `npm run build`, then serve the `public/` folder.)
