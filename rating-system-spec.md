# Daily Rating System — Runbook & Spec

**Horizon:** weeks-to-months (swing-to-position character, targeted at ~3–12 week holds)
**Universe:** an operator-maintained watchlist (not a fixed index) in three buckets — **crypto**, **equity single names**, and **diversifiers** (commodities, FX, broad-market ETFs, quoted per lighter.xyz venue tickers). All lists change over time; the current roster is in **§0** below.
**Output:** Buy / Sell / Hold + 1–10 conviction per asset, daily
**Operator:** Agent runs the process; you maintain the hot list, set risk limits, and own all decisions.
**Account size & margin:** read from the **§9 run log header** at the start of every run — the log is the single source of truth and carries both forward. **First run (no log present): assume a $100,000 account and 20× max leverage**, and write those into the day's log header. All sizing in §7 is expressed in **R and fractions of Capital**, so the system applies unchanged to any account size; see §7b for how margin interacts with position sizing and §7c for the notional guardrail

> **Scope honesty (read first).** Point-in-time web-search snapshots, no streaming data, no continuous monitoring, and no memory between sessions are a comfortable fit for ~3–12 week holds re-rated daily. The §10 limitations bite hardest below ~2-week holds, where crypto funding/OI/liquidations and social velocity move intraday and a once-daily snapshot is genuinely stale — treat anything on that clock as out of architecture.

---

## 0. Current universe roster (operator-maintained)

*Last updated: 2026-07-05. These lists are maintained by the operator and change over time — edit them here and they flow into every run.*

**Crypto (31)** — weight set §2 (crypto), direction §3, β-tiers per §3:
`BTC, ETH, HYPE, SOL, BNB, ZEC, NEAR, XLM, AVAX, TRX, TON, LIT, OP, POL, ARB, MNT, MEGA, LINEA, AAVE, ASTER, LINK, ENA, VVV, MORPHO, APT, JUP, LDO, CRV, AERO, UNI, ONDO`

**Equity single names (23)** — weight set §2 (equity), direction §3, β-tiers per §3:
`MU, NVDA, MSTR, GOOG, STRC, SNDK, CRCL, MRVL, AMZN, TSLA, MSFT, INTC, META, AAPL, AMD, SPCX, HOOD, ORCL, COIN, PLTR, DELL, TSM, RKLB`

**Diversifiers (12) — quoted per Lighter (lighter.xyz) venue tickers** — weight set §2 (equity, reinterpreted per the notes below), direction §3:
`XAU, XAG, WTI, BRENTOIL, NATGAS, WHEAT, XCU, EURUSD, USDJPY, AUDUSD, SPY, IWM`

> **Roster maintenance notes.**
> - *Crypto-proxy equities:* `MSTR, COIN, HOOD, CRCL, STRC` (and other BTC-levered names) trade as **BTC-beta** — count them in the crypto cluster for the §7c per-cluster cap, not as independent equity risk.
> - *Semis cluster:* `NVDA, MU, MRVL, AMD, INTC, TSM, SNDK, DELL` move together on the AI-capex/semi cycle — treat as one correlation cluster under §7c.
> - *Diversifier clusters (§7c):* **precious metals** `XAU, XAG` · **energy** `WTI, BRENTOIL, NATGAS` · **ags & industrial** `WHEAT, XCU` · **FX** `EURUSD, USDJPY, AUDUSD` · **US broad equity** `SPY, IWM`. The sleeve exists to hold risk that is *uncorrelated* with the crypto/tech clusters — a set of diversifier positions that all express one macro bet defeats the purpose.
> - *Diversifier scoring:* use the **equity weight set** with Catalyst read as scheduled macro events (CPI/FOMC, OPEC, EIA inventories, crop reports, BoJ/ECB), Sentiment inputs from futures/COT positioning and ETF flows, Trend unchanged. β-tiers: precious metals and FX **defensive (0.7)**; energy, copper, and broad equity **normal (1.0)**.
> - *Venue liveness:* Lighter listings cycle inactive — a diversifier can only signal if its market is confirmed **live** on the venue that run (§8 step 3).
> - *Deliberately excluded for now:* Asia consumer names (BABA, Tencent, BYD, Pop Mart, Samsung, EWY, et al.) — candidate cluster for a later revision.

---

## 1. Design principles (tuned for weeks-to-months)

- **Most days = Hold, but Hold means "thesis intact."** The engine resists flip-flopping: a persistence rule for entries, daily cadence, and stop/exit-plan re-evaluation every run. Actionable new signals are the exception; most runs maintain and manage what's already on per the §7d exit ladder.
- **Trend is a gate, not just a factor.** Trend/flow carries real predictive weight for the trade itself, and MA structure (20/50/200-day) is a **hard entry and scaling condition** (§5 trend gate) on top of its §2 factor score. Regime is **context plus an extreme-contrarian trigger** (§3).
- **Two distinct sentiment roles, kept separate.** Aggregate positioning/crowding is **contrarian** — fade true extremes (§6). Fresh project-specific news + social *velocity* is **momentum/catalyst** — you ride it (folded into the Catalyst factor, §2), until crowding hits an extreme and it flips to a fade. Conflating these is the classic swing-trading error.
- **Costs and carry are a first-class gate.** Round-trip cost + slippage — and, on multi-week perp holds, **funding** — eat into edge. A signal that does not clear the cost hurdle (§5) is a Hold even when `|D| ≥ 0.4`.
- **Direction ≠ conviction.** Direction is how bullish/bearish; conviction is strength × agreement across factors × data quality. Mixed signals = low conviction even when net-positive.
- **Asymmetry over accuracy.** Losses are capped at 1R by construction, breakeven arrives early, and runners are allowed to compound (§7d). The expectancy target is a fat right tail, not a high win rate.

---

## 2. Factor categories & weights

Each factor is scored on a signed scale **−2 (strong bearish) … 0 (neutral) … +2 (strong bullish).**

Crypto and equity single names use **separate weight sets** — crypto leans sentiment-heavy, equities lean catalyst/trend-heavy.

| Category | Crypto | Equity | What it captures |
|---|---|---|---|
| Catalyst / news + social velocity | 0.28 | 0.32 | Imminent earnings & guidance, token unlocks/upgrades/airdrops, listings, regulatory, on-chain fundamentals, **and the rate-of-change of project-specific news + social attention** (the deep-dive layer) |
| Sentiment / positioning / flow (contrarian) | **0.30** | 0.22 | Crowding/positioning extremes faded; mild momentum-confirm in mid-range (§6). Crypto-weighted by design. |
| Trend / technical | 0.25 | 0.26 | Primary trend, relative strength, momentum, MA structure, overbought/oversold |
| Regime (smile, §3) | 0.12 | 0.15 | Macro/geopolitical/breadth top-down read — **mild directional tailwind in the middle, contrarian at the extremes** |
| Secular trend tilt | 0.05 | 0.05 | Near-vestigial here — only a "don't fight the megatrend on noise" tilt |

*(Each column sums to 1.0.)* Regime's routine weight is deliberately small, but its **extreme-day** influence is decisive via the smile in §3 — "matter as a contrarian signal at the extremes," not as the everyday directional driver.

---

## 3. Direction score

**Regime beta tiers** (scale the *directional core* of the regime read by the asset's risk sensitivity):
- High-beta (most crypto, high-growth/unprofitable tech): **β = 1.3**
- Normal (mega-cap quality, BTC/ETH): **β = 1.0**
- Defensive (low-vol, quality): **β = 0.7**

**Regime smile.** `R` = the day's single regime score (−2 … +2, + = risk-on / easy / accelerating), shared across all assets. Instead of a purely directional `R · β`, regime enters as a smile — directional in the middle, contrarian at both extremes. To keep a small wobble near the boundary from flipping the sign of the whole term, the two zones are joined by a **linear transition band** rather than a hard step:

```
Core (|R| < 1.3): RS = 0.6 · R · β directional, β-scaled tailwind/headwind
Transition (1.3 ≤ |R| ≤ 1.7): RS = (1−t)·(0.6 · R · β) + t·(−sign(R)·1.2) with t = (|R| − 1.3) / 0.4
Extreme (|R| > 1.7): RS = −sign(R) · 1.2 fade euphoria / buy panic
```

So extreme risk-on (`R ≥ +1.7`) contributes **negative** (lean against the crowd), extreme risk-off (`R ≤ −1.7`) contributes **positive** (contrarian buy), the calm middle is a gentle β-scaled nudge, and the 1.3–1.7 band eases between the two so a measurement wobble near the old 1.5 line nudges the contribution instead of inverting it. *(Worked example: at `R = +1.5, β = 1.0`, `t = 0.5` → `RS = 0.5·0.9 + 0.5·(−1.2) = −0.15` — mildly contrarian, not slammed to −1.2.)*

**Direction score** (crypto and equity single names):

```
D = clamp(
 w_cat · Catalyst
 + w_sent · SC (sentiment smile, §6)
 + w_trend · Trend
 + w_reg · RS (regime smile, above)
 + w_sec · Secular ,
 −2, +2 )
```

with `w_*` taken from the asset's column in §2. `D` ∈ [−2, +2].

**Confluence rule** (replaces the old one-way regime gate):
- When the regime smile and the sentiment smile point the **same contrarian direction** (both euphoric → both fading, or both panicked → both buying), that is the highest-quality setup — allow full magnitude on both and **raise `Q`**.
- When regime is extreme but a **fresh idiosyncratic catalyst** on the specific asset opposes the fade, **cap the regime contrarian term at ±0.5.** Don't short a real catalyst just because the macro tape is hot, and don't buy panic into a name whose own thesis just broke.

---

## 4. Conviction (the 1–10)

Three independent components, each ∈ [0, 1]:

- **Strength** = |D| / 2 — distance from neutral.
- **Agreement** `A` = |Σ contributionᵢ| / Σ |contributionᵢ| — coherence of the factors. Equals 1 when every factor points the same way; →0 when they cancel.
- **Quality** `Q` = data confidence (freshness, known catalyst dates, source reliability). Default 0.8; for the crypto sentiment/funding/OI inputs used to time entries, dock `Q` when they aren't from the current day; lower further when inputs are thin.

```
Conviction = round( 1 + 9 · ( Strength^0.5 · A^0.3 · Q^0.2 ) ) ∈ [1, 10]
```

Strength is weighted most, so a powerful, coherent, well-sourced read reaches 9–10; a mixed or cancelling read lands 3–5 even if direction is positive. High conviction is *meant to be rare.*

---

## 5. Action mapping & anti-churn

- **Neutral band:** `|D| < 0.4` → **Hold**, always.
- **Cost hurdle:** estimated move-to-first-target (in R or %) must exceed round-trip cost + slippage + expected funding over the anticipated hold by **≥ 3×** — otherwise **Hold**, even with a valid signal.
- **Open / add** (initiate or increase): requires `|D| ≥ 0.4` **and** `Conviction ≥ 6` **and** the signal has persisted **≥ 2 consecutive run-days**, **and** the cost hurdle clears, **and** the trend gate (below) permits.
- **Trend gate (hard condition; daily-close MA structure; long side — mirror for shorts):**
	- **Below the 20-day MA → no new position.** The signal may score and sit on the hot list, but entry waits for a daily close above the 20-day (§6 step 3 covers how this interacts with extreme-fear readings).
	- **Above the 20-day, below the 50-day → starter only:** open at **½ of formula size** (§7b).
	- **Above both the 20- and 50-day → full formula size**; scale a starter to full on a daily close above the 50-day.
	- **Above the 200-day and extended** (price ≳ 20% over the 200-day, crowding `P ≥ 85`, or clearly overbought): **late-trend caution** — no size-ups, tighten the §7d trail, take the partial early. Mean reversion is the base case for *new* risk here, and the §6 fade side should already be docking the score.
- **Exit / trim** (you hold it): trigger on **any** of — `D ≤ −0.4` (for a long), conviction collapse `< 4`, stop hit (§7d ladder), or thesis invalidation. **Exits skip persistence and skip the trend gate** — risk management acts faster than entry.
- **Binary-event rule:** no new entry into a binary event (earnings, unlock, vote, scheduled regulatory date) within its window **unless the event itself is the thesis**. Events gap through stops.
- Otherwise → **Hold**.

**Hot-list override:** hot-list names are always routed to deep (Tier-2) scrutiny, get the fullest factor set + extra sources, and may use a slightly lower action threshold (Conviction ≥ 5) because you're watching them closely. The hot list does **not** bypass the trend gate.

**Operator-override rule (off-formula trades):** any trade outside the formula — size above the §7b conviction-scaled risk, an entry that violates the trend gate, persistence, or the cost hurdle, or a breach of a §7c cap — is **not taken on the system's authority**. It requires explicit operator sign-off and must be tagged **`OVERRIDE: <reason>`** in the §9 rationale for that asset on the run it opens **and every run it remains open**. An off-formula position found untagged is flagged as a violation on the next run and brought back to formula (trim to formula size, or exit).

**Stop, size & target mechanics:** see §7 — stops set first (ATR + invalidation), size from the stop and conviction (5% max risk per trade), then the §7d asymmetric exit ladder (breakeven at +1R, partial at +1.5R, trail the runner), all under the portfolio-heat and correlation-cluster caps.

---

## 6. Sentiment & contrarian system

**Step 1 — Build a crowding percentile `P` (0–100).** Normalize and blend the available inputs into one "how crowded / how greedy" score, where 0 = maximum fear / under-positioned, 100 = maximum greed / over-positioned. On this horizon, prioritize **near-real-time, fast-moving** inputs and weight **velocity** (rate of change) alongside level.

- *Crypto (fast inputs lead):* funding-rate sign **and** magnitude, open-interest delta, liquidation cascades, perp basis, Crypto Fear & Greed, BTC dominance shifts, and **social-volume velocity** (rate of change, not just level).
- *Equities / index:* CNN Fear & Greed, AAII bull/bear, put/call ratio, VIX level & term structure, % above 200-day MA, notable fund flows.
- *Single names:* options skew / unusual activity, analyst-sentiment shifts, short interest, retail chatter velocity.

**Step 2 — The fade ("smile") transform** → raw `SC_base`. The big contrarian numbers are reserved for **true extremes** — the documented contrarian edge lives at capitulation and euphoria, not at ordinary discomfort, and mid-range fear is the most common reading in any pullback:

| Crowding `P` | `SC_base` | Reading |
|---|---|---|
| ≥ 95 | −2.0 | True euphoria → fade hard |
| 85–95 | −1.5 | Greed → fade |
| 65–85 | 0 → −1.0 (linear) | Getting crowded |
| 40–65 | **+0.4 · sign(Trend)** | Calm middle → ride the trend |
| 25–40 | 0 → +0.75 (linear) | Getting fearful — mild credit only |
| 12–25 | +1.0 | Fear |
| ≤ 12, or a liquidation-cascade / capitulation day | +2.0 | True panic → fade hard |

**Step 3 — Regime and trend-gate interaction.** Regime: handled jointly with the §3 confluence rule — when the sentiment fade and the regime smile agree in the same contrarian direction, allow full magnitude and raise `Q`; when the fade opposes a fresh idiosyncratic catalyst on the asset, the §3 cap applies. Don't fade a strong, fresh fundamental trend on aggregate positioning alone.

**Sentiment scores it; the trend gate times it.** Extreme-fear readings (`P ≤ 12`, `SC = +2.0`) almost always print with price *below* the 20-day MA — exactly where the §5 trend gate forbids entry. That is sequencing, not contradiction: the high `SC` drives the name to the top of the hot list at high conviction, and the position opens on the **first daily close back above the 20-day**. Capitulation → reclaim → entry converts knife-catching into a confirmed reversal; the cost is the first few percent of the bounce, which this horizon can afford.

**Step 4 — Divergence booster.** If price prints new highs/lows while breadth / funding / social *diverge*, push `SC` a further ±0.5 toward the fade (within [−2, +2]). Divergence at an extreme is the highest-quality contrarian setup and also raises `Q` — and it's *more* valuable on this horizon, not less.

---

## 7. Position sizing, stops & exits

**Think in R.** `1R` = the capital risked on a trade = entry-to-stop distance × position size. Every target, every outcome is measured in R — never in fixed dollar amounts. Log realized R per closed trade (§9) — average R is the only honest read on edge, and at this turnover the cost drag shows up there first.

### 7a. Stops (set the stop first, then size to it)

- **Primary — ATR stop:** place the initial stop **2–3 × ATR(14)** from entry, then nudge it to sit just beyond the nearest real invalidation level (swing low, support, key MA).
- **Crypto:** use a **closing-basis** stop (ignore intraday wicks) and the wider end of the ATR range — higher vol + 24/7 gap risk.
- **Single names (e.g. NVDA):** anchor to structure + known catalysts; earnings/regulatory events gap through % stops, so size down or stand aside into them (see §5 binary-event rule).
- **Thesis stop (always on):** exit regardless of price if `D ≤ −0.4`, conviction `< 4`, or the catalyst/thesis breaks. Whichever triggers first — price or thesis — wins.

### 7b. Position size (risk-based)

**`Capital` and `MaxLeverage` are read from the §9 run log header (first run / no log: default $100,000 and 20×). Everything below is expressed in R and fractions of Capital — no fixed dollar amounts anywhere in the sizing math.**

```
Capital        = from run log header (§9)   — default $100k on first run
MaxLeverage    = from run log header (§9)   — default 20× on first run
Max notional buying power = MaxLeverage · Capital
Risk_per_trade = Capital · MaxRisk · (Conviction / 10)        MaxRisk = 5%
Position size (notional)  = Risk_per_trade / StopDistance%
Leverage used  = Position size / Capital    (must stay ≤ MaxLeverage)
```

**Sizing examples at MaxRisk = 5%, expressed as fractions of Capital (valid at any account size):**

| Conviction | Risk (1R, % of Capital) | Notional size (5% stop) | Implied leverage |
|---|---|---|---|
| 10 | 5.0% | 100% of Capital | 1.0× |
| 8 | 4.0% | 80% of Capital | 0.8× |
| 6 | 3.0% | 60% of Capital | 0.6× |
| 5 (hot-list floor) | 2.5% | 50% of Capital | 0.5× |

**Margin use guidance:**
- Margin is a *capacity* ceiling, not a sizing target. The risk formula drives size; leverage is the output, not the input.
- **Hard notional cap:** no single position may exceed **1× Capital in notional** — enforce this as an absolute ceiling in addition to the risk formula.
- On **crypto** (24/7, high-vol, liquidation cascades): treat effective max as **10×** notional per position unless a specific higher limit is set by the operator. Crypto liquidations are non-linear; the headline MaxLeverage limit applies to equities where margin calls are orderly.
- Sizing to an **ATR-based stop already does the volatility-scaling** (a wider BTC stop ⇒ smaller notional for the same dollar risk), so no separate vol term is needed. High leverage will naturally result from tight stops on low-vol assets — confirm the stop is structurally sound before accepting the implied size.
- **Trend-gate scaling (§5):** between the 20- and 50-day MAs, open at **½ of formula size** (a starter); scale to full formula size on a daily close above the 50-day. The add is its own entry for risk purposes — set its stop per §7a and track blended R on the combined position.

### 7c. Portfolio guardrails

- **Portfolio heat cap — tiered by the growth-scare dial (§8 step 1):** total open risk (Σ Risk_per_trade across all positions) is capped by the active tier — **Tier 0 → 25% of Capital** (no triggers on), **Tier 1 → 20%** (one trigger), **Tier 2 → 15%** (two triggers; no new entries in high-beta clusters), **Tier 3 → 10%** (all three; exits-only for high-beta clusters — diversifier and defensive entries still permitted). New entries that would breach the active cap are skipped or down-sized, even with a valid signal. The active tier and which triggers fired are recorded in the §9 run header.
- **Total notional cap:** aggregate open notional across all positions **≤ MaxLeverage · Capital** (the margin ceiling read from the run log). In practice the heat cap will bind first for most portfolios — the notional cap is a hard backstop against the edge case where many tight-stop positions pile up.
- **Correlation clustering:** count each cluster's combined risk toward a **per-cluster cap of ~15% of Capital at risk**. Clusters: **(1) BTC-beta** — all crypto plus crypto-proxy equities (MSTR, COIN, HOOD, CRCL, STRC, …); **(2) AI/semis** — NVDA, MU, MRVL, AMD, INTC, TSM, SNDK, DELL (plus QQQ/SOXL if ever added — they are tech beta, not diversification); **(3) high-beta AI/software**; **(4) precious metals** — XAU, XAG; **(5) energy** — WTI, BRENTOIL, NATGAS; **(6) ags & industrial** — WHEAT, XCU; **(7) FX** — all currency pairs; **(8) US broad equity** — SPY, IWM. Clusters 4–8 are the diversifier sleeve (§0) — their purpose is *uncorrelated* risk, so a set of diversifier positions that all express one macro bet (e.g., all-in on inflation) deserves a second look before it's sized.
- **Per-asset notional backstop:** no single position should exceed **1× Capital in notional** without explicit operator sign-off — even if the risk formula and heat cap technically permit it. Large notional relative to account size magnifies funding costs, spread impact, and liquidation exposure non-linearly.

### 7d. Exits & targets — the asymmetric exit ladder

**Every position gets an explicit exit plan at entry, and the plan's current state is re-stated in the log every run.** The plan is the ladder below; the position's current stop price and ladder rung are tracked in the §9 asset table (`Stop` column) and updated every run. **An open position with no current stop recorded in the log is a violation.**

The ladder (long side; mirror for shorts):

1. **At entry:** initial stop per §7a (2–3 × ATR, beyond invalidation). This is the only point at which a full 1R is at risk.
2. **At +1R:** move the stop to **breakeven**. From here the position is a free option on the thesis.
3. **At +1.5R:** take **⅓–½ off**. The banked partial pays for the losers; the remainder is a runner.
4. **Runner:** trail at the **chandelier stop (highest close − 2.5–3 × ATR)** or the rising **20-day MA**, whichever is more conservative for the structure. Under a §5 late-trend caution flag, tighten to the 10/20-day or 2 × ATR. **Never widen a stop.** Exit the runner on a daily close through the trail, on thesis break (§7a), or on signal decay (§5).
5. **Time stop:** if the position hasn't reached **+1R within ~4–6 weeks** (or its catalyst has passed without follow-through), recycle the capital regardless of price — a sized thesis that goes nowhere for a month is dead capital and dead heat-cap room.

**Transition rule (positions opened under a prior spec revision):** legacy entries are grandfathered — do not re-litigate the entry against rules that didn't exist when it was taken — but each is placed on this ladder **immediately**, at the rung its R-progress to date implies, with a current stop recorded in the §9 `Stop` column from the next run onward. A legacy position that is off-formula under the *current* rules (size, caps) follows the §5 operator-override rule: tag it `OVERRIDE:` with operator sign-off, or bring it back to formula.

The point is asymmetry: losses are capped at 1R by construction, breakeven arrives early, and the runner is allowed to compound to multi-R when the trend cooperates. **Do not convert runners into fixed targets** — the right tail is where the expectancy lives.

*Account size and max leverage (read from the §9 run log header; defaults on first run: $100k / 20×), MaxRisk (5%), the tiered heat cap (25/20/15/10%), 15% cluster cap, per-asset notional backstop, and ATR multiples are your dials — change them in the log header and they flow through every calculation on the next run. I apply them; I don't set your tolerance.*

---

## 8. Daily run procedure (what Agent does each run)

0. **Read account parameters** — pull `Capital` and `MaxLeverage` from the prior run log header (§9). **No prior log (first run of the system): default to a $100,000 account and 20× max leverage**, and record both in today's log header so they carry forward. All §7 sizing and guardrails use these values; nothing else in the system depends on account size.
1. **Regime read** — compute the single `R` dial from macro data **anchored to the prior daily settlement/close** (rates/inflation/Fed/liquidity, 2s10s, DXY, oil, VIX level & term structure, breadth/% > 200-day) — one fixed anchor per day, shared across all assets including the 24/7 crypto names. **Same-day reruns reuse the same anchor and must reproduce the same `R`** — the time of day a run happens is not allowed to move it. Intraday moves are noted as watch items but do **not** re-set `R`; the one exception is a genuine regime break (FOMC, a major data surprise, a real shock), which may trigger an explicit **off-anchor update, flagged as such in the log**. **Headline discipline:** a geopolitical/macro headline only moves `R` if it is a scheduled/confirmed event or persists across the anchor — transient intraday headlines are logged as watch items, not folded into `R` (breaking, thesis-specific news belongs in the Catalyst factor, §2, not the regime dial). Flag which smile zone `R` sits in — **core** (|R| < 1.3), **transition** (1.3–1.7), or **extreme** (|R| > 1.7) — since that governs the regime contribution (§3). **Growth-scare dial (hard triggers, same anchor discipline):** compute three binary triggers — **(a) payrolls:** 3-month average payroll growth below ~50K, or a negative print; **(b) curve:** 2s10s re-inverts, or bull-steepens more than ~25bp within a month on growth fears; **(c) credit:** HY OAS more than ~75bp above its 3-month low. The count of triggers on (0–3) sets the §7c heat-cap tier; record the tier and which triggers fired in the §9 run header.
2. **Freshness check (crypto)** — before scoring, confirm funding/OI/social inputs are current; dock `Q` for anything stale (§4).
3. **Tier-1 screen** — quick trend/momentum/RS pass across crypto, equity single names, and diversifiers, **capturing each name's position vs its 20/50/200-day MAs (feeds the §5 trend gate)**; flag standouts, extremes, and fresh news/social-velocity spikes. For diversifier-sleeve names, confirm the Lighter market is **live/active** before it can signal — listings there cycle inactive.
4. **Tier-2 deep dive** — hot list (always) + current holdings (always) + Tier-1 flags. Apply the full factor set incl. sentiment/contrarian §6 and the project-specific news/social deep dive.
5. **Score** — compute direction (§3), conviction (§4), cost hurdle, trend gate, and action (§5) for each in scope; for every open position, update the §7d exit-ladder state (current stop, rung, R-progress).
6. **Output** — a ratings table + a dated log entry (§9) with one-line rationale per rated asset.

**Cadence:** daily runs are **mandatory** — the §7d exit ladder and per-position stop tracking are managed per run, and a missed run is unmanaged risk. Add extra checks around known catalysts and, for crypto, an intraday glance when funding/OI/social move sharply.

---

## 9. Log format (carry this forward between runs)

Persistence, hysteresis, time stops, and outcome-tracking all depend on history. Paste the prior log back at each run.

The log is written as **native markdown** (not pipe-delimited text in a code block — that renders poorly and breaks if the fence is lost). Each run's log entry has three parts, in order:

**Part 1 — Run header** (one two-column table per run; these fields are the machine-readable state):

| Field | Value |
|---|---|
| DATE | YYYY-MM-DD |
| CAPITAL | $__ |
| MAXLEV | __× |
| REGIME R | __ |
| ANCHOR | __ (prior close/settlement used) |
| ZONE | core / transition / extreme |
| GS TIER | 0–3 (growth-scare triggers on — payrolls / curve / credit — sets the §7c heat cap) |

**Part 2 — Run notes** (free-form prose paragraph directly below the header table: macro summary, watch items, anything that doesn't fit a field — kept out of the table so long text never mangles the layout).

**Part 3 — Asset ratings** (one markdown table, one row per rated asset):

| Asset | Class | D | Conv | Action | β-tier | Key factors | Rationale (1 line) | Prior action | Days in trade | R-progress | Stop |
|---|---|---|---|---|---|---|---|---|---|---|---|

`CAPITAL` and `MAXLEV` are how account size and max leverage persist between runs — §8 step 0 reads them from the most recent run header table at the start of every run. If no prior log exists (first run), the defaults are **$100,000 and 20×**; to change either, edit the values in the latest run header (or state the new values at run time) and they apply from the next run onward. `Days in trade`, `R-progress`, and `Stop` are first-class — the §7d exit ladder depends on them: `Stop` records each open position's **current stop price and ladder rung** (e.g., `1,490 (initial)`, `BE`, `trail 2.95`) and **must be updated every run for every open position** — an open position with an empty `Stop` cell is a violation. Off-formula positions carry the **`OVERRIDE:`** tag in Rationale every run they remain open (§5). Reviewing this log over time is how we learn whether the qualitative weights (§2) are earning their keep — adjust them from evidence, not hindsight.

---

## 10. Honest limitations

- Data is **point-in-time from web search** — and on this horizon that bites harder: crypto funding/OI/social move intraday and a once-daily snapshot can lag the real positioning. Treat prices/levels as approximate and verify before acting.
- **No continuous monitoring and no memory between sessions** — the log lives with you; paste it back each run.
- **This architecture is best suited to ~3–12 week holds re-rated daily.** Pushing toward multi-day or intraday trading is not well-served — you'd need streaming data and faster execution than a daily run provides.
- The quant screen can be backtested (walk-forward, out-of-sample, **real costs — which matter more at this turnover**); the qualitative factors essentially can't — their weights are **priors**, refined via the log.
- Large-cap US equities are fairly efficient; most realized edge will come from risk discipline and cost control, not signal cleverness.
- I generate structured ratings per this system. **I won't execute trades and this isn't personalized financial advice** — the decisions and risk settings are yours.

---

## 11. System change log (spec revisions only)

> **What this is.** A dated history of changes to *this system document* — factor weights, formulas, thresholds, procedures, guardrails. It is the record of how the engine itself evolves over time.
>
> **What this is NOT.** This is **not** the daily run log. Per-run ratings, actions, regime reads, trade rationales, and outcomes go in the **§9 log**, which you carry forward between runs. Nothing about a specific day's trades, holdings, or `R` value belongs here. Rule of thumb: **if an entry names a ticker, a price, or a P&L number, it's in the wrong log.**
>
> **Rules.**
> - One entry per revision, **newest at the top**, dated `YYYY-MM-DD`.
> - Each entry states **what changed**, **which sections**, and **why** (the problem it fixes) — and, where useful, **what was deliberately *not* changed**, so a future reader can tell deliberate scope from oversight.
> - The §0 "last updated" line tracks the **roster**; this log tracks the **system**. Keep the two separate.

---

**2026-07-05 — Horizon retuned to weeks-to-months; asymmetric exit ladder, trend gate, sharpened contrarian trigger, tiered heat caps, diversifier sleeve, operator-override rule.**

*Problem.* Exits capped the right tail (fixed scale-out with no mandated stop progression), entries could knife-catch at full size below all trend structure, the sentiment smile paid near-maximum contrarian credit on mediocre fear readings, the heat cap did not respond to deteriorating hard macro data, the universe concentrated nearly all risk in two correlated clusters, and off-formula trades had no required audit trail.

*Changes.*
- **Header, §1, §4, §5, §7a, §8, §10** — horizon parameters set to ~3–12 week holds: entry persistence **≥ 2 consecutive run-days**, initial stop **2–3 × ATR(14)**, time stop **+1R within ~4–6 weeks**, `Q` staleness docking on a same-day basis, cost hurdle now includes **expected funding over the anticipated hold**.
- **§7d — asymmetric exit ladder.** Every position gets an explicit exit plan at entry: initial ATR stop → **breakeven at +1R** → **⅓–½ partial at +1.5R** → runner trailed at chandelier 2.5–3 × ATR or the 20-day MA; never widen a stop; runners are not converted into fixed targets. The ladder state (current stop + rung) is tracked per position in the §9 `Stop` column and must be updated every run — an open position with no recorded stop is a violation.
- **§5 — trend gate (hard entry/scaling condition, 20/50/200-day MAs):** below the 20-day = no new position; 20–50-day = starter at ½ formula size; above the 50-day = full size (scale starters up on the reclaim); above the 200-day and extended = late-trend caution (no size-ups, tighter trail, early partial). Exits skip the gate. §7b gains the matching starter-scaling rule.
- **§6 — contrarian trigger sharpened:** ±2.0 reserved for true extremes (`P ≥ 95` / `P ≤ 12` or liquidation-cascade days); mid-range fear (25–40) earns only 0 → +0.75; calm-middle momentum credit set to +0.4. Added the **"sentiment scores it, the trend gate times it"** resolution: extreme-fear names hot-list at high conviction but enter on the first daily close back above the 20-day (capitulation → reclaim → entry).
- **§7c + §8 step 1 — growth-scare tiered heat caps:** three hard, anchor-disciplined triggers (payrolls 3-mo trend, 2s10s behavior, HY OAS vs 3-mo low) map to heat-cap tiers 25/20/15/10% of Capital, with high-beta entry restrictions at Tiers 2–3; the active tier is a new §9 run-header field (`GS TIER`).
- **§0 + §7c — diversifier sleeve (Lighter venue tickers):** new roster bucket `XAU, XAG, WTI, BRENTOIL, NATGAS, WHEAT, XCU, EURUSD, USDJPY, AUDUSD, SPY, IWM` and five new correlation clusters (precious metals, energy, ags & industrial, FX, US broad equity), each under the 15% cluster cap; scoring notes (equity weight set reinterpreted, β-tiers) and a **venue-liveness check** (§8 step 3) added. Asia consumer names deliberately excluded for now.
- **§5 — operator-override rule:** any off-formula trade (size, gate, persistence, hurdle, or cap violation) requires explicit operator sign-off and a **`OVERRIDE: <reason>`** tag in the §9 rationale on the opening run and every run it remains open; untagged off-formula positions are flagged and brought back to formula.
- **§7d — transition rule:** positions opened under a prior revision are grandfathered at entry but placed on the exit ladder immediately (current rung per R-progress to date, stop recorded from the next run); if off-formula under current rules they require the §5 `OVERRIDE:` tag or a trim back to formula.

*Deliberately not changed (scope control).* MaxRisk (5%), the conviction formula (§4), factor weights (§2), the regime smile and anchor discipline (§3, §8 step 1), the 15% cluster cap level, and the account-parameter/log mechanics (§8 step 0, §9 header) are untouched — this revision changes exits, entry timing, macro defense, and universe breadth, not the scoring core.

---

**2026-07-04 (b) — §9 log output restructured to native markdown.**

*Problem.* The §9 log was specified as pipe-delimited lines inside a code fence. Rendered, it read as a wall of text with an embedded pseudo-table; if the fence was ever lost in copy/paste, markdown re-interpreted the pipes and mangled the layout. Long run notes crammed into a single pipe field made the header line unreadable.

*Changes.*
- **§9** — the log is now written as native markdown in three parts: a **two-column run-header table** (DATE, CAPITAL, MAXLEV, REGIME R, ANCHOR, ZONE — the machine-readable state §8 step 0 reads), a **free-prose run-notes paragraph** (long text kept out of any table), and a **proper markdown table for asset ratings**. Same fields, same carry-forward role — only the container changed.

*Deliberately not changed.* No fields were added or removed; §8 step 0's read of CAPITAL/MAXLEV is unaffected (it now reads the header table instead of a header line).

---

**2026-07-04 — Sizing made account-size-agnostic; account parameters moved to the run log.**

*Problem.* The spec hard-coded a $100,000 account and fixed dollar amounts throughout §7 (risk-per-trade dollars, a $2,000,000 total notional cap, a $100,000 per-position cap, a dollar cluster figure), so the document only described one account size and the header/§7 disagreed on max leverage (25× vs 20×). It also contained an internal inconsistency: the §7b "$ Risked" column ($500/$400/$300/$2500) contradicted both the sizing formula and the table's own notional/leverage columns.

*Changes.*
- **Header, §7b, §7c, §7d** — all fixed dollar amounts removed. Sizing, caps, and guardrails are now expressed **only in R and fractions of `Capital`** (risk % of Capital, notional as a multiple of Capital, total notional ≤ `MaxLeverage · Capital`, per-position notional ≤ 1× Capital, cluster cap ~15% of Capital at risk), so the identical system applies to any account size.
- **§8 step 0 (new)** — each run begins by reading `Capital` and `MaxLeverage` from the prior run log header. **If no log exists (first run), defaults are $100,000 and 20× max leverage**, recorded into that day's header.
- **§9 log format** — header line gains `CAPITAL=$__ | MAXLEV=__×` fields; the log is now the single source of truth for account parameters between runs.
- **Consistency fixes** — the header's stray "25×" normalized to the log-driven `MaxLeverage` (default 20×); the §7b risk column corrected to the formula-consistent values (5% / 4% / 3% / 2.5% of Capital), which also removes the $2500 typo at the conviction-5 row.

*Deliberately not changed (scope control).* MaxRisk (5%), the 25% heat cap, the ~15% cluster cap, the conviction/sizing formula itself, and all ATR/exit mechanics are untouched — this revision changes the *units and parameter source*, not the risk tolerances.

---

**2026-07-02 — Regime read stabilized against run-timing noise.**

*Problem.* Running the system at different times of the same day produced large swings in the regime read `R`, even though macro regime is a slow-moving, days-to-weeks phenomenon. The cause was measurement, not regime: `R` was set from a live, point-in-time web snapshot whose most volatile inputs (intraday VIX/breadth, live headlines) depended on *when* the run happened, and the hard `|R| ≥ 1.5` smile boundary could invert the sign of the regime term on a tiny wobble.

*Changes.*
- **§8 step 1** — `R` is now computed from data **anchored to the prior daily settlement/close**, one fixed value per day; same-day reruns must reproduce it. A genuine regime break (FOMC, major surprise) may still force a **flagged** off-anchor update. Added **headline discipline**: transient intraday headlines are watch items, not `R` inputs — only scheduled/confirmed or anchor-persistent macro events move the dial (breaking thesis-specific news routes to the §2 Catalyst factor instead).
- **§3 regime smile** — replaced the hard `|R| ≥ 1.5` step with a **linear transition band over 1.3–1.7**. Pure directional below 1.3, pure contrarian above 1.7, smoothly blended between — so a measurement wobble near the old boundary eases the contribution instead of flipping its sign.
- **§9 log line** — now records the **anchor used** and the **smile zone** (core/transition/extreme) so reruns are checkable against each other.

*Deliberately not changed (scope control).* No EWMA / cross-run smoothing of `R` was added — anchoring removes the intraday variance that prompted this fix, and smoothing carries a real risk of over-damping genuine regime breaks. It is parked as a candidate for a later revision *only if* across-day jumpiness turns out to be a separate, observed problem. Factor weights (§2), conviction math (§4), sentiment transform (§6), and sizing/guardrails (§7) were left untouched so the effect of this revision can be read in isolation.
