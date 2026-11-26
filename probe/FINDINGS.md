# Phase 0 findings (facts from probe runs; updated as results arrive)

Sources: Studio static checker messages; NAS100.X 15m summary report (~2026-11-11);
XAUUSD.X 5m full log, 2026-11-11 → 2026-11-25, Studio release 3.21.48.

## Code environment
| Item | Result |
|---|---|
| Backtrader | **1.9.78.123** (stock version number) wrapped by `tl_bt_adapter` (TLData, TLBackBroker, TLCommInfo) |
| Blocked by static checker | imports `sys`, `zoneinfo`; builtin `getattr`; module-level constants flagged as "undefined" → use strategy `params` |
| Imports that work at runtime | `math`, `datetime`, `collections`, `statistics`, `numpy`, `pandas`, `time` |
| Logging | `print()` appears in the Studio log. No built-in `self.log` |
| Studio's own log | prints every order Submitted/Accepted/Completed/Canceled itself |
| Settings | strategy `params` show up as `strategyParamsInput` in the backtest config |
| Default sizer | `TLLotSizer` → `size` is in **lots** |

## Data feed
| Item | Result |
|---|---|
| Feeds | **one** (`len(self.datas)=1`), so no multi-timeframe. Daily values (ATR, EMA, prior-day close) must be built from intraday bars in our own code |
| Lines | `open high low close volume openinterest datetime` **+ `ask bid mid`** |
| Timezone | feed `tz=UTC`. Confirmed: Studio's own log prints the same instant in −0800 local time (bar 03:09:59 = 19:09:59 −0800) |
| Bar stamp | **bar END**, e.g. `03:09:59.999` is the bar from 03:05 to 03:10 |
| Session break (XAUUSD, Nov = NY standard time) | last bar ends 22:00 UTC, next opens 23:00 UTC → 17:00–18:00 New York. ✓ UTC. Weekly: Fri 22:00 UTC → Sun 23:00 UTC. A stray single bar at Fri 23:55–24:00 appears; ignore bars after Friday's close |
| Volume | tick-volume-like (~2,000 per 5m bar) |
| History | the run covered 2 weeks; whether Studio allows longer ranges is still unknown |

## Broker / fills (Studio backtest)
| Item | Result |
|---|---|
| Commission | `commission=0.0` in the backtest config (the field exists); NAS100 report: gross = net |
| Slippage | `slip_perc=0`, `slip_fixed=0` → none |
| Spread | fills are at plain OHLC prices, so **no spread is charged** even though bid/ask exist (to be quantified by probe v2) |
| `getvalue()` | **equity**, i.e. includes floating P&L |
| `getcash()` | drops by margin while a position is open (0.01 lot XAUUSD @4047.77 → $80.96 = 2% → Studio models 1:50 on gold, not GFT's 1:20) |
| Market orders | fill at the **next bar's open** (no look-ahead) |
| Stop entry | fills **intrabar at the trigger price** (no gap case seen yet; assume gap → fill at open) |
| Limit entry | fills at the limit price |
| `self.cancel()` | works |
| `valid=timedelta` | works (expired after 3 bars) |
| `oco=` | **native**: the other leg is cancelled by the platform in the same step |
| `buy_bracket` / `sell_bracket` | work. Stop child fills intrabar at the stop price, target at the limit price, sibling auto-cancelled |
| Price rounding | Studio **truncates** order prices to tick 0.01 (4048.73777 → 4048.73). The bot must round prices itself, always in the safe direction |
| Indicators | ATR, EMA, SMA, Highest, Lowest, RSI, TrueRange, MACD, MACDHisto all work. `MACD` has no `histo` (same as stock; use `MACDHisto`) |

## Instrument economics (Studio backtest)
| Symbol | Value of 1.0 price move per 1.0 lot | 0.01 lot | Notes |
|---|---|---|---|
| XAUUSD.X | **$100** (1 lot = 100 oz) | $1 per $1 move | TLCommInfo reports `lot_step=0.1`, `tick_size=0.1`, `lot_size=1.0`, yet 0.01 lots and 0.01 price ticks were accepted. **Real min size / step must be confirmed in the TradeLocker UI** |
| NAS100.X | **$10** per index point | $0.10 per point | from the summary report; verified on all 6 trades |

## Sizing implications ($5,000 account; not yet a Phase 1 result)
- XAUUSD at 0.01 lot = $1 per $1. A 0.6%-of-price stop (~$24) risks ~$24 = 0.48% at the minimum size.
  At 0.25% risk ($12.50) only stops ≤ $12.50 (~0.31% of price) are tradable. Steps are coarse
  (0.01 → 0.02 lots doubles the risk).
- If the real XAUUSD lot step is **0.1** (= $10 per $1), gold is effectively untradable at $5k:
  0.5% risk would allow only a $2.50 stop.
- NAS100 at 0.01 = $0.10/pt: 0.5% risk allows a 250-pt stop at minimum size, with fine steps after that.
