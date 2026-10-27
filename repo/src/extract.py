"""Extract every <img alt=""> from data/raw/*.html into data/candidates.csv.
You then fill the `label` column by hand: 'decorative' or 'meaningful'
(use the W3C WAI Decorative Images criteria: https://www.w3.org/WAI/tutorials/images/decorative/).
Usage: python src/extract.py [raw_dir] [out_csv]
"""
import sys, re, csv, pathlib
from html import escape
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

FIELDS = ["site", "img_index", "src", "label",
          "name_decor_words", "name_content_words", "has_width_height", "area", "aspect_ratio",
          "in_link", "link_has_text", "aria_hidden", "role_presentation", "parent_tag",
          "text_len_nearby", "is_svg_or_icon_ext", "has_title", "has_figcaption"]
DECOR = re.compile(r"(divider|spacer|separator|bg|background|border|line|icon|arrow|bullet|sprite|pixel|shadow|corner|dot|deco|ornament)", re.I)
CONTENT = re.compile(r"(photo|team|person|portrait|product|hero|banner|screenshot|chart|graph|logo|headshot|gallery|cover|map)", re.I)

def num(v):
    try: return float(re.sub(r"[^\d.]", "", str(v)))
    except Exception: return 0.0

def features(img, idx, site):
    src = img.get("src", "") or ""
    fname = src.split("?")[0].rsplit("/", 1)[-1]
    w, h = num(img.get("width")), num(img.get("height"))
    a = img.find_parent("a")
    parent = img.parent.name if img.parent else ""
    nearby = (img.parent.get_text(" ", strip=True) if img.parent else "")
    return {
        "site": site, "img_index": idx, "src": src, "label": "",
        "name_decor_words": int(bool(DECOR.search(fname))),
        "name_content_words": int(bool(CONTENT.search(fname))),
        "has_width_height": int(w > 0 and h > 0),
        "area": w * h, "aspect_ratio": (w / h) if h else 0.0,
        "in_link": int(a is not None),
        "link_has_text": int(bool(a and a.get_text(strip=True))),
        "aria_hidden": int(img.get("aria-hidden") == "true"),
        "role_presentation": int(img.get("role") in ("presentation", "none")),
        "parent_tag": parent,
        "text_len_nearby": len(nearby),
        "is_svg_or_icon_ext": int(bool(re.search(r"\.(svg|ico)$", fname, re.I))),
        "has_title": int(bool(img.get("title"))),
        "has_figcaption": int(img.find_parent("figure") is not None and
                              img.find_parent("figure").find("figcaption") is not None),
    }

def write_label_sheet(rows, sheet_path, log_path):
    base_urls = {}
    if log_path.exists():
        for line in log_path.read_text(encoding="utf-8").splitlines():
            try:
                url, status = line.split("\t", 1)
            except ValueError:
                continue
            if status.startswith("ok "):
                site = urlparse(url).netloc.replace(":", "_")
                base_urls[site] = url

    cards = []
    for row_number, row in enumerate(rows, start=1):
        site = escape(row["site"])
        raw_src = row["src"].strip()
        if raw_src:
            image_url = urljoin(base_urls.get(row["site"], ""), raw_src)
            src = escape(image_url, quote=True)
            preview = (
                f'<a href="{src}" target="_blank" rel="noreferrer">'
                f'<img src="{src}" alt="Candidate image for CSV row {row_number}" '
                f'loading="lazy"></a>'
            )
        else:
            preview = '<div class="missing">No image source</div>'
        cards.append(
            f'<article>{preview}<p><strong>CSV row {row_number}</strong> '
            f'| {site} | page image index {row["img_index"]}</p></article>'
        )

    document = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Image candidate label sheet</title>
<style>
body { margin: 0; padding: 1rem; color: #222; font: 16px/1.45 sans-serif; }
h1 { font-size: 1.4rem; }
main { display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: 1rem; }
article { min-width: 0; border: 1px solid #bbb; padding: .75rem; }
article a { display: grid; place-items: center; height: 220px; background: #eee; }
img { max-width: 100%; max-height: 100%; object-fit: contain; }
p { margin: .6rem 0 0; overflow-wrap: anywhere; }
</style>
</head>
<body>
<h1>Image candidate label sheet</h1>
<main>
""" + "\n".join(cards) + """
</main>
</body>
</html>
"""
    sheet_path.write_text(document, encoding="utf-8")

def main(raw="data/raw", out="data/candidates.csv"):
    rows = []
    for p in sorted(pathlib.Path(raw).glob("*.html")):
        soup = BeautifulSoup(p.read_bytes(), "html.parser")
        for i, img in enumerate(soup.find_all("img")):
            if img.get("alt") is not None and img.get("alt").strip() == "":
                rows.append(features(img, i, p.stem))
    with open(out, "w", newline="") as f:
        wr = csv.DictWriter(f, fieldnames=FIELDS); wr.writeheader(); wr.writerows(rows)
    print(f"{len(rows)} empty-alt images from {len(set(r['site'] for r in rows))} sites -> {out}")
    out_path = pathlib.Path(out)
    sheet_path = out_path.with_name("label_sheet.html")
    log_path = pathlib.Path(raw).parent / "collection_log.tsv"
    write_label_sheet(rows, sheet_path, log_path)
    print(f"Label sheet -> {sheet_path}")

if __name__ == "__main__":
    main(*sys.argv[1:])
