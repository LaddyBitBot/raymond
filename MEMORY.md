# Raymond Memory

## Portfolio Status (as of 2026-07-16)

### Open Positions
| Asset | Entry | Stop | Notional | 1R Risk | Entry Date | Notes |
|---|---|---|---|---|---|---|
| BTC | $61,500 | $56,000 | $7,830 | $700 | 2026-07-03 | 20-day support ~$62K |
| ETH | $1,720 | $1,490 | $7,478 | $1,000 (OVERRIDE) | 2026-07-04 | OVERRIDE: risk $1K vs $800 formula, operator-approved |
| UNI | $3.20 | $3.20 (BE) | $1,600 | $0 (at BE) | 2026-07-04 | Stop moved to BE; partial target ~$3.80 (+1.2R) |
| SOL | $81.19 | $69.19 | $4,740 | $700 | 2026-07-05 | Weakest position; 20-day ~$74.65 is the line |
| NVDA | $210.87 | $192.50 | $3,448 | $300 | 2026-07-14 | ½ formula size, Conv 7 (↑ from 6); TSMC beat/raise confirms AI cycle |

### Closed Positions
| Asset | Entry | Exit | Realized R | Exit Date |
|---|---|---|---|---|
| PLTR | $134.24 | $129.425 | −0.39R | 2026-07-13 |

### Account Parameters
- Capital: $20,000
- MaxLeverage: 20×
- GS Tier: 1 (heat cap 20% = $4,000)
- Portfolio heat used: $2,700 (67.5%)
- Crypto cluster: $2,400/$3,000 (80%) — $600 headroom
- Semi/AI cluster: $300/$3,000 (10%)

## Key Decisions & Events
- **2026-07-14**: Mike opened NVDA at $210.87 (operator entry, ½ formula, stop $192.50 via 2.5× ATR $7.23). Entered pre-ASML earnings.
- **2026-07-14**: CPI June beat (3.5%/core 2.6%) → R improved −0.8 → −0.5
- **2026-07-14**: BTC ETF outflows −$424.66M Monday — streak resumption concern
- **2026-07-14**: Iran ceasefire collapsed; US sanctioned Iranian oil network + crypto wallets. Oil surging (Brent $85+).
- **2026-07-14**: Config fix: `models.providers.ollama.timeoutSeconds` and `agents.defaults.timeoutSeconds` both set to 600 by Mike. Cron daily run should no longer time out.
- **2026-07-15 ~03:39 UTC**: Live prices (Coinbase) — BTC $64,624, ETH $1,870, SOL $77.59. Market bounced on Korea rotation + CPI relief.
- **2026-07-16**: TSMC Q2 record beat/raise — $40.2B revenue, GM 67.7%. Confirms AI/semi cycle. NVDA Conv ↑ to 7.
- **2026-07-16**: ONDO surges to Conv 9 (highest in universe) on DTCC tokenized stocks launch. Formula risk $900 vs $600 cluster headroom — still cap-constrained.
- **2026-07-16**: ETH testing 100-day EMA, approaching +1R/BE at $1,950.
- **2026-07-16**: UNI at $3.64, ~4.4% from $3.80 partial target.

## Pending Decisions
- **ONDO entry**: Conv 9 (↑ from 7), $900 formula risk > $600 cluster headroom → cap-constrained. Options: enter at $600, trim SOL, or pass. DTCC tokenized stocks catalyst.
- **UNI partial**: Take ⅓–½ off at ~$3.80 (+1.2R). V4 governance votes this week.
- **NVDA post-ASML**: TSMC beat/raise confirms cycle. Scale-up candidate (Conv 7, full size $700).
- **SOL exit watch**: 20-day EMA ~$74.65. Break + D negative → decay trigger. Also trim candidate for ONDO headroom.

## Hot List
- NVDA (op, added 2026-07-12) — Conv 7, TSMC confirms AI cycle
- ONDO (watch) — Conv 9, highest in universe, DTCC catalyst, cap-constrained
- HOOD (watch, added 2026-07-18) — crypto-equity proxy, earnings July 30

## Lessons Learned
- **Always pull live prices from Coinbase API for market data**, not stale web search snapshots. Web search results can be hours old.
- **Stop calculations must use §7a formula** (2.5× ATR beyond invalidation), not eyeballed ranges. The daily run's "$195–198" was sloppy estimation.
- **Don't narrate process** ("Let me pull...", "Now I have everything I need..."). Do the work silently, deliver the answer. Narrating creates clutter and repetition.
- **Don't repeat phrases** across messages. If you said "No, I didn't" once, don't say it again — just do the action.
- **"I'll do better" is meaningless unless written here.** Every time a quality mistake is caught, add the concrete fix to this section. This is the only mechanism for cross-session improvement.
- **When asked about market prices, always fetch live from Coinbase API first** — never lead with web search prices. Web search is for news/context only.
- **When Mike sends a file named `rating-system-spec---*.md`**, replace `rating-system-spec.md` in the workspace with the received content, commit it as "Replace rating-system-spec.md with YYYY-MM-DD revision", and push to GitHub. Do not add or modify the §11 changelog — that travels with the file content he sends.
- **Stop levels are single numbers, not ranges.** Run the ATR math, round to a clean level, commit. Don't present a range and call it ambiguity.
- **When Mike says "open" or "close" a position, he is the trader — I only update the log.** Do not execute trades, do not place orders, and do not run git commit/push for those log updates unless he explicitly asks. The entry/exit price he states is logged as the operator-executed fill.