# Stage 0: Studio probe results

Run: ETHUSD.X, 5m, 2026-11-12 to 2026-11-26, margin 5000, Studio release 3.21.48.

## Supported (all OK)
| Feature | Result |
|---|---|
| `import math`, `import datetime` | OK |
| Strategy params | OK (shown as editable inputs in the backtest config) |
| `print()` | OK. Pass ONE string; several arguments are joined without spaces |
| Module-level functions and plain classes | OK (PropRiskGuard can live outside the strategy) |
| Custom methods on the strategy class | OK |
| EMA(5/200/800), RSI(2, safediv=True), RSI_Safe, ATR, SMA, Highest, Lowest, CrossOver, MACD, MACDHisto `.histo` | OK |
| Market buy / sell (shorts) | OK |
| Stop orders (protective and entry) | OK |
| Limit orders | OK |
| `buy_bracket` (3 orders: main, stop, limit) | OK |
| OCO (`oco=`) | OK: filled buy stop auto-cancelled the sell stop |
| `cancel()`, `close()`, `getposition()` | OK |
| `notify_order`, `notify_trade` (pnl, pnlcomm) | OK |
| `broker.getvalue()`, `broker.getcash()` | OK |

## Facts the bot must respect
- **Timestamps are naive UTC and mark the bar CLOSE** (e.g. `00:04:59.999006` = bar 00:00 to 00:05).
  Studio's own order log prints the same moments in your PC's local time (-0800).
  The bot uses `DATA_TIMEZONE="UTC"` and treats each timestamp as the bar end.
- **Order size is in lots** (0.01 accepted; default sizer `TLLotSizer` honours explicit sizes).
- **Studio rounds stop/limit prices DOWN to the tick size** (1993.9805 -> 1993.98) and warns.
  The bot will round prices itself, always in the safer direction (stop further away is never
  allowed to exceed the planned risk check; see TICK_SIZE setting).
- **Commission is 0 in the backtest config and no spread was visible**, so Studio results
  will look better than reality. Costs are modelled in the local harness.
- ETHUSD.X: value per point per 1 lot = 1.0; broker commission info reports leverage 50.
  **Nasdaq values still to be measured** (run the probe on the Nasdaq CFD, 15m).
- Pasting: copy the file from a plain-text editor. Earlier failures were caused by the paste
  changing indentation and cutting off the end of the file, not by Studio.
