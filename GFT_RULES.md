# GFT 2-Step GOAT — rules as verified on help.goatfundedtrader.com (2026-11-26)

Sources: help.goatfundedtrader.com/2-step-goat.html (updated 25 Nov 2026),
/trading-rules.html, /platforms.html, /goat-guard.html.
Caveat: long pages were read via an extracted summary; re-check exact wording
before relying on edge cases. **Where my brief and the site differ, the bot
follows whichever is stricter.**

| Rule | Brief said | Site says | Bot implements |
|---|---|---|---|
| Targets | 8% / 6% | 8% / 6% / funded none | same |
| Profitable days | ≥3 per phase | ≥3 per phase; a "profitable day" = ≥ **0.5% of initial balance ($25) net** of fees, with ≥1 closed position | count only days ≥ +$25 net |
| Daily loss | 4% vs balance at 5 PM NY, on equity | 4%; at 5:00 PM "EST" they take the **higher of balance or equity** as the day's base | base = max(balance, equity) at 5 PM New York (DST-aware); buffers 1.5% / 2.5% |
| Max loss | 10% static ($4,500) | 10% static of initial size | floor at 7% ($4,650) |
| Hedging | banned | banned, incl. across your own accounts; permanent ban | assert never opposite on a symbol; one bot per symbol |
| Martingale/grid | banned | banned (incl. grid recovery) | fixed-fraction sizing only |
| HFT | banned | banned, no numeric threshold | H1/H4/M15 bars, ≤2 entries/pair/day |
| Tick scalping | banned | not found on site | n/a (we don't) |
| Margin | <80% | margin used ÷ equity >80% = "all-or-nothing" | <50% check before each order |
| News | profit capped within 5 min | allowed; profit from trades opened/closed within ±5 min of red-folder release capped at **3%** of initial per release (accounts bought ≥10 Nov 2026; 1% before); **applies in challenge AND funded** | ±15 min entry blackout |
| Min hold (funded) | 60 s | 60 s (bought ≥6 Oct 2026; 120 s before); profit removed, not a breach | H1-bar strategies; never close < 2 min |
| Weekend | Fri last 3h / Mon first 3h reviewed | holding allowed; that window reviewed, funded profit removed | flat by Fri 20:00 UTC, no entries after 17:00 UTC |
| VPS / hosting | banned | VPN, VPS, proxies, any hosting banned (from 6 Oct 2026) | see open question 2 |
| EA ownership | — | own-developed EAs only; source may be requested | clean git history |
| Inactivity | — | **no trade for 30 days = breach** | alert if no trade in 21 days |
| Leverage | — | FX 1:100 evaluation, 1:50 funded | margin model per phase |
| Commission | (you'll give) | "$5 for FX pairs and metals with raw spread" per lot — per side or round trip **not stated** | assume **$5 per side** ($10 round trip) until confirmed |
| Consistency rule | — | none on 2-Step GOAT | — |
| Max daily profit | — | funded only: $3,000 (excess deducted, no breach) | irrelevant at $5k |
| Goat Guard | — | off in evaluation; funded: combined floating loss ≥2% of initial → split 50%, second time = breach | funded mode must cap open risk < 2% total |
| 1% floating-loss add-on | — | optional checkout toggle; combined floating loss ≥1% of initial = **instant breach** in every phase | see open question 1 |

## Open questions (please answer before Phase 2)

1. **Did you enable the "1% Floating Loss Limit" option at checkout?** If yes,
   total open loss may never reach $50 on a $5k account. That rules out most
   of the planned risk levels and needs its own guard.
2. **Where does a Studio bot actually run?** If it runs inside the TradeLocker
   desktop app on your PC, that fits the "no VPS/hosting" rule. If TradeLocker
   runs it server-side, ask GFT support whether it counts as "hosting". Also
   run the desktop app on the Windows host, with no VPN.
3. **Is Studio available on your GFT TradeLocker account?** The TradeLocker
   docs say Studio is "currently only available on our desktop app and demo
   environment". If it can't launch on the GFT evaluation account, the whole
   plan needs a different execution route.
4. Commission: open a 0.01-lot demo trade on GFT TradeLocker and note the
   commission shown on open and on close. That tells us per side vs. round trip.
5. Is the 5 PM reset "EST" meant as New York local time (DST-adjusted)? Assumed yes.
