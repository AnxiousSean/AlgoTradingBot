# SCALP research report (many small trades)

Generated 2026-11-27 19:15 from 5094353 1-minute bars, 2010-11-14 23:02:00 to 2026-11-13 21:14:00 UTC. In-sample before 2022-01-25 NY, out-of-sample after. 22 backtests in 5320 s.

Strategy: 1-minute trend pullback. Long when EMA9 > EMA50 and a bar dips to EMA9 and closes above it as an up-bar (short = mirror). Stop beyond that bar by 0.5 x ATR(14) (at least 0.03% of price), target 1R placed after the 2-minute minimum hold, exit after 15 minutes, 5-minute pause between trades, max 10 trades a day, 0.25% ($12.50) risk per trade, entries 09:45-15:00 NY. Costs: 2.5 points round trip at NAS100 30,000 (scaled with price); 1.5x = 3.75 points.

Each calendar year is simulated as a fresh $5,000 account (indicators warmed up on the previous 45 days, whose trades are dropped), so a losing year cannot drain the account and stop later years from trading.

## Out-of-sample

| Config | Trades | Win % | Avg win R | Avg loss R | Exp. R | PF | Net % | Max DD % | Worst day % | Lose streak |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SCALP 1m NO COSTS | 10840 | 48.3 | 1.02 | -0.96 | -0.006 | 0.99 | -9.77 | 16.71 | 1.67 | 12 |
| SCALP 1m 1.0x | 10838 | 47.9 | 0.93 | -1.05 | -0.099 | 0.83 | -192.80 | 194.07 | 1.73 | 12 |
| SCALP 1m target 0.5R 1.0x | 10832 | 58.9 | 0.57 | -1.07 | -0.104 | 0.77 | -214.20 | 214.45 | 1.62 | 8 |
| SCALP 1m target 2R 1.0x | 10832 | 38.0 | 1.38 | -1.02 | -0.107 | 0.84 | -207.23 | 208.93 | 1.92 | 17 |
| SCALP 3m 1.0x | 9859 | 48.7 | 0.71 | -0.80 | -0.067 | 0.84 | -120.56 | 120.92 | 1.66 | 12 |
| SCALP 1m 1.5x | 10804 | 47.8 | 0.89 | -1.09 | -0.145 | 0.77 | -260.55 | 261.53 | 1.80 | 14 |
| SCALP 1m target 0.5R 1.5x | 10802 | 58.9 | 0.53 | -1.12 | -0.149 | 0.70 | -275.45 | 275.65 | 1.72 | 9 |
| SCALP 1m target 2R 1.5x | 10765 | 37.5 | 1.35 | -1.06 | -0.156 | 0.78 | -269.60 | 270.76 | 2.02 | 16 |
| SCALP 3m 1.5x | 9853 | 47.8 | 0.69 | -0.82 | -0.098 | 0.78 | -176.85 | 177.09 | 1.68 | 14 |
| SCALP RANDOM seed1 1.0x | 10824 | 47.5 | 0.94 | -1.11 | -0.136 | 0.82 | -201.98 | 205.36 | 1.73 | 22 |
| SCALP RANDOM seed2 1.0x | 10832 | 47.9 | 0.94 | -1.11 | -0.125 | 0.84 | -181.49 | 184.00 | 1.79 | 12 |
| SCALP RANDOM seed3 1.0x | 10840 | 47.3 | 0.93 | -1.11 | -0.146 | 0.81 | -206.30 | 207.55 | 1.84 | 16 |

## In-sample

| Config | Trades | Win % | Avg win R | Avg loss R | Exp. R | PF | Net % | Max DD % | Worst day % | Lose streak |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SCALP 1m NO COSTS | 27810 | 48.2 | 1.06 | -0.96 | 0.014 | 1.02 | 48.33 | 29.99 | 1.61 | 13 |
| SCALP 1m 1.0x | 27807 | 47.8 | 0.93 | -1.08 | -0.117 | 0.82 | -461.96 | 462.34 | 1.83 | 13 |
| SCALP 1m target 0.5R 1.0x | 27807 | 58.7 | 0.58 | -1.11 | -0.118 | 0.77 | -478.24 | 478.24 | 1.82 | 10 |
| SCALP 1m target 2R 1.0x | 27803 | 37.9 | 1.45 | -1.06 | -0.107 | 0.86 | -394.12 | 395.79 | 2.01 | 20 |
| SCALP 3m 1.0x | 25162 | 47.4 | 0.75 | -0.83 | -0.080 | 0.82 | -361.45 | 362.76 | 1.79 | 15 |
| SCALP 1m 1.5x | 27759 | 47.5 | 0.88 | -1.14 | -0.183 | 0.73 | -654.88 | 655.17 | 1.84 | 13 |
| SCALP 1m target 0.5R 1.5x | 27778 | 58.2 | 0.52 | -1.16 | -0.182 | 0.67 | -666.35 | 666.35 | 1.92 | 14 |
| SCALP 1m target 2R 1.5x | 27757 | 37.2 | 1.41 | -1.11 | -0.175 | 0.79 | -591.13 | 592.53 | 2.10 | 22 |
| SCALP 3m 1.5x | 25160 | 46.2 | 0.72 | -0.85 | -0.123 | 0.75 | -530.57 | 531.64 | 1.87 | 15 |
| SCALP RANDOM seed1 1.0x | 27800 | 47.8 | 0.93 | -1.08 | -0.121 | 0.81 | -481.68 | 482.68 | 1.99 | 14 |
| SCALP RANDOM seed2 1.0x | 27803 | 47.8 | 0.92 | -1.08 | -0.123 | 0.81 | -473.51 | 475.45 | 1.85 | 14 |
| SCALP RANDOM seed3 1.0x | 27810 | 48.3 | 0.92 | -1.08 | -0.112 | 0.82 | -437.32 | 440.84 | 2.13 | 13 |

## Monte Carlo (out-of-sample, 1.5x costs, 10000 runs, Step 1 target 8%)

| Config | Pass % | Firm breach % | Bot -7% stop % | Unfinished % | Median days to pass | Verdict |
|---|---:|---:|---:|---:|---:|---|
| SCALP 1m 1.5x | 0.0 | 0.0 | 100.0 | 0.0 | - | NOT READY: PF 0.77 < 1.25; max DD 261.53% > 6.0% |
| SCALP 1m target 0.5R 1.5x | 0.0 | 0.0 | 100.0 | 0.0 | - | NOT READY: PF 0.70 < 1.25; max DD 275.65% > 6.0% |
| SCALP 1m target 2R 1.5x | 0.1 | 0.0 | 99.9 | 0.0 | 23 | NOT READY: PF 0.78 < 1.25; max DD 270.76% > 6.0% |
| SCALP 3m 1.5x | 0.0 | 0.0 | 100.0 | 0.0 | - | NOT READY: PF 0.78 < 1.25; max DD 177.09% > 6.0% |

## Real signal vs random direction (1x costs)

- Out-of-sample: real -0.099 R over 10838 trades; random -0.136, -0.125, -0.146 (mean -0.136); real beats 3 of 3.
- In-sample: real -0.117 R over 27807 trades; random -0.121, -0.123, -0.112 (mean -0.119); real beats 2 of 3.

## Robustness: parameters +-20% (IN-SAMPLE, 1x costs)

| Config | Trades | Win % | Avg win R | Avg loss R | Exp. R | PF | Net % | Max DD % | Worst day % | Lose streak |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BASE (defaults) | 27807 | 47.8 | 0.93 | -1.08 | -0.117 | 0.82 | -461.96 | 462.34 | 1.83 | 13 |
| SCALP_FAST_EMA 9 -> 7 | 27808 | 47.6 | 0.94 | -1.07 | -0.116 | 0.81 | -474.95 | 475.83 | 1.76 | 12 |
| SCALP_FAST_EMA 9 -> 11 | 27798 | 47.9 | 0.93 | -1.08 | -0.121 | 0.81 | -467.71 | 468.63 | 1.72 | 14 |
| SCALP_SLOW_EMA 50 -> 40 | 27801 | 47.6 | 0.94 | -1.08 | -0.120 | 0.81 | -473.93 | 474.54 | 1.82 | 14 |
| SCALP_SLOW_EMA 50 -> 60 | 27808 | 48.0 | 0.93 | -1.08 | -0.113 | 0.82 | -453.41 | 454.28 | 1.83 | 12 |
| SCALP_STOP_ATR 0.5 -> 0.4 | 27804 | 47.4 | 0.96 | -1.10 | -0.121 | 0.81 | -460.42 | 460.72 | 1.88 | 14 |
| SCALP_STOP_ATR 0.5 -> 0.6 | 27810 | 48.2 | 0.91 | -1.06 | -0.109 | 0.82 | -457.15 | 457.68 | 1.83 | 16 |
| SCALP_TARGET_R 1.0 -> 0.8 | 27806 | 51.7 | 0.79 | -1.09 | -0.120 | 0.80 | -474.50 | 474.50 | 1.79 | 12 |
| SCALP_TARGET_R 1.0 -> 1.2 | 27809 | 44.7 | 1.07 | -1.07 | -0.115 | 0.83 | -455.55 | 456.93 | 1.78 | 16 |
| SCALP_MAX_HOLD_MIN 15 -> 12 | 27808 | 47.3 | 0.92 | -1.05 | -0.117 | 0.81 | -461.46 | 462.37 | 1.73 | 16 |
| SCALP_MAX_HOLD_MIN 15 -> 18 | 27808 | 47.9 | 0.95 | -1.10 | -0.119 | 0.82 | -469.96 | 470.45 | 1.79 | 13 |

## Exit reasons and cost share (full period)

- **SCALP 1m NO COSTS**: 38650 trades; STOP 16504, STOP_IN_FILL_BAR 2114, TARGET 14095, TARGET_PASSED 3193, TIME_STOP 2744; median hold 4 min; 2114 adjusted for stop-in-fill-bar
- **SCALP 1m 1.0x**: 38645 trades; STOP 16502, STOP_IN_FILL_BAR 2114, TARGET 14090, TARGET_PASSED 3194, TIME_STOP 2745; median hold 4 min; 2114 adjusted for stop-in-fill-bar
- **SCALP 3m 1.0x**: 35021 trades; STOP 10909, STOP_IN_FILL_BAR 290, TARGET 9635, TARGET_PASSED 1138, TIME_STOP 13049; median hold 11 min; 290 adjusted for stop-in-fill-bar

## Acceptance (OOS, 1.5x costs: >=100 trades, PF >= 1.25, max DD <= 6%, worst day <= 2.5%, MC breach < 15%)

- SCALP 1m 1.5x: **NOT READY: PF 0.77 < 1.25; max DD 261.53% > 6.0%**
- SCALP 1m target 0.5R 1.5x: **NOT READY: PF 0.70 < 1.25; max DD 275.65% > 6.0%**
- SCALP 1m target 2R 1.5x: **NOT READY: PF 0.78 < 1.25; max DD 270.76% > 6.0%**
- SCALP 3m 1.5x: **NOT READY: PF 0.78 < 1.25; max DD 177.09% > 6.0%**
