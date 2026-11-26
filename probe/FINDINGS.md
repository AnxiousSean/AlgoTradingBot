# Phase 0 findings (facts only — updated as probe results arrive)

## Studio static code checker (before the code runs)
- Blocked imports: `sys`, `zoneinfo`.
- Blocked builtin: `getattr`.
- Module-level constants were reported as "undefined variable", so settings go in the strategy `params`.
- Not flagged: `math`, `datetime`, `collections`, `statistics`, `numpy`, `pandas`, `time`.
  (Runtime import success not yet confirmed — needs the `PROBE|ENV` log lines.)

## NAS100.X — Studio backtest, 15m, around 2026-11-11 (summary report only, no PROBE| log yet)
- 6 closed trades = T1, T2, T3, T6, T7, T8. T4/T5 place no fills by design. All tests ran.
- **Value per point:** each trade's P&L = price move × size × **10**, checked on all 6 trades and the
  30.494 total. So size 1.0 = $10 per index point, and size 0.01 = $0.10 per point.
- **Costs:** gross profit = net profit = 30.494 → **no commission charged**. Fills look like plain
  bar prices, so a spread is probably not modelled either (to be confirmed from the BROKER| lines).
  The Studio backtest is optimistic on costs.
- "Total Price" in the orders table = size × price (not margin or $ notional).
- Order timestamps end in `:x4:59` / `:x9:59`. Bars appear to be stamped at bar **end minus 1 s**,
  not bar open. The gap/offset calculation must allow for this.
- Orders were filled at 16:44:59 and 17:29:59. That rules out server = New York time, because the
  17:00–18:00 NY break would show no bars. Exact offset needs the GAP lines.
- The bracket target fills (T7 +85.67 pts, T8 −84.84 pts) are consistent with fills at the 0.3% target
  price set from the signal bar's close.
