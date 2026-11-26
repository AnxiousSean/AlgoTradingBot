# PLATFORM_NOTES — TradeLocker Studio

Status: **Phase 0, waiting for probe results from Studio.** Items marked ❓ are
unknown until `probe_bot.py` has been run in Studio and its log pasted back.
Every later design decision must respect what is recorded here.

## 1. What the official docs say (checked 2026-11-26)

| Topic | Finding | Source |
|---|---|---|
| Language/engine | Python + Backtrader (`import backtrader as bt`, `class X(bt.Strategy)`) | tradelocker.com/how-to/use-a-bot-sizer/ |
| Where Studio runs | "currently only available on our desktop app and **demo environment**" | tradelocker.com/how-to/studio-guide/ |
| Backtest inputs | margin, instrument, resolution, start date, end date | studio-guide |
| Launch inputs | margin, instrument, resolution | studio-guide |
| Order size | Docs speak of `lot_size` / `sizer_lots: 0.27` → size is probably **lots** | use-a-bot-sizer |
| Built-in sizers | FixedLotSizer, FixedCashSizer, AssignedMarginPercentSizer, custom `bt.Sizer` (Desktop ≥ 2.36) | use-a-bot-sizer |
| Params style | dict `params = {...}` in examples | use-a-bot-sizer |
| Code checks | Studio runs unspecified "bot code checks"; they can be disabled per account via `dangerous_policy_violation.txt` | tradelocker.com/how-to/disable-bot-code-checks/ |
| Min lot | 0.01 (platform marketing page) | tradelocker.com/desktop/ |
| Logging, tz, order types, brackets, multi-feed, Python version | **Not documented** | — |
| Strategy storage | "Your strategies are stored locally on your device" | tradelocker.com/studio/ |

Do **not** disable the code checks. We stay inside whatever Studio allows.

## 2. Probe results (fill in from Studio log)

| Question | Local stock Backtrader 1.9.78.123 (reference) | Studio | Design consequence |
|---|---|---|---|
| Backtrader version | 1.9.78.123 | ❓ | |
| Python version / imports allowed | py3.13; all stdlib + numpy/pandas | ❓ | final bot uses only backtrader/math/datetime regardless |
| print() visible? | yes | ❓ | |
| Data timezone | n/a (synthetic UTC) | ❓ (week-open bar time + hourly range profile) | |
| Bar resolution = chart resolution? | n/a | ❓ | |
| Bar timestamp = bar open or close? | n/a | ❓ | |
| `getvalue()` includes open P&L (equity)? | yes (ratio ≈ mult) | ❓ | daily guard source |
| `getvalue()` starting value = "margin" setting? | n/a | ❓ | |
| `size` meaning | depends on comminfo | ❓ (0.01 vs 1000 test, implied multiplier) | |
| Commission charged in backtest | configurable | ❓ | |
| Market order fill | next bar open | ❓ | |
| Stop entry / Limit entry | work | ❓ | |
| cancel() | works | ❓ | |
| buy_bracket / sell_bracket (OCO) | work, other leg auto-cancels | ❓ | |
| StopTrail | works | ❓ | |
| close() leaves separate stop order alive (orphan) | **yes — must cancel manually** | ❓ | |
| Opposite order nets position (no hedge) in backtest | yes | ❓ | live may differ! |
| `broker.get_orders_open()` | works | ❓ | |
| Indicators EMA/SMA/ATR/ADX/DMI/BB/Highest/Lowest/RSI/MACD/MACDHisto/CrossOver/Stochastic | all OK, MACDHisto has `.histo`, plain MACD does not | ❓ | |
| Number of data feeds / resampledata | 1 / available on cerebro | ❓ | |
| `add_timer` | available | ❓ | |

## 3. Local Backtrader pitfalls already found

1. **`setcommission(leverage=...)` double-counts open P&L in `getvalue()`** for
   futures-style (non-stocklike) commission. Measured d(value)/d(size·price)
   = 199,011 instead of 100,000. The local harness models FX with
   `mult=100000, margin=<per-lot margin>, stocklike=False` and **no** `leverage=`.
2. Stock Backtrader **crashes (IndexError) when the data has fewer bars than the
   longest indicator warm-up** (e.g. EMA200 on a 150-bar backtest). Studio
   backtests must cover enough bars; the final bot must also survive short
   histories (guard or compute indicators manually).
3. `close()` does not cancel a pending protective stop. Any "manual stop"
   design must cancel its own stop when it closes, or an orphan stop can later
   open a position in the opposite direction.
4. `bt.indicators.MACD` has no `histo` line; only `MACDHisto` does.

## 4. Open questions for the user / GFT / TradeLocker
See `GFT_RULES.md` §Open questions.
