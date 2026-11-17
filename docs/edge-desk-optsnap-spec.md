# Edge Desk options lab: daily snapshot spec

The Options lab tab of the Edge Desk Screener (https://claude.ai/artifact/SmjmcoBbiX1ykbGR6hd1eA) scans option chains from IBKR and saves one snapshot per ticker per US trading day to the page database, so positioning (open interest, GEX walls, zero gamma) can be compared across dates. A scheduled task captures the tickers on the page's auto-track list after each US close.

## Nightly run
1. ArtifactData `get` `optsnap_cfg/main` → `tickers` (max 6). If empty, stop.
2. Date = today's date in America/New_York (YYYY-MM-DD). Skip US market holidays (no new OI).
3. For each ticker (uppercase letters, digits, dot, dash only):
   - IBKR `search_contracts` → US listing with OPT; `get_price_snapshot` on the underlying (last, implied_vol_underlying, underlying_today_option_volume, underlying_avg_option_volume).
   - `get_option_parameters` → pick the nearest expiry with ≥ 2 DTE, the next standard monthly (`regular: true`) and the monthly after that (up to 3 distinct expiries).
   - For each expiry `get_option_data` with min_strike = spot × 0.88 and max_strike = spot × 1.12; keep the 24 strikes nearest spot.
   - For every call and put: `get_price_snapshot` with bid_ask, last, option_volume, option_open_interest, implied_vol.
   - If the ticker already has a doc for this date (`optsnap/<T>_<date>`), merge: replace rows for the same (e, K), keep others.
4. ArtifactData `set` `optsnap/<T>_<date>` with the schema below (`source: "scheduled"`).
5. Read only. Never place orders or create order instructions. Never republish the page.

## Document schema: optsnap/<TICKER>_<YYYY-MM-DD>
```
{ ticker, date, takenAt (ISO UTC), spot, iv (underlying annual IV, decimal), source: "page"|"scheduled",
  uvol: { c, p, avgC, avgP },           // underlying total option volume today vs average
  rows: [ { e: "YYYYMMDD", K: number,
            cOI, pOI, cV, pV,           // open interest and today's volume (integers)
            cB, cA, cL, pB, pA, pL,     // bid, ask, last for call and put (omit if missing)
            cIV, pIV } ] }              // decimal IV (omit if invalid)
```
Omit null fields. Keep each document under 100 KB.

## Page math (for reference)
- GEX per strike = BS gamma × OI × 100 × S² × 1%, calls +, puts − (assumes dealers long calls / short puts).
- Zero gamma: grid search ±20% of spot for the sign change of total GEX. Call wall = max call GEX strike; put wall = most negative put GEX strike.
- Max pain per expiry; expected move = ATM call mid + ATM put mid.
- Flow proxy: Vol/OI > 1 flagged; last trade within 25% of the spread from the ask = "near ask · bought", from the bid = "near bid · sold". There is no tape or sweep/block data in the IBKR connector.
