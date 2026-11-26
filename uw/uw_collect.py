#!/usr/bin/env python3
"""Collect public Unusual Whales data for Edge Desk (no login, no API key).

Writes into the folder this script lives in:
  latest.json            congress trades (latest ~100 filings), politician most-held,
                         UW news headlines, per-ticker summary, fetchedAt
  congress-history.json  every congress trade seen so far (kept 400 days)
  tickers/<T>.json       per-ticker IV, IV rank, implied move, max pain, earnings
Usage: python3 -I uw_collect.py [EXTRA_TICKER ...]
"""
import json, os, re, sys, time, datetime, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = "https://unusualwhales.com"
UA = {"User-Agent": "Mozilla/5.0 (EdgeDesk personal research)"}
HOLDINGS = ["GOOGL", "PLTR", "SKM", "DRAM", "MSFT", "BE", "MU", "NBIS", "SNXX", "C", "HOOD", "NOK"]
UNIVERSE = ["SNXX", "SKM", "SPY", "AMD", "PFE", "BAC", "INTC", "CSCO", "UBER", "RKLB", "GDX", "SLV", "SOFI",
            "F", "HIMS", "PYPL", "CCL", "MARA", "IONQ", "OKLO", "SOUN", "NVDA", "QQQ"]
BIG_AMOUNTS = ("$250,001", "$500,001", "$1,000,001", "$5,000,001", "$25,000,001", "$50,000,000")


def page_props(path):
    req = urllib.request.Request(BASE + path, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        html = r.read().decode("utf-8", "replace")
    m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.S)
    if not m:
        raise ValueError("no page data")
    return json.loads(m.group(1)).get("props", {}).get("pageProps", {})


def facts(pp):
    return {f["label"]: f["value"] for f in ((pp.get("seoSummary") or {}).get("facts") or [])}


def ticker_snapshot(t):
    out = {"ticker": t, "url": f"{BASE}/stock/{t}/overview"}
    try:
        f = facts(page_props(f"/stock/{t}/volatility"))
        for k, v in f.items():
            if k.startswith("Implied volatility"):
                out["iv"] = v
                out["ivExpiry"] = k[k.find("(") + 1:-1] if "(" in k else None
        out["ivRank1y"] = f.get("IV rank (1y)")
        out["impliedMove"] = f.get("Implied move")
        out["name"] = f.get("Name"); out["sector"] = f.get("Sector"); out["marketCap"] = f.get("Market cap")
        time.sleep(0.4)
        f = facts(page_props(f"/stock/{t}/greeks"))
        for k, v in f.items():
            if k.startswith("Max pain"):
                out["maxPain"] = v
                out["maxPainExpiry"] = k[k.find("(") + 1:-1] if "(" in k else None
        time.sleep(0.4)
        pp = page_props(f"/stock/{t}/earnings")
        f = facts(pp)
        ev = (pp.get("initialStockEvents") or {}).get("earning") or {}
        out["earnings"] = {"next": f.get("Next earnings"), "time": ev.get("report_time"),
                           "epsEst": ev.get("eps_mean_est"), "lastReport": f.get("Last report"),
                           "lastEps": f.get("Last EPS"), "lastNextDayMove": f.get("Next-day move"),
                           "sinceLastReport": f.get("Since last report")}
        out["price"] = (pp.get("initialStockEvents") or {}).get("currentPrice")
    except Exception as e:  # ETFs and odd tickers can 404
        out["error"] = str(e)[:120]
    return out


def main():
    now = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    watch = set(HOLDINGS + UNIVERSE)
    errors = []

    # Congress trades
    trades, most_held = [], []
    try:
        pp = page_props("/politics")
        for x in pp.get("trade_data") or []:
            sym = (x.get("symbol") or "").upper()
            trades.append({
                "member": x.get("name") or x.get("reporter"), "party": x.get("current_party"),
                "chamber": x.get("member_type"), "ticker": sym, "asset": x.get("issuer"),
                "action": x.get("txn_type"), "amount": x.get("amounts"),
                "traded": x.get("transaction_date"), "filed": x.get("filed_at_date"),
                "source": x.get("link_url"), "id": x.get("file_record_id"),
                "watched": sym in watch, "holding": sym in HOLDINGS,
                "big": bool(sym) and (x.get("amounts") or "").startswith(BIG_AMOUNTS),
            })
        for m in (pp.get("overview_data") or {}).get("most_held") or []:
            most_held.append({"ticker": m.get("ticker"), "politicians": m.get("politicians"),
                              "count": m.get("politicians_count"), "midValue": m.get("mid_value")})
    except Exception as e:
        errors.append(f"politics: {e}")

    # Congress history (append, dedupe, keep 400 days)
    hist_path = os.path.join(HERE, "congress-history.json")
    try:
        hist = json.load(open(hist_path))
    except Exception:
        hist = []
    key = lambda r: (r.get("id"), r.get("ticker"), r.get("traded"), r.get("action"), r.get("amount"), r.get("member"))
    seen = {key(r) for r in hist}
    new_trades = [r for r in trades if key(r) not in seen]
    hist.extend(new_trades)
    cutoff = (datetime.date.today() - datetime.timedelta(days=400)).isoformat()
    hist = [r for r in hist if (r.get("filed") or "9999") >= cutoff]
    hist.sort(key=lambda r: (r.get("filed") or "", r.get("traded") or ""), reverse=True)
    # UW sometimes serves /politics with an empty trade list; keep the last known filings instead
    if not trades and hist:
        errors.append("politics: page returned 0 trades, showing last known filings from history")
        trades = [dict(r, watched=r.get("ticker") in watch, holding=r.get("ticker") in HOLDINGS,
                       big=bool(r.get("ticker")) and (r.get("amount") or "").startswith(BIG_AMOUNTS))
                  for r in hist[:100]]

    # UW news headlines
    news = []
    try:
        pp = page_props("/news")
        for a in pp.get("featuredArticles") or pp.get("posts") or (pp.get("more") or {}).get("posts") or []:
            news.append({"title": a.get("title"), "published": a.get("created_at"), "tags": a.get("tags"),
                         "url": f"{BASE}/news/{a.get('slug')}"})
    except Exception as e:
        errors.append(f"news: {e}")

    # Per-ticker snapshots
    tickers = []
    for t in sorted(watch | {a.upper() for a in sys.argv[1:] if re.fullmatch(r"[A-Za-z0-9.\-]{1,10}", a)}):
        snap = ticker_snapshot(t)
        snap["fetchedAt"] = now
        if "error" not in snap:
            json.dump(snap, open(os.path.join(HERE, "tickers", f"{t}.json"), "w"), indent=1)
        tickers.append(snap)
        time.sleep(0.4)

    latest = {
        "fetchedAt": now, "source": "unusualwhales.com public pages (no login)",
        "notes": "Options flow and dark pool are NOT included: they need a paid UW API key.",
        "congress": {"trades": trades, "newSinceLastRun": len(new_trades),
                     "watchedTrades": [r for r in trades if r["watched"] or r["big"]], "mostHeld": most_held[:15]},
        "news": news, "tickers": tickers, "errors": errors,
    }
    json.dump(latest, open(os.path.join(HERE, "latest.json"), "w"), indent=1)
    json.dump(hist, open(hist_path, "w"), indent=1)
    ok = sum(1 for t in tickers if "error" not in t)
    print(f"UW {now}: {len(trades)} congress trades ({len(new_trades)} new, "
          f"{len(latest['congress']['watchedTrades'])} watched/big), {len(news)} headlines, "
          f"{ok}/{len(tickers)} tickers, errors: {errors or 'none'}")


if __name__ == "__main__":
    main()
