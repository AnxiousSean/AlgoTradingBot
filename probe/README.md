# Phase 0 — Studio capability probe

`probe_bot.py` is a tiny test bot, not a strategy. It reports which Python and Backtrader features
TradeLocker Studio actually supports, so later phases are built on facts instead of assumptions.

**Run it only in the Studio backtester, or on a TradeLocker DEMO account. Never on the GFT account.**

## How to run it in Studio

1. Create a new bot in Studio and paste in the whole of `probe_bot.py`. If Studio's template needs a
   specific class name, rename `ProbeStrategy` and tell me what the name was.
2. Do 2 backtests (or 3 if you can):
   | Run | Instrument | Resolution | Dates | Why |
   |---|---|---|---|---|
   | A | XAUUSD | 5m | **2026-02-15 → 2026-04-15** | covers US DST start (8 Mar) and EU DST start (29 Mar), so we can see whether server time shifts |
   | B | NAS100 (or US100) | 5m | same dates | value per point, index session times |
   | C (optional) | XAUUSD | 15m | 2026-10-15 → 2026-11-20 | covers the US DST end (1 Nov) |
   Leave margin at the default. Write down any spread, commission or slippage fields the backtest
   settings show, even if they are blank.
3. Copy the full log. If it's too long, paste: every line before the first `PROBE|BAR`, the first
   60 `PROBE|BAR` lines, 15 or so `PROBE|GAP` lines, every `ORDER`/`FILL`/`TRADE`/`MEASURE`/`FLOAT`
   line, and the whole `PROBE|SUMMARY` block.
4. If every order says `Rejected` or `Margin`, change `PROBE_SIZE` (try `1`, then `0.1`) and run it again.
   Tell me which value worked.

## What to read from the log (checklist)

| # | Look for | It tells us |
|---|---|---|
| 1 | `ENV|python=`, `ENV|backtrader=` | which versions to pin locally |
| 2 | `ENV|import ... -> OK/FAIL` | which modules the final bot may use (numpy? zoneinfo for DST?) |
| 3 | `DATA|len(self.datas)` | whether there's more than one feed (multi-timeframe) or only one |
| 4 | `BROKER|param slip_*`, `COMMINFO|commission/mult/margin/leverage` | whether Studio models costs at all; how `size` maps to money |
| 5 | `BAR|` lines | the timestamp format, and whether timestamps carry a timezone |
| 6 | `GAP|` lines + `SUMMARY|implied server-minus-UTC offset votes` | **server timezone**. Gold and NAS100 CFDs pause at 17:00 New York, so the time of each pause gives the server's UTC offset. Check whether the vote changes after 8 Mar / 29 Mar |
| 7 | `FLOAT|` lines / `T1_MARKET` result | whether `getvalue()` includes floating P&L (ratio ≈ the per-point value means yes, 0 means no), and how `getcash()` behaves with an open position |
| 8 | `MEASURE|` / `SUMMARY|value per 1.0 price move per 1 size unit` | **value per point per unit**. Example: if it says 100 on XAUUSD, then size=1 means 100 oz (1 lot) |
| 9 | `SUMMARY|note: market order ...` | whether market orders fill at the next bar's open (realistic) or at the signal bar's close (optimistic) |
| 10 | T2 / T3 `fill=` | how stop and limit entries fill: `AT_TRIGGER_PRICE` = intrabar at the order price; `AT_BAR_OPEN` only = gap fill at the open; `AT_BAR_CLOSE` = fills only at bar close |
| 11 | T4, T5 | whether `self.cancel()` and `valid=` expiry work |
| 12 | T6 | whether `oco=` is supported natively (`auto-cancelled by platform: True`). A `SAFETY|... cancelling manually` line means it isn't |
| 13 | T7, T8 | whether `buy_bracket` / `sell_bracket` work, how the stop child fills, and whether the sibling gets cancelled |
| 14 | `IND|` lines | which indicators exist. Note: stock Backtrader's `MACD` has no `histo` line either (it lives on `MACDHisto`), so that public-bot finding wasn't specific to Studio |
| 15 | any `EXCEPTION` / `FAIL` / `ERR` | something unsupported. Paste these exactly |

## Also check in the TradeLocker UI (the probe can't see these)

For **XAUUSD** and **NAS100** on your GFT account (open the instrument info / symbol specification):
- exact symbol names as listed (e.g. `XAUUSD`, `NAS100`, `US100`, `USTEC`)
- minimum trade size, size step, and contract size (e.g. 1 lot = 100 oz)
- tick size and tick value
- typical spread at London open and at NY open (a screenshot is fine)
- commission per lot, if any
- the leverage shown on the account (expected 1:20 for indices/commodities in eval)
- whether you can export history (CSV) from TradeLocker, for Phase 1 data

## Optional: short live demo run
If you're willing, also **Launch** the probe on a *demo* account for about an hour while gold is
trading. `CLOCK|machine now` versus the live `BAR|` timestamps tells us the live server offset
directly, and the fills show live slippage. Then stop the bot from the Bots Panel.
