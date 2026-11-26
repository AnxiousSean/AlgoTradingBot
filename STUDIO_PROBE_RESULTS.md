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
- Pasting: copy the file from a plain-text editor. Earlier failures were caused by the paste
  changing indentation and cutting off the end of the file, not by Studio.

## NAS100.X (15m, 2026-09-26 to 2026-11-26)
- **Value per point per 1 lot = $10** (0.01 lot = $0.10 per point). Trade P&L matches exactly.
- Tick size 0.01. Broker commission info: leverage 50, commission 0.
- 1 lot at 30,000 = $300,000 notional = $6,000 margin at 1:50. With the 30% margin cap,
  the largest possible position on $5,000 is 0.25 lots.
- Typical risk-based size: $25 risk / (52-point stop x $10) = 0.04 lots (risks $20.80;
  rounding down to 0.01 lots under-risks a little, never over-risks).
- Market orders fill at the next bar's open. No spread difference between buy and sell fills
  was visible, so Studio backtests are cost-free unless we add commission.
- Bars are present around the clock on weekdays (UTC); the US cash session is
  13:30-20:00 UTC in summer time and 14:30-21:00 UTC in winter time. The guard handles the switch.
