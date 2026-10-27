"""Download home pages listed in data/urls.txt (one URL per line).
Respects robots.txt and waits between requests. Saves HTML to data/raw/<site>.html
Run on YOUR machine (needs internet). Only public pages; do not log in or bypass blocks.
Usage: python src/collect.py data/urls.txt
"""
import sys, time, pathlib, urllib.request, urllib.robotparser
from urllib.parse import urlparse

UA = "ClearSiteResearchBot/0.1 (student course project)"
DELAY = 3.0

def allowed(url):
    p = urlparse(url)
    rp = urllib.robotparser.RobotFileParser()
    rp.set_url(f"{p.scheme}://{p.netloc}/robots.txt")
    try:
        rp.read()
    except Exception:
        return False  # cannot confirm permission: skip
    return rp.can_fetch(UA, url)

def main(path):
    out = pathlib.Path("data/raw"); out.mkdir(parents=True, exist_ok=True)
    log = []
    for url in [u.strip() for u in open(path) if u.strip() and not u.startswith("#")]:
        site = urlparse(url).netloc.replace(":", "_")
        if not allowed(url):
            log.append((url, "skipped: robots.txt")); print("skip", url); continue
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            html = urllib.request.urlopen(req, timeout=20).read()
            (out / f"{site}.html").write_bytes(html)
            log.append((url, f"ok {len(html)} bytes")); print("ok  ", url)
        except Exception as e:
            log.append((url, f"error: {e}")); print("err ", url, e)
        time.sleep(DELAY)
    with open("data/collection_log.tsv", "w") as f:
        for u, s in log: f.write(f"{u}\t{s}\n")

if __name__ == "__main__":
    main(sys.argv[1])
