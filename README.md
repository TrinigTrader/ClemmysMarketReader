# Edge Desk

Personal, read-only investment research tooling for options (the wheel, debit/credit spreads), stock picks and market news. Built and run by Claude in the "Investments Analysis" claude.ai project. Nothing here places orders. Not financial advice.

## What's in this repo

| Path | What it is |
|---|---|
| `docs/edge-desk-index.html` | Source of the Edge Desk Screener page (a private claude.ai artifact). Single-file HTML/JS app with tabs: Overview, Wheel, Option plays, Stocks, News, Deep Dive, Options lab, Wheel Check, Watchlist, Portfolio. Reads live quotes from the Interactive Brokers (IBKR) connector and stores state in the artifact database. |
| `docs/edge-desk-screener-spec.md` | Screener rules and the daily re-screen runbook (budget, universe, wheel / option-play / stock rules, thesis standard, latest snapshot). |
| `docs/edge-desk-news-spec.md` | News scanner spec: `news` collection schema, categories, impact levels, phone/Telegram alert rules. |
| `docs/edge-desk-deepdive-spec.md` | Deep-dive research spec: per-ticker report schema (`research/<TICKER>`), valuation verdict method. |
| `docs/edge-desk-optsnap-spec.md` | Nightly options snapshot spec (`optsnap/<TICKER>_<date>`), GEX / zero-gamma / max-pain math. |
| `docs/edge-desk-handoff.txt` | Full handoff notes: history of requests, architecture, scheduled tasks, appendices. |
| `docs/UPGRADE-NOTES.md` | Notes from moving the original claude.ai project to the new project format. |
| `uw/uw_collect.py` | Collector for public Unusual Whales pages (no login, no API key). Writes the JSON files below. |
| `uw/latest.json` | Latest congress trades, politicians' most-held stocks, UW headlines, per-ticker summary. |
| `uw/congress-history.json` | Every congress trade seen since 2026-10-17 (kept 400 days). |
| `uw/tickers/<T>.json` | Per-ticker IV, 1y IV rank, implied move, max pain, next earnings. |

The JSON files are a snapshot taken 2026-11-17; the collector refreshes the live copies every 2 hours.

## Architecture

- **Page**: one claude.ai HTML artifact ("Edge Desk Screener"). Live data comes from the IBKR connector (`get_price_snapshot`, `get_option_data`, `get_account_positions`, ...); shared state lives in the artifact's database (collections `news`, `research`, `optsnap`, `optsnap_cfg`, `holdings`, `prefs`, `meta`).
- **Scheduled tasks** (Claude routines):
  - *News scan* every 2h: writes `news` docs, sends High-impact alerts to a Telegram channel.
  - *Daily re-screen* each US trading day: re-runs the wheel/plays/stock screen, rewrites theses, republishes the page.
  - *Deep dive* on demand from the page: writes a full `research/<TICKER>` report.
  - *Options snapshots* nightly after the US close: saves chain OI/IV for auto-tracked tickers.
  - *Unusual Whales collector* every 2h: runs `uw/uw_collect.py`.

## Screening rules (summary)

- Budget $10,000: Wheel 60%, option plays 10%, stocks 25%, cash 5%.
- **Wheel**: stock under ~$60; sell a ~0.20-delta put, 20-45 DTE, monthly preferred; no earnings before expiry; spread <= 25% of mid and OI >= 500. Score = annualised yield x (1 - min(spread%, 50%)) x (1 + (IVpct52 - 0.5) x 0.4) x (IV > HV ? 1.1 : 0.9). Max 30% of the sleeve per name.
- **Option plays**: debit spreads when IV < realised vol and IV percentile is low; credit spreads when IV is well above realised vol. Defined risk only; take profit at 50% of max, exit debits at -50%.
- **Stocks** (all must pass): price above its price 52 weeks ago, price >= 85% of 52-week high, 52-week IV percentile < 50%, 90-day average dollar volume >= $500M.
- **Thesis standard**: every idea has trade, one-line thesis, setup, why now, structure, risk, plan and a conviction (High / Medium / Medium-Low / Low / Pass). Edge test compares premium with value at 30-day realised vol.

## Options math

- GEX per strike = Black-Scholes gamma x OI x 100 x S^2 x 1% (calls +, puts -).
- Zero gamma: sign change of total GEX on a +/-20% grid. Call wall = max call GEX strike; put wall = most negative put GEX strike.
- Expected move = S x IV x sqrt(DTE/365), cross-checked with ATM straddle mid.

## Universe

SPY, AMD, PLTR, PFE, BAC, INTC, CSCO, BE, NBIS, DRAM, HOOD, UBER, RKLB, GDX, SLV, SOFI, F, HIMS, PYPL, CCL, NOK, MARA, IONQ, OKLO, SOUN, plus holdings GOOGL, SKM, MSFT, MU, SNXX, C, QQQ, NVDA.

## Running the collector

```
python3 -I uw/uw_collect.py [EXTRA_TICKER ...]
```

Writes into the `uw/` folder. Options flow and dark-pool data are not included (they need a paid Unusual Whales API key).
