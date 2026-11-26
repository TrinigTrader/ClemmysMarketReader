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

<!-- ARCHIVE-LOG:START -->
## Archive log (auto-generated)

Full history lives under `archive/`. This section lists the last 30 days of news headlines, every deep-dive verdict and recent re-screen snapshots so Graphify (which reads only README.md on the Free plan) can find them.

### Deep-dive verdicts

- 2026-09-26 AMD: Fairly valued, Neutral, conviction Medium; price 630.92 vs fair 520-670 (mid 600). AMD is executing well
- 2026-09-27 BE: Overvalued, Neutral, conviction Medium; price 289 vs fair 190-275 (mid 232). Bloom is executing exceptionally: Q2 2026 revenue of $1.065B (+166% YoY), a 22.5% non-GAAP operating margin, positive FCF, and FY26 guidance raised to $3.9-4.2B with every major US hyperscaler now a validated customer
- 2026-10-23 CRDO: Fairly valued, Overweight, conviction Medium; price 165.7 vs fair 150-270 (mid 210). Credo sells the active electrical cables, SerDes and optical DSPs that connect AI servers, and it is growing fast and profitably: fiscal Q1 2027 revenue rose 115% to $479M with a 48% non-GAAP operating margin, and it gui
- 2026-09-27 DRAM: Fairly valued, Neutral, conviction Low; price 61.97 vs fair 54-76 (mid 65). DRAM is a $26B actively managed basket of Samsung, Micron and SK hynix (together about 74%), plus smaller NAND and storage names
- 2026-09-27 FOPC: Fairly valued, Underweight, conviction Medium; price 24.73 vs fair 24.5-24.95 (mid 24.73). FOPC is not a company but a small ($33M) actively managed fund-of-funds that holds 8 bond ETFs (FLXR, VGIT, IGEB, JCPB, SCHP, MBB, VTIP, PYLD), so its fair value is its NAV and it trades close to it; there is no misprici
- 2026-09-27 INTC: Overvalued, Underweight, conviction Medium; price 122.95 vs fair 80-120 (mid 100). Intel's turnaround is real: Q2 revenue grew 25%, data-center sales jumped 59%, gross margin recovered about 12 points to ~42%, and it has landed Tesla (14A) plus a reported Apple foundry deal
- 2026-09-27 IONQ: Fairly valued, Neutral, conviction Low; price 45.3 vs fair 36-60 (mid 48). IonQ is the revenue leader in listed quantum computing (Q2 revenue $80.1M, +287% YoY, about two-thirds of the listed pure-play group's Q2 revenue) and has raised 2026 guidance to $450–460M after closing the SkyWater foun
- 2026-09-26 MSFT: Fairly valued, Neutral, conviction Medium; price 517.91 vs fair 470-575 (mid 520). Microsoft is executing very well: FY26 revenue was $331.8B (+18%), Azure grew 43% last quarter, and commercial RPO jumped 84% to $678B
- 2026-09-27 MU: Fairly valued, Neutral, conviction Medium; price 1085.02 vs fair 1010-1345 (mid 1180). Micron is earning record, peak-cycle profits: fiscal Q3 revenue rose 346% y/y to $41.5B at an 85% gross margin, and Q4 is guided to $50B
- 2026-10-23 NBIS: Fairly valued, Neutral, conviction Medium; price 160.3 vs fair 135-240 (mid 185). Nebius is one of the fastest-growing AI clouds: Q2 2026 revenue rose about 454% to roughly $582M with a 41% adjusted EBITDA margin, and it reaffirmed $3.0-3.4B 2026 revenue and $7-9B exit ARR
- 2026-11-12 NVDA: Undervalued, Overweight, conviction Medium; price 166.08 vs fair 180-240 (mid 205). NVDA trades at $166.08, about 32% below its 52-week high of $243.37 after an AI-chip sell-off that began in October and deepened on Nov 5 (-9%, no company-specific news reported)
- 2026-11-10 ORCL: Fairly valued, Neutral, conviction Low; price 120.4 vs fair 105-165 (mid 135). Oracle trades at about $120, roughly 52% below its 52-week high of $249 and near its 52-week low of $109
- 2026-11-03 PLTR: Fairly valued, Neutral, conviction Low; price 174.82 vs fair 120-210 (mid 165). Palantir just posted an exceptional Q3 2026: revenue of $2.313B (+96% y/y), a 62% adjusted operating margin, and U.S
- 2026-09-27 SNDK: Fairly valued, Neutral, conviction Low; price 1772.04 vs fair 1500-2075 (mid 1790). Sandisk is a pure-play NAND supplier riding an AI-driven flash shortage: FY26 revenue rose 175% to $20.2B, Q4 gross margin hit 84.6% and Q1 FY27 guidance ($10.3–10.8B revenue, $44–46 EPS) points higher still
- 2026-09-27 SOFI: Fairly valued, Neutral, conviction Medium; price 16.58 vs fair 14.5-20.5 (mid 17.5). SoFi is executing well: Q2 2026 adjusted revenue rose 40% to $1.21B, net income rose 61% to $157M, members hit 15.8M, and FY26 guidance calls for ~$0.60 adjusted EPS
- 2026-10-23 SPCX: Fairly valued, Neutral, conviction Low; price 147.3 vs fair 115-215 (mid 160). SpaceX (now including xAI and X) just posted its first operating profit as a public company: Q3 2026 revenue rose 161% to $14.6B, beating the $12.86B consensus, with $2.79B of operating income and $4.4B of net income ($0

### Re-screen snapshots

- 2026-11-16: Published as artifact v47 ("Re-screen 16 Nov"). IBKR was flaky (many 503s; retried until all 25 underlyings loaded). SPY $747.95 (−0.9%), IV 16.0% vs HV 13.7%. S&P 500 closed 13 Nov at 7,561.67 (−0.4%, +2.5% on the week). Nvidia reports ~Nov 18 after close (est.); Anthropic IPO this week. Brent ~$96.30, gold −0.9%. December Fed hike priced near-certain. Bitcoin ~$73k on 14 Nov. No live option bid/
- 2026-11-17: Published as artifact v48 ("Re-screen 17 Nov"). IBKR flaky again (503s; retried until all 25 underlyings loaded). S&P 500 closed 16 Nov at 7,416.59 (−1.92%); Nasdaq 24,509.76 (−2.49%, correction territory). SPY $738.59, IV 18.2%. Nvidia reports today Nov 17 after the close (confirmed). Anthropic IPO expected to start trading Thursday. No live option bid/ask at 9:40 ET; W uses IBKR model values as 
- 2026-11-18: Published as artifact v49 ("Re-screen 18 Nov"). IBKR flaky again (503s; retried until all 25 underlyings loaded). S&P 500 closed 17 Nov at 7,340.53 (−1.03%, fourth straight loss, lowest close since July); Dow −849; Nasdaq 24,328.38 (−0.74%). Nvidia Q3 FY27 revenue $115.8bn (+103%), Q4 guide $130bn (no China data-center sales assumed). Futures rose overnight but SPY $730.95 (−0.2%) at 9:42 ET; IV 2
- 2026-11-19: Published as artifact v50 ("Re-screen 19 Nov"). IBKR loaded all 25 underlyings (one 503 on an option, retried). Fixed a build bug that left a 0.0% change blank in U. 18 Nov: S&P 500 −0.23% to 7,323.63 (fifth straight loss), Dow −561, Nasdaq +0.42% to 24,429.88; Nvidia −2.9% (board says Huang won't return as CEO); AMD +5.8%. Anthropic priced IPO at $83 (above $70–78 range, ~$81bn raised), trading t
- 2026-11-23: SPY $723.20 (+4.8%), IV 21.3% vs HV 16.5%, 52w IV pct 95% (elevated). S&P 500 ~7,238 (+4.7%, best day since Apr 2025) after Nvidia reinstated Jensen Huang; Fri 20 Nov S&P −3.7% to 6,910, Nasdaq −5.3%, week −8.6% (correction). Anthropic (ANT) closed day one 19 Nov at $97.17 (+17% on $83 IPO). Dec 8–9 Fed hike ~98% priced. Account: S$45 cash, S$1,693 net liq. Positions BE 2, DRAM 5, NBIS 2.5, NOK 5,
- 2026-11-24: SPY $715.88 (−0.9%), IV 23.4% vs HV 22.2%, 52w IV pct 98% (elevated). Chips reversing Monday's Nvidia rally: AMD −9.6% (registered ~337M OpenAI/Meta warrant shares for resale, Nov 23), DRAM −7.3%, INTC −5.6%. Mon 23 Nov S&P ~+4.7% (best day since Apr 2025). Dec 8–9 Fed hike ~98% priced; gold at 13-month low (Nov 16). BTC ~$64k (Nov 19). Account: S$45 cash, S$1,592 net liq. Positions BE 2, DRAM 5, 
- 2026-11-25: SPY $698.10 (−2.9%), IV 26.7%, 52w IV pct 99.6%; VIX above 26. Drivers: hot PCE (3.8%), new 20% tariffs, chip rout. Silver broke its $36.72 low (SLV $35.09, −4.8%). Thanksgiving: closed Thu 26 Nov, early close Fri 27 Nov. Account: S$45 cash, S$1,458 net liq. Positions BE 2, DRAM 5, NBIS 2.5, NOK 5, PLTR 2, VST 1. IBKR returned no option bid/ask at the open; W rows use model price as bid = ask.

### News headlines (last 30 days)

- 2026-11-26 [Medium] Europe rebounds: Stoxx 600 up 1.4%, DAX 1.7% early as chipmakers lead (VGK, ASML, SMH)
- 2026-11-26 [Medium] Asia rebounds after chip rout: Taiex up 2.6%, Kospi 1.2%, SK Hynix 3.7%; Bank of Korea hikes (EWY, EWJ, SMH)
- 2026-11-25 [Low] Sen. Rand Paul discloses three Nvidia purchases of $1K to $15K each (NVDA)
- 2026-11-25 [High] Stocks tumble into Thanksgiving: Nasdaq 100 tracker down over 4% on hot PCE, tariffs and chip rout (QQQ, SMH, NVDA, ORCL, NBIS)
- 2026-11-25 [High] TrendForce trims DRAM price forecast; Micron falls ~10%, SanDisk 11.5% (MU, DRAM, SNXX, SNDK, WDC)
- 2026-11-25 [High] US proposes Section 301 tariffs on 14 partners; China faces extra 20% (FXI, EWY, EWT, SMH, SKM)
- 2026-11-25 [High] Core PCE runs hot at 3.3%; Q3 GDP revised up to 4.3% (SPY, QQQ, TLT, MU, NBIS, HOOD)
- 2026-11-25 [Low] Rep. Kevin Hern sells $15K-$50K of Intel (filed Nov 25) (INTC)
- 2026-11-25 [Low] Deere misses at $3.89 EPS on farm weakness, shares down over 3% (DE, CAT)
- 2026-11-25 [Medium] Futures slip before PCE; Dell reverses to -7.5% premarket, Workday -9.9% (SPY, QQQ, DELL, WDAY)
- 2026-11-25 [Medium] Peter Thiel buys $122.3M of Palantir stock (PLTR)
- 2026-11-25 [High] Micron falls 11%, chip index down 7.9%; Kospi slides nearly 6% Wednesday (MU, DRAM, SNXX, SKM, NVDA)
- 2026-11-24 [Low] Autodesk beats with $3.20 EPS and raises guide, shares fall about 4% (ADSK, IGV)
- 2026-11-24 [Medium] Nvidia closes down 7.2%, Nasdaq 100 falls 2.7% as Huang rally reverses (NVDA, QQQ, SMH, AMD)
- 2026-11-24 [Low] HP Inc Q4 beats at $16.0B revenue, guides FY27 EPS $3.15 to $3.45 (HPQ, DELL)
- 2026-11-24 [High] Dell Q3 revenue $54.9B, up 103%; AI backlog hits $132.3B, FY guide $202B (DELL, MU, DRAM, NVDA)
- 2026-11-24 [Low] Workday Q3 beats at $2.705B revenue, raises subscription guide to $9.958B (WDAY, CRM, IGV)
- 2026-11-24 [Medium] HPE falls 16% as AI server margin squeeze overshadows raised outlook (HPE, DELL, SMCI)
- 2026-11-24 [Medium] US readies new Section 301 tariffs on China, EU and a dozen-plus economies (FXI, SPY, EWG)
- 2026-11-24 [Medium] Schumer vows probe of Huang's return; Gallego wants trading probe (NVDA, SMH)
- 2026-11-24 [Medium] BNP Paribas cuts Micron to Neutral, slashes target to $775 from $1,700 (MU, DRAM, SNXX)
- 2026-11-24 [Low] Medtronic Q2 EPS $1.34 edges past, revenue $9.36B misses; shares fall premarket (MDT, XLV)
- 2026-11-24 [Low] Dell, Workday, HP report after close; Best Buy, ADI before open (DELL, ADI, BBY, MU)
- 2026-11-24 [Medium] SpaceX and Tesla name five directors to negotiate a possible $3.5 trillion merger (TSLA)
- 2026-11-24 [Medium] Kospi jumps over 6%, SK Hynix up about 9% as Huang returns to Nvidia (DRAM, SNXX, MU, EWY)
- 2026-11-23 [Medium] CrowdStrike to buy Zscaler in $43.9B all-stock deal (CRWD, ZS, PANW)
- 2026-11-23 [High] Dow soars 1,448 points, Nasdaq +6.5% in best day since April 2025 on Huang return (SPY, QQQ, NBIS, MU)
- 2026-11-23 [High] Nvidia reinstates Jensen Huang as CEO; NVDA closes up about 30%, Nebius and CoreWeave up 30%+ (NVDA, NBIS, MU, SMH)
- 2026-11-23 [Medium] Rep. Hageman buys MU and NVDA, sells MSFT (filed Nov 23) (MU, MSFT, NVDA)
- 2026-11-19 [High] Dow sinks 1,101 points below 50,000; Nasdaq -2.25% as Anthropic fails to lift AI trade (SPY, QQQ, MU, NBIS)
- 2026-11-19 [High] Anthropic opens at $111.50, up 34% from IPO, near $2 trillion value (GOOGL, AMZN, MSFT, NVDA)
- 2026-11-19 [Medium] Chips rally at the open: Micron up ~5%, Nvidia ~4% before Anthropic's debut (MU, GOOGL, NVDA, QQQ)
- 2026-11-19 [Medium] Philly Fed plunges to 6.3, lowest since May; jobless claims 203K vs 197K expected (SPY, TLT)
- 2026-11-19 [Low] Walmart beats, raises full-year outlook a third time; e-commerce up 17% (WMT, XRT)
- 2026-11-19 [Medium] Trump filing: sold GOOGL, bought MSFT, NVDA, AMD ($1K-$15K each), filed Nov 19 (GOOGL, MSFT, NVDA, AMD)
- 2026-11-19 [Medium] Nasdaq futures up 2%, S&P up 1% ahead of Anthropic's debut (QQQ, SPY)
- 2026-11-19 [Low] Trump, Xi and Putin hold first trilateral; nuclear talk but no deal (FXI, SPY, SMH)
- 2026-11-19 [Low] Kospi slips 1.4% below 5,000 as pension funds sell Samsung, SK Hynix (EWY, DRAM)
- 2026-11-18 [High] Anthropic prices record IPO at $83, above range; raises about $81B (GOOGL, AMZN, NVDA, MSFT)
- 2026-11-18 [Low] Renaissance cut Nvidia 99.7% in Q3; Micron now its largest holding (NVDA, MU, GOOGL)
- 2026-11-18 [Medium] Fed minutes: nearly all officials see further hikes, a couple floated a bigger move (SPY, QQQ, TLT)
- 2026-11-18 [Medium] Iran strikes US air base in Kuwait and targets in Bahrain after US hit on Qeshm Island (USO, XLE)
- 2026-11-18 [Low] Dow falls 1.1%, S&P 500 fifth straight loss; Nvidia down 2.9% despite beat (NVDA, SMH, QQQ)
- 2026-11-18 [Low] Lowe's beats with comps up 1.8%, lifts sales outlook; shares slip premarket (LOW, XRT)
- 2026-11-18 [Low] Target comps jump 5.6%, raises guidance; tariff refund adds ~50 cents EPS (TGT, XRT)
- 2026-11-18 [Low] Nasdaq futures up about 1% as Nvidia rises ~3% premarket; Fed minutes, Anthropic pricing today (QQQ, SPY, NVDA)
- 2026-11-18 [Low] Kospi's Nvidia rally fades: opened up 3%, slipped by late morning (EWY, SMH)
- 2026-11-17 [High] Nvidia beats, guides Q4 to $130B and lifts FY28 growth view to ~75% (NVDA, MU, DRAM, SNXX, NBIS, MSFT, GOOGL, SMH)
- 2026-11-17 [Medium] Jensen Huang says he would be honored to return as Nvidia CEO (NVDA)
- 2026-11-17 [Low] Dow drops 849 points, S&P 500 at lowest close since July before Nvidia (QQQ, SPY, NVDA)
- 2026-11-17 [Medium] Nvidia cuts Nokia stake by 56%; Nokia falls more than 4% (NOK, NVDA)
- 2026-11-17 [Low] Home Depot beats with comps up 2.2%, names Richard McPhail CEO (HD, XRT)
- 2026-11-17 [Medium] Nvidia cuts Intel stake by 25%; Intel falls 3.3% premarket (INTC, NVDA)
- 2026-11-17 [Low] US futures slip 0.4% ahead of Nvidia results after Monday's chip rout (SPY, QQQ, NVDA, SOXX)
- 2026-11-17 [Low] Bitcoin near $64,600, down about 13% in a week (BTC, COIN, HOOD)
- 2026-11-17 [Low] Taiwan's Taiex falls another 1.7% after Monday's 6% crash (EWT, TSM, EWY)
- 2026-11-17 [Low] Kospi opens down 1.8%, slips below 5,000 on Nvidia day (EWY, MU, DRAM)
- 2026-11-16 [Medium] US rule requires licenses for AI chip sales to 5 countries, curbs China remote access (NVDA, AMD, SMH)
- 2026-11-16 [Low] Fed Chair Warsh gives AI and productivity speech, no rate signal (TLT, SPY)
- 2026-11-16 [Medium] AI selloff deepens at the open: Nebius -8%, Micron -5% to -7%, Nasdaq -1.4% (NBIS, MU, DRAM, SNXX, NVDA, HOOD)
- 2026-11-16 [Medium] Fatal accident halts work at Micron's Taichung site; production reportedly unaffected (MU, DRAM)
- 2026-11-16 [Low] Phillip Securities lifts Palantir target to $248 from $215, keeps Buy (PLTR)
- 2026-11-16 [Medium] Nasdaq closes down 2.5%, S&P down 1.9% as Nvidia leads AI rout (SPY, QQQ, NVDA, SOXX)
- 2026-11-16 [Low] European stocks steady, Stoxx 600 up 0.1% as chip names slip (VGK, NOK)
- 2026-11-16 [Medium] Kospi falls 3.6% as SK hynix sinks 7.9%, Samsung 4.5% (MU, DRAM, SNXX, SKM, NVDA)
- 2026-11-16 [Medium] China October data misses: retail sales +0.4%, output +4.8%, investment -8.1% (FXI, KWEB, EEM)
- 2026-11-16 [Low] Kospi reverses lower after flat open, SK hynix slips ahead of Nvidia (MU, DRAM, SNXX, SKM)
- 2026-11-15 [Low] Japan Q3 GDP shrinks 0.1% annualised, missing forecasts for growth (EWJ, USDJPY)
- 2026-11-15 [Low] US futures tick higher Sunday night, Nasdaq futures up about 0.4% (SPY, QQQ, NVDA, MU, NBIS)
- 2026-11-15 [Low] Micron at $778 after 12.8% weekly gain heading into Nvidia week (MU, DRAM, SNXX, NVDA)
- 2026-11-15 [Low] Friday's 4-hour FAA ground stop, longest in 25 years, blamed on router switch (DAL, UAL, AAL, JETS)
- 2026-11-15 [Medium] Bitcoin drops to ~$65K Sunday, down ~14% on the week (BTC, HOOD, COIN)
- 2026-11-14 [Medium] Bessent urges Fed not to over-hike; Goolsbee, Daly push back (TLT, SPY, QQQ)
- 2026-11-14 [Medium] Trump says he's done seeking an Iran deal but won't resume war 'for now' (USO, XLE)
- 2026-11-13 [Medium] Week ahead: Nvidia earnings Tue ($108.8B expected), retail sales, Walmart, Anthropic IPO (NVDA, WMT)
- 2026-11-13 [Medium] Nvidia approached Arm CEO Rene Haas; no search firm picked yet; stock below $4T (NVDA, ARM)
- 2026-11-13 [Medium] CFTC sues Louisiana over order blocking Robinhood, Kalshi event contracts (HOOD, COIN)
- 2026-11-13 [Medium] S&P -0.4%, Nasdaq -0.9% Friday, but Nasdaq logs first weekly gain in 5 weeks (SPY, QQQ, NVDA, AMD, MU, NBIS)
- 2026-11-13 [Low] Oil posts second weekly drop, Brent settles at $95.84 (CL, BZ, XLE)
- 2026-11-13 [Medium] Reuters finds $3B+ of Chinese AI data centres built on restricted Nvidia chips (NVDA)
- 2026-11-13 [Medium] Chip sell-off deepens: Nasdaq -1.7%, AMD -10%, Nvidia -3% (SPY, QQQ, NVDA, AMD, AVGO, MU, DRAM, SNXX, NBIS)
- 2026-11-13 [Medium] Altman told Samsung AI memory demand was 'double-counted' (MU, DRAM, SNXX, NBIS, 005930.KS)
- 2026-11-13 [Low] SpaceX-Tesla merger talks progress; deal possible in December (TSLA)
- 2026-11-13 [Medium] White House weighs Lutnick ouster; Senate calls Huang, Lutnick to testify (NVDA, AMD, MU)
- 2026-11-13 [Medium] Rep. David Taylor (R) buys GOOGL $1K-$15K, filed Nov 13 (GOOGL)
- 2026-11-13 [Medium] HSBC cuts Nvidia to hold, slashes target to $170 from $375 (NVDA)
- 2026-11-13 [Medium] October PPI +0.3% vs 0.4% expected; 6.5% y/y, highest since 2022 (SPY, TLT, C, NBIS, MU, BE, PLTR)
- 2026-11-13 [Medium] Microsoft falls ~2% premarket as global 365 outage enters day 2 (MSFT)
- 2026-11-13 [Low] Europe dips from record: Stoxx 600 -0.2%, still set for best week since June (VGK, NOK)
- 2026-11-13 [Medium] Baird cuts Nebius target to $200 from $340; Piper to $148 (NBIS, CRWV, IREN)
- 2026-11-13 [Low] Asia late: Kospi reverses to -0.7%, SK Hynix -2%; Nikkei +0.9% (DRAM, MU, SNXX)
- 2026-11-13 [Low] Samsung in talks to buy data-center cooling maker Modine; MOD +25% (MOD, DRAM, BE)
- 2026-11-12 [Medium] Huang agrees to testify before Congress; China chip curbs gain traction (NVDA)
- 2026-11-12 [Low] Cerebras jumps ~12% after hours on raised guidance; Broadcom closed +5.5% (CBRS, AVGO, AMD, ANET)
- 2026-11-12 [Low] Applied Materials beats with record $10.41B revenue, guides Q1 to $11.1B (AMAT)
- 2026-11-12 [Medium] Robinhood October: $15.1B net deposits, crypto volume down 21% (HOOD, COIN)
- 2026-11-12 [Medium] Stocks close lower: S&P -0.35%, Nasdaq -0.39%; Nvidia -4.3%, Nebius ~-16% (NVDA, NBIS, MU, DRAM, GOOGL, QQQ)
- 2026-11-12 [Medium] Cisco beats with $18.5B revenue, raises FY27 guide; AI outlook $9B (CSCO, ANET)
- 2026-11-12 [Medium] At least six analysts downgrade Nvidia; Citi cuts target to $225 (NVDA)
- 2026-11-12 [Medium] 10-year yield jumps to ~5.07%; Goldman adds a March Fed hike (TLT, C, NBIS, BE, PLTR, MU)
- 2026-11-12 [Medium] Trump says US doesn't need Iran deal; Brent above $94, 10-year tops 5% (USO, XLE, TLT)
- 2026-11-12 [High] Jensen Huang resigns as Nvidia CEO; Kress interim, NVDA ~-10% premarket (NVDA, MU, DRAM, SNXX, NBIS, MSFT, GOOGL)
- 2026-11-12 [High] Nebius Q3 revenue $980.8M beats, but $40-45B 2027 capex sinks stock ~10-15% (NBIS, CRWV, NVDA)
- 2026-11-12 [Low] Nvidia ~-7% premarket as board weighs Huang; Alibaba falls 7% (NVDA, BABA, AMD, AVGO, MU, DRAM, NBIS)
- 2026-11-12 [Low] Asia extends gains despite Nvidia crisis: Kospi +1.2%, Nikkei +0.8% (MU, DRAM, SKM, 005930.KS, 000660.KS)
- 2026-11-12 [Medium] Bernstein cuts Nvidia to Market Perform, halves target to $200 (NVDA, MU, DRAM, SNXX, NBIS)
- 2026-11-12 [High] Nvidia board weighs ousting CEO Huang; NVDA ~-9% after hours (NVDA, MU, DRAM, SNXX, NBIS, MSFT, GOOGL)
- 2026-11-11 [Medium] Axios: Lutnick stalled Nvidia China chip curbs Trump approved 3 times (NVDA, MU, DRAM)
- 2026-11-11 [Medium] Sen. Hawley backs nationwide pause on data center construction (BE, GOOGL, MSFT, NBIS, VST, CEG)
- 2026-11-11 [Medium] PLA-linked Chinese university bought Nvidia H200s despite US blacklist (NVDA, MU, DRAM)
- 2026-11-11 [Low] Nasdaq closes +1.6%, S&P +1.3% as CoreWeave's 24% jump revives AI trade (CRWV, NVDA, NBIS, MU, DRAM, AVGO)
- 2026-11-11 [Medium] Micron jumps ~13% as CoreWeave beat and Morgan Stanley revive memory (MU, DRAM, SNXX, SNDK, WDC)
- 2026-11-11 [Low] Robinhood up ~5%, Coinbase ~4% as bitcoin steadies near $74K (HOOD, COIN, BTC)
- 2026-11-11 [Medium] Bloom Energy surges ~17% as CoreWeave lifts AI power stocks (BE, FCEL, CRWV)
- 2026-11-11 [Low] Neoclouds jump premarket: CoreWeave +13.7%, Nebius and peers up 4.7%-11.8% (NBIS, CRWV, ORCL, IREN, NVDA)
- 2026-11-11 [Low] Rep. Cisneros (D) sells NVDA and UBER, buys CSCO (K-$15K each) (NVDA, CSCO, UBER)
- 2026-11-11 [Low] Premarket: CoreWeave +13%, Nvidia +5%, Nasdaq futures +1.6% (CRWV, NVDA, MU, NBIS, DRAM)
- 2026-11-11 [Low] Nasdaq futures up 1.5% on CoreWeave beat; Europe opens up 0.9% (QQQ, NBIS, MU, DRAM, BE)
- 2026-11-11 [Low] Kospi up 1.7%, KOSDAQ +5% at midday as Tankan hits 5-year high (EWY, EWJ, MU, DRAM, SNXX)
- 2026-11-11 [Low] Oil rebounds to ~$92 Brent as tankers hit mines in Hormuz (USO, XLE, NBIS, PLTR, BE)
- 2026-11-11 [Medium] Nebius reports Q3 Thursday premarket; consensus about $906M revenue, options price ~17% move (NBIS, CRWV, MU, DRAM)
- 2026-11-11 [Low] Asia opens flat after hot US CPI; SoftBank sinks 9% (EWY, EWJ, MU, DRAM, SNXX, NBIS)
- 2026-11-10 [Medium] Google, Nvidia and Micron among 7 firms buying $26B of Anthropic IPO stock (GOOGL, MU, NVDA, MSFT)
- 2026-11-10 [Low] Stocks close lower after hot CPI; Nvidia drops 5.5% (QQQ, SPY)
- 2026-11-10 [Medium] CoreWeave beats Q3 at $3.66B, lifts 2026 revenue guide to $13-13.3B (CRWV, NBIS, MU, DRAM, NVDA)
- 2026-11-10 [Low] White House vows to keep tariffs despite midterm backlash over prices (SPY, NBIS, PLTR, NOK)
- 2026-11-10 [Medium] Microsoft passes Nvidia in market value as Nvidia slides over 6% (NVDA, MSFT, MU, NBIS, DRAM, BE)
- 2026-11-10 [Low] 10-year yield back at 5% as Fed hawks line up behind a December hike (TLT, NBIS, PLTR, BE, C)
- 2026-11-10 [Medium] Anthropic launches Claude Sheets and office tools; Microsoft falls over 3.5% (MSFT, GOOGL)
- 2026-11-10 [Low] Bloom Energy falls 4.6% on profit-taking and hot CPI (BE, GEV, VRT)
- 2026-11-10 [High] October CPI runs hot: 0.4% headline, 0.3% core; Nasdaq futures sink (QQQ, NBIS, PLTR, BE, MU, HOOD, C)
- 2026-11-10 [Low] Premarket: Sanmina up 19%, Take-Two up 4%, Nvidia and Micron edge up (SANM, TTWO, NVDA, MU)
- 2026-11-10 [Medium] Anthropic sets IPO range at $70-$78, raising up to $64.4B (GOOGL, AMZN, NBIS)
- 2026-11-10 [Low] US futures mixed before CPI, Nvidia up 1.7% premarket (SPY, QQQ, NVDA)
- 2026-11-10 [Low] Stoxx 600 near record, up 0.9%; Infineon up 3% as oil slides (VGK, IFNNY)
- 2026-11-10 [Medium] SoftBank swings to $7.1B Q2 net loss as Arm, Intel, Coupang slide (SFTBY, ARM, INTC)
- 2026-11-10 [Low] European futures up 0.9% after Stoxx 600 gains 1.3%, CPI eyed (VGK)
- 2026-11-10 [Medium] Nikkei reclaims 60,000, SoftBank jumps over 11%, Kioxia up 7% (SFTBY, TOELY, ATEYY)
- 2026-11-10 [Medium] Anthropic sends, then retracts IPO terms: 867M shares at $70-$80 (GOOGL, AMZN, NBIS)
- 2026-11-10 [Medium] Nvidia and Huang hit with securities class action over spy ties (NVDA)
- 2026-11-10 [Medium] Kospi jumps 4.5% at open, SK Hynix up 7%, Samsung up 5% (MU, DRAM, SNXX)
- 2026-11-10 [Low] US futures flat ahead of CPI, December hike odds near 80% (SPY, QQQ)
- 2026-11-09 [Low] Bitcoin near $74.7K, down from $82.8K a month ago (BTC, HOOD, COIN)
- 2026-11-09 [Low] SoftBank reports Q2 today, $64.6B OpenAI stake in focus (SFTBY, MSFT, NBIS)
- 2026-11-09 [Medium] Dow jumps 1,104 points; Nasdaq up about 2.7% and exits correction (SPY, QQQ)
- 2026-11-09 [Medium] AMD surges 13.4% to $509 on Oppenheimer upgrade (AMD, NVDA, MU)
- 2026-11-09 [Low] Robinhood backs tokenized trading of its stock on OKX-ICE venue (HOOD, ICE)
- 2026-11-09 [Low] Congress Democrats press Nvidia on Huang affair, Jeffries flags concern (NVDA)
- 2026-11-09 [High] Brent sinks 5.9% to $92.57 as Trump signals restraint on Iran (USO, XLE, C, NBIS)
- 2026-11-09 [Medium] NYT: Commerce cleared Nvidia H200 buyers with empty offices (NVDA, MU, DRAM)
- 2026-11-09 [Medium] Palantir snaps 8-day losing streak, up about 5.9%; Citi PT $265 (PLTR)
- 2026-11-09 [Low] NYSE picks Avalanche for tokenized stock platform, AVAX up 10% (HOOD, COIN, ICE)
- 2026-11-09 [Medium] Alphabet rises 3.3% as Google launches two new TPU variants (GOOGL, NVDA)
- 2026-11-09 [High] Nvidia falls 4.2% as board probes Jensen Huang's ties to alleged Chinese spy (NVDA, AMD, MU, NBIS)
- 2026-11-09 [Medium] CoreWeave reports Q3 Tuesday after close, $3.54B expected (CRWV, NBIS, NVDA)
- 2026-11-09 [Low] Nuclear stocks bounce as Oklo and NuScale post smaller losses (OKLO, SMR, BE)
- 2026-11-09 [Low] Coinbase wins full OCC national trust charter (COIN, HOOD)
- 2026-11-09 [Medium] December Fed hike odds near 85% after hot jobs data (TLT, C, NBIS, PLTR)
- 2026-11-09 [Medium] October CPI due Tuesday: 0.3% headline, 0.2% core expected (SPY, QQQ, TLT)
- 2026-11-09 [Medium] Anthropic IPO roadshow week starts with no price range filed (GOOGL, AMZN, NBIS)
- 2026-11-09 [Medium] Kospi rebounds to 5,118; SK Hynix up 4.2%, Samsung up 2.5% (MU, DRAM, SNXX, SKM)
- 2026-11-09 [Medium] China October PPI jumps 5.7%, highest since 2022; CPI misses at 0.7% (FXI)
- 2026-11-08 [Medium] Anthropic pays $3.4B for 1.7GW of gas generators (BE, CAT, GEV)
<!-- ARCHIVE-LOG:END -->
