#!/usr/bin/env python3
"""Extract publicly published booking links from text or a URL.

Usage:
    python3 extract_booking_links.py <file-or-url> [--check] [--json]

Reads a local file, a URL, or stdin ("-"), then prints every booking link it
finds, classified by platform. HTML entities are unescaped first, because many
APIs (e.g. Hacker News) store links as
`https:&#x2F;&#x2F;calendly.com&#x2F;<handle>&#x2F;<slug>` and a naive regex
finds zero.

--check also does a low-effort HTTP status check on each unique link.
Stdlib only, so it runs anywhere.
"""
import argparse
import html
import json
import re
import ssl
import sys
import urllib.request

# Ordered so more specific patterns win before the bare-domain ones.
PATTERNS = [
    ("calendly",       r"calendly\.com/(?P<h>[A-Za-z0-9._%+-]+)(?:/(?P<s>[A-Za-z0-9._%+-]+))?"),
    ("cal.com",        r"(?<![\w.])cal\.com/@?(?P<h>[A-Za-z0-9._%+-]+)(?:/(?P<s>[A-Za-z0-9._%+-]+))?"),
    ("google-appt",    r"calendar\.app\.google/(?P<h>[A-Za-z0-9_-]+)(?:/(?P<s>[A-Za-z0-9_-]+))?"),
    ("google-sched",   r"calendar\.google\.com/calendar/appointments/schedules/(?P<h>[A-Za-z0-9_-]+)"),
    ("savvycal",       r"savvycal\.com/(?P<h>[A-Za-z0-9._%+-]+)(?:/(?P<s>[A-Za-z0-9._%+-]+))?"),
    ("topmate",        r"topmate\.io/(?P<h>[A-Za-z0-9._%+-]+)"),
    ("clarity",        r"clarity\.fm/(?P<h>[A-Za-z0-9._%+-]+)"),
    ("tempi",          r"meettempi\.com/(?P<h>[A-Za-z0-9._%+-]+)(?:/(?P<s>[A-Za-z0-9._%+-]+))?"),
    ("clockwise",      r"getclockwise\.com/c/(?P<h>[A-Za-z0-9._%+-]+)(?:/(?P<s>[A-Za-z0-9._%+-]+))?"),
    ("booktime",       r"booktime\.xyz/(?:p/)?(?P<h>[A-Za-z0-9._%+-]+)"),
]
COMPILED = [(name, re.compile(rx, re.I)) for name, rx in PATTERNS]

# Domains/paths that are almost always noise (vendor docs, clones, blogs).
NOISE_SUBSTR = (
    "calendly.com/", "cal.com/blog", "cal.com/pricing", "cal.com/docs",
    "cal.com/enterprise", "cal.com/teams", "api-evangelist", "github.com/calendly",
    "producthunt", "/alternatives", "wikipedia", "grammar",
)
SELF_HOSTED = re.compile(r"https?://[^\s\"'<>)]+", re.I)
BOOKISH = re.compile(
    r"(\.coffee(?:[/?#]|$))|(//coffee\.[\w.-]+)|(/coffee(?:[/?#]|$))"
    r"|(/book[\w-]*(?:[/?#]|$))|(/chat(?:[/?#]|$))|(/mycal(?:[/?#]|$))",
    re.I,
)


def fetch(url: str, timeout: int = 20) -> str:
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:
        raw = r.read()
    try:
        return raw.decode("utf-8", "replace")
    except Exception:
        return raw.decode("latin-1", "replace")


def load(src: str) -> str:
    if src == "-":
        return sys.stdin.read()
    if re.match(r"^https?://", src):
        return fetch(src)
    with open(src, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def extract(text: str):
    text = html.unescape(text)  # critical for HN-style entity-encoded URLs
    rows = {}
    for name, rx in COMPILED:
        for m in rx.finditer(text):
            h = m.group("h")
            if h.lower() in ("www", "blog", "pricing", "docs", "enterprise", "teams"):
                continue
            url = m.group(0).rstrip(").,;\"'")
            if any(n in url.lower() for n in ("cal.com/blog", "cal.com/pricing", "cal.com/docs")):
                continue
            s = m.groupdict().get("s")
            rows[url] = {"url": url, "platform": name, "handle": h, "slug": s}
    for m in SELF_HOSTED.finditer(text):
        url = m.group(0).rstrip(").,;\"'")
        if not BOOKISH.search(url):
            continue
        if any(n in url.lower() for n in NOISE_SUBSTR):
            continue
        rows.setdefault(url, {"url": url, "platform": "self-hosted", "handle": None, "slug": None})
    return list(rows.values())


def check(url: str, timeout: int = 12) -> object:
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:
            return r.status
    except Exception as e:  # noqa: BLE001
        return getattr(e, "code", "ERR")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("source", help="file path, URL, or '-' for stdin")
    ap.add_argument("--check", action="store_true", help="HTTP status-check each link")
    ap.add_argument("--json", action="store_true", help="emit JSON instead of a table")
    args = ap.parse_args()

    rows = extract(load(args.source))
    if args.check:
        for r in rows:
            r["status"] = check(r["url"])

    if args.json:
        print(json.dumps(rows, indent=2))
        return
    if not rows:
        print("no booking links found")
        return
    hdr = f"{'platform':13} {'handle':24} {'url'}"
    print(hdr)
    print("-" * len(hdr))
    for r in sorted(rows, key=lambda x: (x["platform"], x["url"])):
        status = f"  [{r['status']}]" if args.check else ""
        print(f"{r['platform']:13} {str(r['handle']):24} {r['url']}{status}")


if __name__ == "__main__":
    main()
