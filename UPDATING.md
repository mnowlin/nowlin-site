# Updating Your Website

Everything on the site is plain text. You can edit files directly on GitHub (click the file, then the pencil icon), commit, and the site rebuilds and goes live automatically in about two minutes. You never need to run anything on your own computer — but if you want to preview locally, see the last section.

## Before you publish: things to check once

1. **Homepage intro** — `content/_index.md`, the `intro:` line. It is a draft written for the new site; rewrite it in your own words (third person, 2–4 sentences).
2. **People page links** — the People page is **built automatically from the co-authors on your publications**, and its links were **found by web search**. Search can match the wrong person or an outdated page. Please open `data/coauthors.json` and check every entry; fix or delete anything wrong, and add links for anyone listed without one.
3. **Hidden notes** — search the `content/` folder for `NOTE FOR MATT`. Each note flags a place where your C.V. and BibTeX disagreed (volume numbers, a year, two typos). These notes never appear on the site.

## Add a new publication

### From Zotero (the usual way)

1. Add the paper to your **Publications** collection in Zotero, with the abstract and DOI filled in. For a forthcoming paper, leave the volume empty or put `forthcoming` in Extra.
2. Optional: to offer a PDF, save it in `pdf-inbox/` (in this repo) as `<citation-key>.pdf`, the Better BibTeX key shown in Zotero.
3. With Zotero open, run `bash scripts/add-pubs.sh` from this folder.

The script adds a page for every item in the collection that isn't on the site yet. It skips papers that are already there, matching on DOI or title. When a paper marked forthcoming has come out (Zotero now has its volume or pages), the script updates that page in place and its web address stays the same. It prints what it did, guesses each new paper's research areas, and names any new co-authors. It publishes only when you answer `y`. If you answer no, the files stay in place, so you can fix the research areas (the `tags:` line and `data/research_areas.json`) or set `featured: true`, then commit and push.

### By hand

1. On GitHub, open `content/publication/` and choose **Add file → Create new file**.
2. Name it `a-short-slug/index.md` (lowercase words joined by hyphens). **The folder name becomes the permanent web address** — `matthewcnowlin.com/publication/a-short-slug/` — so never rename it later.
3. Paste and fill in:

```yaml
---
title: "Full Title of the Paper"
date: 2026-03-01
authors: ["Matthew C. Nowlin", "Co-Author Name"]
publication_types: ["journal_article"]   # or book, chapter, conference_paper, book_review, working_paper
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

For a working paper use `publication_types: ["working_paper"]` and put its status in `publication:` (e.g. “Working paper” or “Under review”); it appears under the **Working Papers** tab. A `doi:` is optional.

For a forthcoming paper add `status: forthcoming` and put “Forthcoming” at the end of `publication:`.

4. Add the folder name to the `items` list of each of its research areas in `data/research_areas.json`. `tags:` controls the Writings-page filter, while the homepage research areas read `items`.

The paper then appears on the Writings page, on its research areas on the homepage, in search, and in "See Also" on related pages.

**Research-area ids:** `policy-process`, `cultural-theory`, `climate-energy`, `nuclear`, `hazards`, `deliberation`, `governance`, `methods`. To also place a paper inside a sub-group of Theories of the Policy Process, add its folder name to the right subcategory `items` list in `data/research_areas.json`.

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

It appears under the **Presentations** tab on the Writings page. To place it under a research area on the homepage, also add its folder name to that area's `items` list in `data/research_areas.json`.

**Slides:** export the deck as a PDF, save it in `pdf-inbox/` as `<talk-folder-name>.pdf` (for example `beliefs-about-climate-change.pdf`), and run `bash scripts/add-pubs.sh`. The PDF is moved to `static/files/<talk-folder-name>-slides.pdf`, and a **Slides (PDF)** button is added to the talk's page.

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
