# Website Principles — matthewcnowlin.com

Architecture playbook for anyone (human or AI) maintaining this site. Built from the GaryKing.org/mysite build instructions; visual model is gking.harvard.edu.

## Stack

- **Hugo extended 0.148.2+** (Hugo Blox 0.10 refuses older versions) with **Hugo Blox `blox-tailwind` v0.10.0** as a Go module, vendored in `_vendor/` (committed) so builds are hermetic and theme templates can be copied for overrides.
- **Tailwind v4** via Hugo's native `css.TailwindCSS`; needs `@tailwindcss/cli` and `@tailwindcss/typography` from `package.json`. All project styling lives in `assets/css/custom.css`, loaded after Tailwind; layouts use project-specific semantic classes rather than Tailwind utilities.
- **Pagefind** builds the search index after Hugo (`npx pagefind --site public`). `<main>` carries `data-pagefind-body`, so the navbar/footer aren't indexed.
- **Deployment:** `.github/workflows/deploy.yml` (GitHub Pages) or `netlify.toml` (Netlify, the current host). Both run `npm ci → hugo --gc --minify → pagefind`.
- `baseURL` is the final `https://matthewcnowlin.com/` in `hugo.yaml` and is **not** overridden in CI (configure-pages can emit `http://`, poisoning canonicals and the sitemap).

## Overrides

Overrides of theme partials go in `layouts/_partials/...` (Blox uses `_partials`, not `partials`). Project layouts:

| File | Role |
|---|---|
| `layouts/baseof.html` | Shell: skip link, navbar, `<main>`, footer, search modal. Still calls Blox's `site_head` (Tailwind, OG tags, JS bundle). |
| `_partials/components/headers/navbar.html` | Institution bar + brand (owner's name, uppercase, links home) + right-aligned nav + icon-only search + mobile hamburger. Keeps class `page-header` because Blox's `hb-nav.js` measures it. |
| `_partials/components/search-modal.html` | Vanilla-JS Pagefind modal; `import('{{ "pagefind/pagefind.js" \| relURL }}')`, loaded on first open; Cmd/Ctrl-K, `/`, Esc, arrows; Google `site:` fallback. |
| `_partials/site_footer.html` | Dark footer; mysite credit gated by `params.mysite.credit`. |
| `_partials/hooks/head-end/mysite.html` | Favicons; generator meta + homepage Person JSON-LD (gated by `params.mysite.discovery`); scholarly metadata on publication/talk pages. |
| `_partials/scholarly_meta.html` | Google Scholar `citation_*` tags + ScholarlyArticle/Book/CreativeWork JSON-LD. |
| `_partials/related_finder.html` | "See Also" algorithm (below). |
| `_partials/citation_line.html`, `author_list.html`, `page_links_row.html`, `bibtex.html` | One rendering of a citation, reused everywhere (homepage, Writings, detail pages). |
| `home.html`, `landing/list.html` → `_partials/homepage.html` | Hero (photo left, text right; stacked ≤640px) + research-area accordions (`<details>`; 5 items each, featured first, then "View all N →" to the filtered Writings page). |
| `publication/list.html` | Writings page (below). |
| `publication/single.html`, `talk/single.html` → `_partials/item_single.html` | Detail page: breadcrumbs, title, authors (co-authors linked via `data/coauthors.json`), year · venue, link chips, Cite/BibTeX, abstract (`#abstract`), body, See Also. **Never shows the publication_types label.** |
| `authors/list.html` | People page — names-only, alphabetized by last name, auto-discovered from all `authors:` fields. |
| `_default/single.html` | Bio, Teaching, Contact (`show_photo: true` adds the portrait). |
| `redirect/single.html` + `content/_content.gotmpl` | Meta-refresh redirect pages generated from `data/redirects.yaml`. |
| `robots.txt`, `404.html`, `shortcodes/staticrel.html` | As named. |

## Content model

- Every item is a directory with `index.md`; **the directory name is the permanent slug** (`permalinks: :contentbasename`). Never rename once live.
- Publications: `content/publication/<slug>/`; talks: `content/talk/<slug>/`. Shared front matter: `title, date, authors, publication_types, publication (venue string), abstract, doi, links, tags (research-area ids), featured, status`.
- `publication_types` vocabulary used here: `journal_article, book, chapter, conference_paper, book_review, presentation`.
- Writings tabs come from `data/writings_legacy_map.json` (slug → tab, preserving the legacy site's categories: Books, Journal Articles, Book Chapters, Refereed Conference Proceedings, Book Reviews, Open-Source Educational Resources), falling back to `publication_types` (`functions/tab_of.html`). Talks are the Presentations tab.
- `data/research_areas.json` drives the homepage accordions, the Writings research-area filter, and See Also siblings. Item membership is `tags:` on each page; `items`/`subcategories` lists in the JSON are used for sibling detection.
- Migration metadata stays in `data/`, never in front matter. `scripts/import_bib.py` was the one-time importer from the legacy `pubs.bib` + C.V.; don't re-run it over edited content.
- Taxonomy pages are disabled (`disableKinds: [taxonomy, term]`); `tags` still work as front-matter data. The `author` taxonomy is deliberately not used (it renders name+count walls).

## Writings page

Server-renders every item (crawlable without JS). Each `<li class="pub-item">` carries `data-tab`, `data-year`, `data-date`, `data-title`, `data-types`, `data-areas`, `data-search`. One inline IIFE handles: tab clicks (all `.tab-btn`s have listeners; "All" resets), research-area select, year checkboxes, text search, sort, result count, BibTeX export of visible items, and hash state — `#tab`, `#all&area=<id>`, `&year=2021,2022`, `&q=text` — with `pushState` so Back works and filtered views are shareable. The hash is read on load.

## See Also algorithm (`related_finder.html`)

1. Explicit `related_papers / related_talks / related_software / related_datasets` (+ legacy singular) always win.
2. `see_also: [{url,title}]` or `[{slug}]`; `dataverse_url` (or a Dataverse DOI found in the abstract) → `[Dataset]` row.
3. Siblings in the same research-area subcategory (+10).
4. Scoring: +2 per shared title token (stop words and tokens <3 chars removed), +1 per shared co-author (exact or last-name match; **the site owner is excluded** since he is on every item), +2 per shared tag. Threshold 4, relaxed to 2 with fewer than 3 explicit picks.
5. Response/Comment/Reply/Rejoinder titles pin their subject; book editions with the same base title cross-link.
6. Sort by pin → score → year; dedupe by normalized title; cap 8. Labels: publication_types before section.

## Design rules

- Palette (custom.css tokens): warm off-white `#fbf9f6`, surfaces `#f4efe8/#ebe4da`, charcoal text `#2d2926`, muted `#66605a`, hairlines `#e2ddd5`, accent slate `#355f7d`, link `#2f5872`, **UTA blue `#0064b1` only for thin rules, active tab/nav underline, and link hover**, muted clay `#a5633f` for presentation labels. Focus ring gold `#d4a96a`. Always light mode.
- Dense one-line citations with hairline separators; no card grids. Abstracts expand inline (`<details>`). Consistent treatment: primary actions = filled/outlined `.btn`, per-item links = `.chip`.
- Sticky header scrolls the institution bar away and keeps the nav; anchors use `scroll-padding-top: nav height + 12px` (one mechanism only — stacking `scroll-margin` double-offsets).
- No visible process notes. Owner-facing flags live in HTML comments (`<!-- NOTE FOR MATT: … -->`).
- Homepage intro (third person, `content/_index.md`) and Bio text (owner's own first-person words, `content/bio/index.md`) must remain different texts.
- Favicon is an "MN" monogram on the accent colour (`static/favicon*`, `assets/media/icon.png`).

## Verification checklist after changes

`hugo --gc --minify` builds with no warnings; every Writings tab changes the list; Research Areas link lands just below the navbar; brand returns home; mobile (375px) has no horizontal scroll and the hamburger sits at the right; `curl` `/robots.txt`, `/sitemap.xml` (all `https://`), `/llms.txt`, and a publication page (contains `citation_title` and `application/ld+json`).
