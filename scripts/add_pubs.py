#!/usr/bin/env python3
"""Add new publications from Zotero to the site.

Pulls the "Publications" collection from Zotero (Better BibTeX's local export endpoint, so Zotero
must be open), then for each item:
  - already on the site (same DOI, Zotero key, or near-identical title): left alone, unless the
    page is marked forthcoming and Zotero now has the published details, in which case the page
    is updated in place (its web address stays the same);
  - not on the site: a new content/publication/<slug>/index.md is written, and the slug is added
    to the guessed research areas in data/research_areas.json.
PDFs dropped in pdf-inbox/ named <citation-key>.pdf or <slug>.pdf are moved to static/files/ and
linked from their page: "Article (PDF)" for a publication, "Slides (PDF)" for a talk in content/talk/.

Usually run through scripts/add-pubs.sh, which reviews, commits, and pushes.
  python3 scripts/add_pubs.py [--dry-run] [--file export.json] [--changed-list out.txt]
"""
import argparse, glob, json, os, re, shutil, sys, unicodedata, urllib.parse, urllib.request

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PUBDIR = os.path.join(SITE, "content", "publication")
TALKDIR = os.path.join(SITE, "content", "talk")
AREAS_JSON = os.path.join(SITE, "data", "research_areas.json")
INBOX = os.path.join(SITE, "pdf-inbox")
COLLECTION = "Publications"
EXPORT_URL = "http://127.0.0.1:23119/better-bibtex/export/collection?/1/{}.json"

TYPES = {"article-journal": "journal_article", "article": "journal_article", "chapter": "chapter",
         "book": "book", "paper-conference": "conference_paper", "review": "book_review",
         "review-book": "book_review", "manuscript": "working_paper"}

# Research-area guesses: a keyword in the title counts on its own; in the abstract it takes two hits.
AREA_KEYWORDS = {
    "policy-process": ["policy process", "advocacy coalition", "policy learning", "belief updating",
                       "beliefs updating", "policy change", "policy feedback", "implementation",
                       "information processing", "policy subsystem"],
    "cultural-theory": ["cultural theory", "cultural cognition", "worldview", "grid-group",
                        "egalitarian", "individualis", "hierarchi", "fatalis", "belief system"],
    "climate-energy": ["climate", "energy", "environmental", "sustainab", "public lands",
                       "natural resource", "renewable", "fossil"],
    "nuclear": ["nuclear", "radioactive", "yucca"],
    "hazards": ["hazard", "weather", "disaster", "tornado", "hurricane", "emergency", "flood"],
    "deliberation": ["deliberat", "mini-public", "citizens' assembl", "citizens’ assembl"],
    "governance": ["governance", "polycentric", "administrative", "bureaucra", "public administration",
                   "managerial", "collaborat", "public management"],
    "methods": ["methodolog", "text analysis", "quantitative methods", "measurement", "survey experiment"],
}

STOP = {"a", "an", "the", "of", "and", "in", "on", "for", "to", "by", "through", "with", "about", "as", "at"}


# ---------- text helpers

def clean(s):
    s = re.sub(r"<[^>]+>", "", s or "")
    return re.sub(r"\s+", " ", s).strip()

def norm(s):
    return re.sub(r"[^a-z0-9]", "", clean(s).lower())

def words(s):
    ws = re.findall(r"[a-z0-9]+", unicodedata.normalize("NFKD", clean(s).lower()))
    return {w.rstrip("s") for w in ws if w not in STOP}

def similar_titles(a, b):
    """Near-identical titles, or one a reworded subset of the other (overlap of significant words)."""
    if norm(a) == norm(b):
        return True
    wa, wb = words(a), words(b)
    if min(len(wa), len(wb)) < 3:
        return False
    return len(wa & wb) / min(len(wa), len(wb)) >= 0.8

def slugify(title):
    t = re.split(r"[:?.]", clean(title))[0]
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode().lower()
    ws = re.findall(r"[a-z0-9]+", t)
    return "-".join(ws[:10])

def q(s):
    return json.dumps(s, ensure_ascii=False)

def person(p):
    return clean(" ".join(x for x in (p.get("given"), p.get("family")) if x)) or clean(p.get("literal", ""))

def join_names(names):
    if len(names) <= 2:
        return " and ".join(names)
    return ", ".join(names[:-1]) + ", and " + names[-1]

def dash(pages):
    return re.sub(r"\s*[-–—]+\s*", "–", pages or "")


# ---------- existing site

def read_page(path):
    text = open(path, encoding="utf-8").read()
    m = re.match(r"---\n(.*?)\n---\n?(.*)", text, re.S)
    fm, body = (m.group(1), m.group(2)) if m else ("", text)
    def get(key):
        mm = re.search(rf"^{key}:\s*(.*)$", fm, re.M)
        if not mm:
            return None
        v = mm.group(1).strip()
        try:
            return json.loads(v)
        except ValueError:
            return v.strip('"')
    return dict(path=path, slug=os.path.basename(os.path.dirname(path)), fm=fm, body=body,
                title=get("title") or "", doi=(get("doi") or "").lower(), key=get("zotero_key"),
                status=get("status"), types=get("publication_types") or [], authors=get("authors") or [])

def existing_pages():
    return [read_page(p) for p in sorted(glob.glob(os.path.join(PUBDIR, "*", "index.md")))]

def author_aliases(pages):
    """Known author spellings by family name, so 'Thomas Rabovsky' maps to 'Thomas M. Rabovsky'."""
    by_family = {}
    for p in pages:
        for a in p["authors"]:
            by_family.setdefault(a.split()[-1].lower(), set()).add(a)
    return by_family

def canonical(name, by_family):
    parts = name.split()
    if len(parts) < 2:
        return name
    cands = by_family.get(parts[-1].lower(), set())
    if name in cands:
        return name
    first = parts[0].rstrip(".").lower()
    hits = [c for c in cands if c.split()[0].rstrip(".").lower() in (first, first[:1])
            or first == c.split()[0].rstrip(".").lower()[:1]]
    return hits[0] if len(hits) == 1 else name


# ---------- Zotero item -> page fields

def is_forthcoming(it):
    extra = " ".join(str(it.get(k, "")) for k in ("status", "note", "extra")).lower()
    if "forthcoming" in extra or "in press" in extra:
        return True
    if it["type"] in ("article-journal", "article", "review", "review-book"):
        return not it.get("volume")
    if it["type"] == "chapter":
        return not it.get("page")
    return False

def fields(it, by_family):
    ptype = TYPES[it["type"]]
    title = clean(it["title"])
    # Book reviews come through as articles titled "Book Title. By Author. Place: Press, Year. 260p."
    m = re.match(r"(.+?)\.\s+By\s+[A-Z]", title)
    if m and ptype == "journal_article":
        ptype, title = "book_review", m.group(1)

    forthcoming = is_forthcoming(it)
    container = clean(it.get("container-title", ""))
    pages = dash(it.get("page", ""))
    if re.fullmatch(r"\d{9,}", pages):          # OnlineFirst placeholders such as 02750740261478906
        pages = ""
    if ptype in ("journal_article", "book_review"):
        if forthcoming:
            pub = f"{container}, Forthcoming"
        else:
            pub = container + ", " + it["volume"] + (f"({it['issue']})" if it.get("issue") else "") + (f": {pages}" if pages else "")
    elif ptype == "chapter":
        eds = [person(e) for e in it.get("editor", [])]
        pub = "In " + container
        if eds:
            pub += (", eds. " if len(eds) > 1 else ", ed. ") + join_names(eds)
        pub += ". " + clean(it.get("publisher", ""))
        pub += ", Forthcoming" if forthcoming else (f", {pages}" if pages else "")
    elif ptype == "working_paper":
        pub = container or "Working paper"
    elif ptype == "book":
        pub = ": ".join(x for x in (clean(it.get("publisher-place", "")), clean(it.get("publisher", ""))) if x)
    else:  # conference_paper
        pub = "In " + container + (f", {pages}" if pages else "") + (f". {clean(it['publisher'])}" if it.get("publisher") else "")
    pub = pub.strip(" ,.")

    y, mo, d = (list(it.get("issued", {}).get("date-parts", [[]])[0]) + [1, 1, 1])[:3]
    doi = clean(it.get("DOI", ""))
    url = f"https://doi.org/{doi}" if doi else clean(it.get("URL", ""))
    text = (title + " " + container).lower()
    abstract = clean(it.get("abstract", ""))
    areas = [a for a, kws in AREA_KEYWORDS.items()
             if any(k in text for k in kws) or sum(abstract.lower().count(k) for k in kws) >= 2]
    return dict(title=title, date=f"{int(y):04d}-{int(mo):02d}-{int(d):02d}",
                authors=[canonical(person(a), by_family) for a in it.get("author", [])],
                type=ptype, publication=pub, forthcoming=forthcoming, abstract=abstract,
                doi=doi, url=url, areas=areas, key=it["citation-key"])

def new_page(f):
    lines = ["---", f"title: {q(f['title'])}", f"date: {f['date']}",
             f"authors: {q(f['authors'])}", f"publication_types: {q([f['type']])}",
             f"publication: {q(f['publication'])}"]
    if f["forthcoming"]:
        lines.append("status: forthcoming")
    if f["abstract"]:
        lines.append(f"abstract: {q(f['abstract'])}")
    if f["doi"]:
        lines.append(f"doi: {q(f['doi'])}")
    if f["url"]:
        lines += ["links:", "  - name: \"Publisher's Version\"", f"    url: {q(f['url'])}"]
    lines += [f"tags: {q(f['areas'])}", "featured: false", f"zotero_key: {q(f['key'])}", "---", ""]
    return "\n".join(lines)


# ---------- editing existing front matter

def fm_blocks(fm):
    """Split front matter into [key, lines] blocks; indented/list lines stay with their key."""
    blocks = []
    for line in fm.split("\n"):
        m = re.match(r"([A-Za-z_]+):", line)
        if m or not blocks:
            blocks.append([m.group(1) if m else None, [line]])
        else:
            blocks[-1][1].append(line)
    return blocks

def set_block(blocks, key, lines, after=None):
    for b in blocks:
        if b[0] == key:
            b[1] = lines
            return
    idx = next((i + 1 for i, b in enumerate(blocks) if b[0] == after), len(blocks))
    blocks.insert(idx, [key, lines])

def update_forthcoming(page, f):
    blocks = [b for b in fm_blocks(page["fm"]) if b[0] != "status"]
    set_block(blocks, "title", [f"title: {q(f['title'])}"])
    set_block(blocks, "date", [f"date: {f['date']}"])
    set_block(blocks, "publication", [f"publication: {q(f['publication'])}"])
    have = {b[0] for b in blocks}
    if f["abstract"] and "abstract" not in have:
        set_block(blocks, "abstract", [f"abstract: {q(f['abstract'])}"], after="publication")
    if f["doi"] and "doi" not in have:
        set_block(blocks, "doi", [f"doi: {q(f['doi'])}"], after="abstract" if f["abstract"] else "publication")
    if f["url"] and "links" not in have:
        set_block(blocks, "links", ["links:", "  - name: \"Publisher's Version\"", f"    url: {q(f['url'])}"],
                  after="doi" if f["doi"] else "abstract" if f["abstract"] else "publication")
    if "zotero_key" not in have:
        set_block(blocks, "zotero_key", [f"zotero_key: {q(f['key'])}"])
    fm = "\n".join(l for b in blocks for l in b[1])
    return f"---\n{fm}\n---\n{page['body']}"

def add_link(path, name, url):
    page = read_page(path)
    if url in page["fm"]:
        return False
    blocks = fm_blocks(page["fm"])
    entry = [f"  - name: {q(name)}", f"    url: {q(url)}"]
    for b in blocks:
        if b[0] == "links":
            b[1] += entry
            break
    else:
        set_block(blocks, "links", ["links:"] + entry, after="doi")
    fm = "\n".join(l for b in blocks for l in b[1])
    open(path, "w", encoding="utf-8").write(f"---\n{fm}\n---\n{page['body']}")
    return True


# ---------- research_areas.json (edited as text to keep its hand formatting)

def add_to_area(text, area, slug):
    m = re.search(rf'"id":\s*"{re.escape(area)}"', text)
    if not m:
        return text
    start = text.index('"items": [', m.end()) + len('"items": [')
    end = text.index("]", start)
    inner = text[start:end]
    if f'"{slug}"' in inner:
        return text
    if inner.strip():
        indent = re.search(r"\n(\s*)\"", inner).group(1)
        new_inner = inner.rstrip() + f',\n{indent}"{slug}"' + inner[len(inner.rstrip()):]
    else:
        line_indent = re.search(r"\n(\s*)\"items\"", text[:start]).group(1)
        new_inner = f'\n{line_indent}  "{slug}"\n{line_indent}'
    return text[:start] + new_inner + text[end:]


# ---------- main

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="show what would change; write nothing")
    ap.add_argument("--file", help="read a Better CSL JSON export instead of asking Zotero")
    ap.add_argument("--changed-list", help="write the changed paths here, one per line")
    args = ap.parse_args()

    if args.file:
        items = json.load(open(args.file, encoding="utf-8"))
    else:
        try:
            with urllib.request.urlopen(EXPORT_URL.format(urllib.parse.quote(COLLECTION)), timeout=60) as r:
                items = json.load(r)
        except OSError as e:
            sys.exit(f"Could not reach Zotero ({e}). Open Zotero and try again.")

    pages = existing_pages()
    by_family = author_aliases(pages)
    known_people = set().union(*by_family.values()) if by_family else set()
    areas_text = open(AREAS_JSON, encoding="utf-8").read()
    changed, added, updated, notes = [], [], [], []
    slug_for_key = {}

    for it in items:
        if it.get("type") not in TYPES:
            notes.append(f"skipped (type '{it.get('type')}' not handled): {clean(it.get('title'))}")
            continue
        f = fields(it, by_family)
        doi = f["doi"].lower()
        match = next((p for p in pages if (doi and p["doi"] == doi) or p["key"] == f["key"]), None) \
            or next((p for p in pages if similar_titles(p["title"], f["title"])), None)

        if match:
            slug_for_key[f["key"]] = match["slug"]
            if match["status"] == "forthcoming" and not f["forthcoming"]:
                updated.append((match["slug"], match["title"], f))
                if not args.dry_run:
                    open(match["path"], "w", encoding="utf-8").write(update_forthcoming(match, f))
                changed.append(os.path.relpath(match["path"], SITE))
            continue

        slug = base = slugify(f["title"])
        n = 2
        while os.path.exists(os.path.join(PUBDIR, slug)) or slug in slug_for_key.values():
            slug, n = f"{base}-{n}", n + 1
        slug_for_key[f["key"]] = slug
        added.append((slug, f))
        path = os.path.join(PUBDIR, slug, "index.md")
        if not args.dry_run:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            open(path, "w", encoding="utf-8").write(new_page(f))
        changed.append(os.path.relpath(path, SITE))
        for a in f["areas"]:
            areas_text = add_to_area(areas_text, a, slug)
        for a in f["authors"]:
            if a not in known_people and a != "Matthew C. Nowlin":
                notes.append(f"new co-author (no link yet; add to data/coauthors.json if wanted): {a}")
                known_people.add(a)

    if added and not args.dry_run:
        open(AREAS_JSON, "w", encoding="utf-8").write(areas_text)
    if added:
        changed.append(os.path.relpath(AREAS_JSON, SITE))

    # PDFs waiting in the inbox: articles for publications, slides for talks
    attached = []
    for pdf in sorted(glob.glob(os.path.join(INBOX, "*.pdf"))):
        stem = os.path.splitext(os.path.basename(pdf))[0]
        slug = slug_for_key.get(stem) or (stem if os.path.isdir(os.path.join(PUBDIR, stem)) else None)
        if slug:
            page, fname, label = os.path.join(PUBDIR, slug, "index.md"), f"{slug}.pdf", "Article (PDF)"
        elif os.path.isdir(os.path.join(TALKDIR, stem)):
            slug = stem
            page, fname, label = os.path.join(TALKDIR, slug, "index.md"), f"{slug}-slides.pdf", "Slides (PDF)"
        else:
            notes.append(f"PDF not matched to a publication or talk (name it <citation-key>.pdf or <slug>.pdf): {os.path.basename(pdf)}")
            continue
        dest = os.path.join(SITE, "static", "files", fname)
        attached.append((os.path.basename(pdf), fname, slug))
        if not args.dry_run:
            shutil.move(pdf, dest)
            add_link(page, label, f"files/{fname}")
        changed += [os.path.relpath(dest, SITE), os.path.relpath(page, SITE)]

    # Report
    say = print
    if args.dry_run:
        say("DRY RUN: nothing was written.\n")
    for slug, f in added:
        say(f"NEW  {slug}/\n     {f['title']}\n     {f['publication']}"
            + ("  [forthcoming]" if f["forthcoming"] else "")
            + f"\n     research areas (guessed, please check): {', '.join(f['areas']) or 'none'}\n")
    for slug, old, f in updated:
        say(f"PUBLISHED (was forthcoming)  {slug}/\n     was: {old}\n     now: {f['title']}\n     {f['publication']}\n")
    for name, fname, slug in attached:
        say(f"PDF  {name} -> static/files/{fname}, linked from {slug}/")
    for n in notes:
        say("NOTE " + n)
    if not (added or updated or attached):
        say("No new publications: the site already matches Zotero.")

    if args.changed_list:
        open(args.changed_list, "w").write("\n".join(dict.fromkeys(changed)) + ("\n" if changed else ""))


if __name__ == "__main__":
    main()
