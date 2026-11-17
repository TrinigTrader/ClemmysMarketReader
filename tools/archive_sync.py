#!/usr/bin/env python3
"""Merge Edge Desk outputs into this repo's archive (the private research database).

Usage: python3 -I tools/archive_sync.py DB_DIR [PROJECT_FILES_DIR]
  DB_DIR             folder holding artifact-database exports: news/*.json, research/*.json, optsnap/*.json
  PROJECT_FILES_DIR  default /mnt/project-files (for edge-desk/uw and knowledge/claude)

Writes (relative to the repo root):
  archive/news/YYYY-MM/<id>.json        every news story, kept forever (the page prunes after 10 days)
  archive/research/<T>/<YYYY-MM-DD>.json finished deep dives, one version per day
  archive/optsnap/<T>/<YYYY-MM-DD>.json  nightly option-chain snapshots
  archive/uw/tickers/<YYYY-MM-DD>.json   daily snapshot of per-ticker Unusual Whales data
  archive/uw/congress-history.json       running congress-trade history (merged, never shrinks)
  archive/rescreen/<YYYY-MM-DD>.md       re-screen snapshot + thesis summary from the screener spec
  uw/, docs/                             latest copies of the collector data, specs and page source
  README.md                              regenerated "Archive log" section (Graphify reads only README.md)
Prints a one-line summary of what changed.
"""
import json, os, re, shutil, sys, glob, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A = os.path.join(ROOT, "archive")
LOG_START, LOG_END = "<!-- ARCHIVE-LOG:START -->", "<!-- ARCHIVE-LOG:END -->"


def load(p):
    try:
        with open(p) as f:
            return json.load(f)
    except Exception:
        return None


def write_json(p, obj):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    new = json.dumps(obj, indent=1, sort_keys=True, ensure_ascii=False) + "\n"
    if os.path.exists(p) and open(p).read() == new:
        return False
    open(p, "w").write(new)
    return True


def strip_meta(d):
    return {k: v for k, v in d.items() if not k.startswith("__") and k not in ("version",)}


def day(s):
    return (s or "")[:10] if re.match(r"\d{4}-\d{2}-\d{2}", s or "") else datetime.date.today().isoformat()


def main():
    db = sys.argv[1]
    pf = sys.argv[2] if len(sys.argv) > 2 else "/mnt/project-files"
    n = {"news": 0, "research": 0, "optsnap": 0, "uw": 0, "rescreen": 0}

    for p in glob.glob(os.path.join(db, "news", "*.json")):
        d = load(p)
        if not d:
            continue
        did = os.path.basename(p)[:-5]
        n["news"] += write_json(os.path.join(A, "news", did[:7], did + ".json"), strip_meta(d))

    for p in glob.glob(os.path.join(db, "research", "*.json")):
        d = load(p)
        if not d or d.get("status") != "done":
            continue
        t = re.sub(r"[^A-Z0-9.\-]", "", os.path.basename(p)[:-5].upper())
        n["research"] += write_json(os.path.join(A, "research", t, day(d.get("updatedAt") or d.get("startedAt")) + ".json"), strip_meta(d))

    for p in glob.glob(os.path.join(db, "optsnap", "*.json")):
        d = load(p)
        if not d:
            continue
        m = re.match(r"([A-Z0-9.\-]+)_(\d{4}-\d{2}-\d{2})$", os.path.basename(p)[:-5])
        if m:
            n["optsnap"] += write_json(os.path.join(A, "optsnap", m.group(1), m.group(2) + ".json"), strip_meta(d))

    uw = os.path.join(pf, "edge-desk", "uw")
    if os.path.isdir(uw):
        shutil.copytree(uw, os.path.join(ROOT, "uw"), dirs_exist_ok=True,
                        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        snap = {}
        for p in glob.glob(os.path.join(uw, "tickers", "*.json")):
            d = load(p)
            if d:
                snap[os.path.basename(p)[:-5]] = d
        lt = load(os.path.join(uw, "latest.json")) or {}
        if snap:
            dp = os.path.join(A, "uw", "tickers", day(lt.get("fetchedAt")) + ".json")
            if not os.path.exists(dp):
                n["uw"] += write_json(dp, snap)
        hist_p = os.path.join(A, "uw", "congress-history.json")
        old = load(hist_p) or []
        new = load(os.path.join(uw, "congress-history.json")) or []
        new = new.get("trades", new) if isinstance(new, dict) else new
        seen, merged = set(), []
        for r in list(new) + list(old):
            k = r.get("id") or json.dumps(r, sort_keys=True)
            if k not in seen:
                seen.add(k)
                merged.append(r)
        merged.sort(key=lambda r: (r.get("filed") or "", r.get("traded") or ""), reverse=True)
        n["uw"] += write_json(hist_p, merged)

    kc = os.path.join(pf, "knowledge", "claude")
    if os.path.isdir(kc):
        for p in glob.glob(os.path.join(kc, "*")):
            shutil.copy2(p, os.path.join(ROOT, "docs", os.path.basename(p)))
        spec = os.path.join(kc, "edge-desk-screener-spec.md")
        if os.path.exists(spec):
            txt = open(spec).read()
            i = txt.find("## Snapshot ")
            if i >= 0:
                m = re.match(r"## Snapshot (\d{1,2}) (\w{3})\w* (\d{4})", txt[i:])
                if m:
                    dt = datetime.datetime.strptime(" ".join(m.groups()), "%d %b %Y").date().isoformat()
                    rp = os.path.join(A, "rescreen", dt + ".md")
                    body = txt[i:].strip() + "\n"
                    if not os.path.exists(rp) or open(rp).read() != body:
                        os.makedirs(os.path.dirname(rp), exist_ok=True)
                        open(rp, "w").write(body)
                        n["rescreen"] += 1

    update_readme()
    print("archive: " + ", ".join(f"{k} {v}" for k, v in n.items()) + " new/changed")


def update_readme():
    lines = [LOG_START, "## Archive log (auto-generated)", "",
             "Full history lives under `archive/`. This section lists the last 30 days of news headlines, "
             "every deep-dive verdict and recent re-screen snapshots so Graphify (which reads only README.md on the Free plan) can find them.", ""]
    cutoff = (datetime.date.today() - datetime.timedelta(days=30)).isoformat()

    lines += ["### Deep-dive verdicts", ""]
    for tdir in sorted(glob.glob(os.path.join(A, "research", "*"))):
        for p in sorted(glob.glob(os.path.join(tdir, "*.json"))):
            d = load(p) or {}
            lines.append(f"- {os.path.basename(p)[:-5]} {d.get('ticker')}: {d.get('verdict')}, {d.get('stance')}, conviction {d.get('conviction')}; "
                         f"price {d.get('price')} vs fair {d.get('fairLow')}-{d.get('fairHigh')} (mid {d.get('fairMid')}). "
                         f"{(d.get('summary') or '').split('. ')[0][:220]}")
    lines += ["", "### Re-screen snapshots", ""]
    for p in sorted(glob.glob(os.path.join(A, "rescreen", "*.md")))[-20:]:
        first = [l for l in open(p).read().splitlines() if l.startswith("- ")][:3]
        lines.append(f"- {os.path.basename(p)[:-3]}: " + " ".join(l[2:] for l in first)[:400])
    lines += ["", "### News headlines (last 30 days)", ""]
    rows = []
    for p in glob.glob(os.path.join(A, "news", "*", "*.json")):
        d = load(p) or {}
        if (d.get("published") or "") >= cutoff:
            rows.append((d.get("published", ""), d))
    for pub, d in sorted(rows, key=lambda x: x[0], reverse=True):
        lines.append(f"- {pub[:10]} [{d.get('level')}] {d.get('title')} ({', '.join(d.get('tickers') or [])})")
    lines.append(LOG_END)

    rp = os.path.join(ROOT, "README.md")
    txt = open(rp).read()
    block = "\n".join(lines) + "\n"
    if LOG_START in txt:
        txt = txt[:txt.index(LOG_START)] + block + txt[txt.index(LOG_END) + len(LOG_END):].lstrip("\n")
    else:
        txt = txt.rstrip("\n") + "\n\n" + block
    open(rp, "w").write(txt)


if __name__ == "__main__":
    main()
