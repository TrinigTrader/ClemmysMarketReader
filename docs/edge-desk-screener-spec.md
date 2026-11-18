# Edge Desk Screener: spec and daily re-screen runbook

Artifact: https://claude.ai/artifact/SmjmcoBbiX1ykbGR6hd1eA (title "Edge Desk Screener")
Page source: `claude/edge-desk-index.html` in this project (the published HTML, without the skeleton).
Data source: Interactive Brokers (IBKR) connector. The page declares mcp → "Interactive Brokers (IBKR)" / get_price_snapshot for a live "Refresh live quotes" button.

## Budget
- Default $10,000 USD. Sleeves: Wheel 60%, Option plays 10%, Stocks 25%, cash 5%.
- Clement's IBKR account (as of 26 Sep 2026) has only about S$358 cash and S$2,651 NLV. The plan assumes he funds $10k. Check whether his account has options permissions for short puts.

## Universe (IBKR contract ids)
SPY 756733, AMD 4391, PLTR 444857009, PFE 11031, BAC 10098, INTC 270639, CSCO 268084, BE 326398514, NBIS 88819736, DRAM 870556708, HOOD 504546674, UBER 365207014, RKLB 787273575, GDX 229726316, SLV 39039301, SOFI 494162724, F 9599491, HIMS 466188387, PYPL 199169591, CCL 878372298, NOK 661513, MARA 474219659, IONQ 517593749, OKLO 500073396, SOUN 558869874.

## Holdings (two IBKR accounts)
- IBKR (live via get_account_positions; 27 Sep 2026): BE 2, DRAM 5, NBIS 2, NOK 5 (avg 14.00), PLTR 2.
- IBKR 2 — Clement's second IBKR account, not connected to the connector (entered by Clement, stored in ArtifactData `holdings/other` {broker, positions:[{t,q}]}, edited from the Overview "Holdings · all accounts" card): MU 3.5, SNXX 150 (Tradr 2X Long SNDK ETF), DRAM 80, PLTR 30, NBIS 12, BE 12, C 6 (entered as "CITI", mapped to Citigroup), HOOD 5, SKM 150 (SK Telecom ADR), GOOGL 20, MSFT 10.
- Combined (27 Sep 2026): GOOGL 20, PLTR 32, SKM 150, DRAM 85, MSFT 10, BE 14, MU 3.5, NBIS 14, SNXX 150, C 6, HOOD 5, NOK 5 — about $44k at 25 Sep closes, ~$42.3k of it in IBKR 2.
- Cash & fixed income (ArtifactData `holdings/fixed` {items:[{name, sgd, mat:"YYYY-MM"}]}): S$20,000 Singapore T-bills maturing Feb 2028. Counts in "All accounts" at the live USD/SGD rate; treat it as the cash buffer when sizing (it is not in either IBKR account).
- Contract ids for the non-universe holdings: MU 9939, SNXX 849555205, C 87335484, SKM 524517647, GOOGL 208813719, MSFT 272093.
- The page computes `held` = IBKR + other broker at runtime, so the re-screen keeps writing only IBKR quantities into U[15]. When writing theses, treat the combined position as what he owns (a PLTR or DRAM idea adds to an existing 32/85-share position; concentration matters). Read `holdings/other` each run for the current list.

Underlying snapshot fields: last, change, implied_vol_underlying, historical_vol, implied_volatility_percentile, misc_statistics, avg_90d_usd_volume, underlying_avg_option_volume.

## Wheel rules
- Stock under ~$60. Sell a put near 0.20 delta (≈0.67σ below spot, σ = spot·IV·√(DTE/365)), 20–45 DTE, monthly expiry preferred.
- Exclude a name if earnings fall before expiry. Check dates by web search; mark estimates "est.".
- Quote quality: spread ≤ 25% of mid and OI ≥ 500.
- Score = annualised yield × (1 − min(spread%, 50%)) × (1 + (IVpct52 − 0.5)·0.4) × (IV>HV ? 1.1 : 0.9).
- Funding: rank order, max 30% of the wheel sleeve per name (or one contract if larger).
- Delta and P(OTM) come from Black-Scholes with the underlying's IV, because the option-level IV comes back invalid outside market hours.

## Option-play rules
- Debit spreads where IV < realised vol and IV percentile is low. Credit spreads where IV is well above realised vol and IV percentile is high.
- Defined risk only. One spread each, funded in order until the plays sleeve ($1,000) runs out.
- Management: take profit at 50% of max; exit debit spreads at −50%.

## Stock screen (all four must pass)
- Price above its price 52 weeks ago (misc_statistics.open_52w)
- Price ≥ 85% of the 52-week high
- 52-week IV percentile < 50%
- 90-day average $ volume ≥ $500M

## Thesis standard (required for every trade shown)
Every wheel pick, option play and passing stock gets a TH entry with: trade (one line), line (the one-sentence thesis), setup (IBKR numbers), why (fundamental/catalyst facts from web research with dates), struct (why this strike/structure, including the edge vs realised vol), risk (what would break it), plan (profit target, roll/exit, what to do if assigned). Also assign a conviction: High / Medium / Medium-Low / Low / Pass. Pass means shown with reasoning but never funded.
- Edge test: compare premium with the put's value using 30-day realised vol (HV). Negative edge → Pass or Low unless there's an ownership reason (e.g. cost-basis repair), which must be stated.
- For spreads, simulate EV and P(profit) under IV and HV; for event trades add an earnings-jump term. State honestly when a trade depends on a directional view.
- Update the "Market read" block (Fed, index level/IV, BTC) and the thesis sources list in the footer.
- Cite only facts found in sources this run. Never invent numbers.

## Daily re-screen procedure
1. Pull underlying snapshots for the universe.
2. Choose the wheel expiry: the nearest monthly with 20–45 DTE, or a weekly when the monthly is under 20 DTE.
3. For each wheel candidate, get the chain around the ~0.20-delta strike, quote bid/ask/OI, and apply the rules above.
4. Re-check the three option plays. Close or replace any play whose expiry has passed or whose thesis broke, using the same rules.
5. Research news for every candidate (web search), write the theses per the standard above, then update the `U`, `W` (incl. conviction), `P` (incl. key/conv/tag), `TH`, `EXP` and `ASOF` constants, the market-read text and sources in the page source. Keep design and code otherwise unchanged. Republish to the artifact URL, and save the updated source back to this project.
6. Report a 5-line summary covering the top wheel pick, any new or closed plays, stocks that passed, and warnings (earnings this week, IV spikes).

## Snapshot 18 Nov 2026 (9:42 ET)
- Published as artifact v49 ("Re-screen 18 Nov"). IBKR flaky again (503s; retried until all 25 underlyings loaded).
- S&P 500 closed 17 Nov at 7,340.53 (−1.03%, fourth straight loss, lowest close since July); Dow −849; Nasdaq 24,328.38 (−0.74%). Nvidia Q3 FY27 revenue $115.8bn (+103%), Q4 guide $130bn (no China data-center sales assumed). Futures rose overnight but SPY $730.95 (−0.2%) at 9:42 ET; IV 20.0% vs HV 14.3%. Gold at a 14-month low, silver −3% (hawkish Fed, strong dollar). Bitcoin ~$64k on 16 Nov. Anthropic IPO prices this week.
- No live option bid/ask; W uses IBKR model values as bid = ask (DTE 30).
- W: PYPL 52.5P $0.53 OI 6,175 Medium (delta .16, edge +$29, funded; strike moved down from $55, now delta .28, $1.05, edge +$34); SLV 37P $0.78 OI 2,647 Low (+$26; SLV $40.86 new 52-week low); DRAM 34P $1.61 OI 8,517 Low (+$14, held shares); SOFI 14P $0.73 Pass (−$12); HIMS 16P $0.64 Pass (−$19).
- Stock screen: no passers. CCL drops off (IVP52 .566). PFE fails only on IV (.869). Three-check names: PYPL, BE, RKLB, CCL. NOK down to two (IVP52 .526).
- Account: S$1,689 NLV, S$45 cash. Positions BE 2, DRAM 5, NBIS 2.5, NOK 5, PLTR 2, VST 1.

## Theses 18 Nov 2026 (summary)
- PYPL Dec 18 $52.50 put: Medium, funded ($5,250 collateral, ~12% annualised). No earnings before expiry (next Feb 2, 2027); sell at $0.50+ on a live quote. $55 put is the higher-premium alternative.
- SLV Dec 18 $37 put: Low (down from Medium-Low); silver broke to a new low; wait for it to stop falling. No budget alongside PYPL.
- DRAM $34 put: Low (adds to held shares). SOFI, HIMS puts: Pass.
- CCL: Watch, off the screen on IV; Q4 report ~Dec 17–18 (est.). Keep any starter's stop below ~$27.50.
- Watch: PFE (IV only), PYPL/BE/RKLB (three checks). PLTR: hold 2, don't add.
