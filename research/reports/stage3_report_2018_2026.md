# Stage 3 research report (2018-2026, 1-minute execution)

Generated 2026-11-27 06:22 from `data/NAS100_1m_2018.csv`, 2814888 1-minute bars, 2018-01-01 21:31:00 to 2026-11-13 21:14:00 UTC.
In-sample: before 2024-03-17 07:43 NY. Out-of-sample: after. OOS trading days in Monte Carlo pool: 684.
Costs: 1x = 2.5 points round trip at NAS100 30,000 (scaled with price, e.g. about 0.5 points at 6,300 in 2018), 1.5x = 3.75 points. Risk 0.5% ($25) per trade, 1:20 leverage, 30% margin cap. 42 backtests in 1922 s.

Data source: HistData.com NSXUSD 1m bars (same feed as Dukascopy USATECHIDXUSD; not TradeLocker's feed, but matches NAS100.X within a few points, see data_check.md).

## Out-of-sample

| Config | Trades | Win % | Avg win R | Avg loss R | Exp. R | PF | Net % | Max DD % | Worst day % | Lose streak |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| RSI2 15m 1.0x | 586 | 56.8 | 0.60 | -0.93 | -0.059 | 0.85 | -14.30 | 18.28 | 1.47 | 6 |
| RSI2 1H 1.0x | 213 | 50.2 | 0.81 | -0.85 | -0.015 | 0.99 | -0.42 | 5.73 | 1.36 | 7 |
| RSI2 15m slowEMA800 1.0x | 487 | 56.5 | 0.62 | -0.94 | -0.063 | 0.84 | -13.50 | 18.64 | 1.47 | 6 |
| ORB 5m range-stop 1.0x | 363 | 35.3 | 2.27 | -1.02 | 0.143 | 1.17 | 15.76 | 7.75 | 1.36 | 10 |
| ORB 5m atr-stop 1.0x | 363 | 22.9 | 3.92 | -1.05 | 0.083 | 1.11 | 13.84 | 17.65 | 1.15 | 23 |
| ORB 5m range-stop 2R 1.0x | 363 | 41.0 | 1.74 | -1.02 | 0.114 | 1.18 | 14.97 | 6.92 | 1.36 | 10 |
| ORB RANDOM seed1 1.0x | 318 | 32.7 | 2.44 | -1.00 | 0.125 | 1.18 | 14.34 | 8.06 | 1.02 | 11 |
| ORB RANDOM seed2 1.0x | 323 | 32.2 | 2.30 | -1.00 | 0.065 | 1.19 | 15.18 | 8.16 | 0.51 | 13 |
| ORB RANDOM seed3 1.0x | 313 | 30.7 | 2.35 | -1.00 | 0.028 | 1.07 | 6.06 | 8.76 | 0.57 | 9 |
| ORB RANDOM seed4 1.0x | 318 | 28.6 | 2.14 | -0.99 | -0.098 | 0.90 | -8.04 | 13.05 | 0.57 | 17 |
| ORB RANDOM seed5 1.0x | 314 | 30.9 | 2.43 | -1.01 | 0.052 | 1.07 | 5.97 | 14.73 | 1.36 | 8 |
| RSI2 15m 1.5x | 586 | 56.1 | 0.60 | -0.93 | -0.074 | 0.82 | -17.92 | 21.15 | 1.50 | 6 |
| RSI2 1H 1.5x | 213 | 50.2 | 0.80 | -0.86 | -0.025 | 0.96 | -1.20 | 5.97 | 1.38 | 7 |
| RSI2 15m slowEMA800 1.5x | 487 | 55.6 | 0.61 | -0.94 | -0.079 | 0.80 | -16.55 | 20.23 | 1.50 | 6 |
| ORB 5m range-stop 1.5x | 363 | 35.0 | 2.28 | -1.03 | 0.128 | 1.14 | 13.65 | 8.57 | 1.36 | 10 |
| ORB 5m atr-stop 1.5x | 363 | 22.6 | 3.94 | -1.08 | 0.057 | 1.07 | 9.73 | 18.29 | 1.16 | 23 |
| ORB 5m range-stop 2R 1.5x | 363 | 40.8 | 1.73 | -1.03 | 0.099 | 1.15 | 12.84 | 7.18 | 1.36 | 10 |
| ORB RANDOM seed1 1.5x | 318 | 32.7 | 2.43 | -1.02 | 0.110 | 1.15 | 12.50 | 8.57 | 1.02 | 11 |
| ORB RANDOM seed2 1.5x | 323 | 31.9 | 2.31 | -1.01 | 0.050 | 1.16 | 13.37 | 8.39 | 0.52 | 13 |
| ORB RANDOM seed3 1.5x | 313 | 30.7 | 2.34 | -1.02 | 0.013 | 1.05 | 4.29 | 9.14 | 0.58 | 9 |
| ORB RANDOM seed4 1.5x | 318 | 28.6 | 2.12 | -1.01 | -0.113 | 0.89 | -9.83 | 13.27 | 0.58 | 17 |
| ORB RANDOM seed5 1.5x | 314 | 30.6 | 2.44 | -1.02 | 0.037 | 1.05 | 4.20 | 15.29 | 1.36 | 8 |

## In-sample

| Config | Trades | Win % | Avg win R | Avg loss R | Exp. R | PF | Net % | Max DD % | Worst day % | Lose streak |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| RSI2 15m 1.0x | 1399 | 56.7 | 0.70 | -0.95 | -0.015 | 0.97 | -6.42 | 19.15 | 1.58 | 6 |
| RSI2 1H 1.0x | 489 | 48.1 | 0.78 | -0.83 | -0.057 | 0.86 | -12.03 | 16.37 | 1.46 | 8 |
| RSI2 15m slowEMA800 1.0x | 1154 | 55.7 | 0.71 | -0.95 | -0.026 | 0.95 | -11.21 | 19.88 | 1.55 | 6 |
| ORB 5m range-stop 1.0x | 738 | 32.4 | 2.85 | -1.01 | 0.238 | 1.30 | 62.94 | 9.68 | 0.52 | 13 |
| ORB 5m atr-stop 1.0x | 738 | 21.3 | 5.89 | -1.05 | 0.429 | 1.56 | 147.43 | 12.13 | 0.54 | 17 |
| ORB 5m range-stop 2R 1.0x | 738 | 37.1 | 1.81 | -1.02 | 0.032 | 1.01 | 2.41 | 12.04 | 0.52 | 10 |
| ORB RANDOM seed1 1.0x | 645 | 29.9 | 2.54 | -1.01 | 0.052 | 1.05 | 10.11 | 13.07 | 0.52 | 17 |
| ORB RANDOM seed2 1.0x | 654 | 30.6 | 2.61 | -1.00 | 0.103 | 1.11 | 21.27 | 9.72 | 0.52 | 19 |
| ORB RANDOM seed3 1.0x | 651 | 30.1 | 2.57 | -1.00 | 0.078 | 1.09 | 16.74 | 13.72 | 0.52 | 13 |
| ORB RANDOM seed4 1.0x | 659 | 31.4 | 2.44 | -0.99 | 0.086 | 1.13 | 24.59 | 11.93 | 0.52 | 19 |
| ORB RANDOM seed5 1.0x | 646 | 28.2 | 2.54 | -1.01 | -0.008 | 0.95 | -8.73 | 13.93 | 0.52 | 13 |
| RSI2 15m 1.5x | 1399 | 56.5 | 0.68 | -0.96 | -0.030 | 0.94 | -15.56 | 25.77 | 1.64 | 6 |
| RSI2 1H 1.5x | 489 | 47.9 | 0.77 | -0.83 | -0.066 | 0.84 | -13.87 | 18.02 | 1.47 | 8 |
| RSI2 15m slowEMA800 1.5x | 1154 | 55.6 | 0.70 | -0.96 | -0.041 | 0.91 | -18.89 | 24.91 | 1.58 | 6 |
| ORB 5m range-stop 1.5x | 738 | 32.2 | 2.85 | -1.02 | 0.224 | 1.27 | 58.96 | 9.91 | 0.54 | 13 |
| ORB 5m atr-stop 1.5x | 738 | 21.3 | 5.87 | -1.07 | 0.405 | 1.51 | 139.58 | 12.53 | 0.57 | 17 |
| ORB 5m range-stop 2R 1.5x | 738 | 37.0 | 1.80 | -1.03 | 0.019 | 0.99 | -1.61 | 13.96 | 0.54 | 10 |
| ORB RANDOM seed1 1.5x | 645 | 29.8 | 2.54 | -1.02 | 0.039 | 1.04 | 6.77 | 13.53 | 0.53 | 17 |
| ORB RANDOM seed2 1.5x | 654 | 30.6 | 2.60 | -1.01 | 0.089 | 1.09 | 17.69 | 10.19 | 0.53 | 19 |
| ORB RANDOM seed3 1.5x | 651 | 30.0 | 2.57 | -1.01 | 0.064 | 1.07 | 13.36 | 14.21 | 0.53 | 13 |
| ORB RANDOM seed4 1.5x | 659 | 31.4 | 2.43 | -1.01 | 0.073 | 1.11 | 21.02 | 12.24 | 0.53 | 19 |
| ORB RANDOM seed5 1.5x | 646 | 28.0 | 2.54 | -1.02 | -0.021 | 0.94 | -12.15 | 16.36 | 0.53 | 13 |

## Monte Carlo (out-of-sample, 1.5x costs, 10000 runs, Step 1 target 8%)

| Config | Pass % | Firm breach % | Bot -7% stop % | Unfinished % | Median days to pass | Verdict |
|---|---:|---:|---:|---:|---:|---|
| RSI2 15m 1.5x | 1.9 | 0.0 | 95.2 | 2.9 | 230 | NOT READY: PF 0.82 < 1.25; max DD 21.15% > 6.0% |
| RSI2 1H 1.5x | 8.2 | 0.0 | 23.9 | 67.9 | 519 | NOT READY: PF 0.96 < 1.25 |
| RSI2 15m slowEMA800 1.5x | 1.7 | 0.0 | 94.6 | 3.7 | 274 | NOT READY: PF 0.80 < 1.25; max DD 20.23% > 6.0% |
| ORB 5m range-stop 1.5x | 70.5 | 0.0 | 27.7 | 1.7 | 164 | NOT READY: PF 1.14 < 1.25; max DD 8.57% > 6.0% |
| ORB 5m atr-stop 1.5x | 53.2 | 0.0 | 46.8 | 0.0 | 80 | NOT READY: PF 1.07 < 1.25; max DD 18.29% > 6.0% |
| ORB 5m range-stop 2R 1.5x | 79.0 | 0.0 | 15.3 | 5.7 | 234 | NOT READY: PF 1.15 < 1.25; max DD 7.18% > 6.0% |
| ORB RANDOM seed1 1.5x | 71.1 | 0.0 | 26.3 | 2.5 | 178 | NOT READY: PF 1.15 < 1.25; max DD 8.57% > 6.0% |
| ORB RANDOM seed2 1.5x | 68.1 | 0.0 | 30.5 | 1.4 | 156 | NOT READY: PF 1.16 < 1.25; max DD 8.39% > 6.0% |
| ORB RANDOM seed3 1.5x | 51.4 | 0.0 | 46.7 | 1.9 | 154 | NOT READY: PF 1.05 < 1.25; max DD 9.14% > 6.0% |
| ORB RANDOM seed4 1.5x | 23.9 | 0.0 | 74.1 | 1.9 | 170 | NOT READY: PF 0.89 < 1.25; max DD 13.27% > 6.0% |
| ORB RANDOM seed5 1.5x | 52.8 | 0.0 | 45.1 | 2.1 | 167 | NOT READY: PF 1.05 < 1.25; max DD 15.29% > 6.0% |

## ORB vs random direction (out-of-sample, 1x costs)

Real ORB expectancy +0.143 R over 363 trades. Random seeds: +0.125, +0.065, +0.028, -0.098, +0.052 (mean +0.034 R).
Real signal beats 5 of 5 random seeds.

## Robustness: RSI2 15m parameters +-20% (IN-SAMPLE, 1x costs)

| Config | Trades | Win % | Avg win R | Avg loss R | Exp. R | PF | Net % | Max DD % | Worst day % | Lose streak |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BASE (defaults) | 1399 | 56.7 | 0.70 | -0.95 | -0.015 | 0.97 | -6.42 | 19.15 | 1.58 | 6 |
| RSI_LONG_ENTRY 10.0 -> 8.0 (RSI_SHORT_ENTRY 92.0) | 1099 | 56.5 | 0.70 | -0.94 | -0.016 | 0.97 | -6.10 | 13.72 | 1.55 | 6 |
| RSI_LONG_ENTRY 10.0 -> 12.0 (RSI_SHORT_ENTRY 88.0) | 1685 | 57.4 | 0.67 | -0.95 | -0.021 | 0.97 | -10.27 | 26.67 | 1.58 | 8 |
| TREND_EMA 200 -> 160 | 1300 | 57.0 | 0.68 | -0.94 | -0.018 | 0.96 | -8.82 | 24.64 | 1.58 | 6 |
| TREND_EMA 200 -> 240 | 1473 | 56.1 | 0.70 | -0.94 | -0.020 | 0.97 | -8.04 | 20.70 | 1.58 | 8 |
| STOP_ATR_MULT 1.5 -> 1.2 | 1475 | 52.1 | 0.90 | -1.00 | -0.011 | 0.99 | -2.62 | 20.10 | 1.58 | 8 |
| STOP_ATR_MULT 1.5 -> 1.8 | 1343 | 60.2 | 0.57 | -0.88 | -0.009 | 0.98 | -4.02 | 14.36 | 1.52 | 6 |
| TIME_STOP_BARS 12 -> 10 | 1399 | 56.7 | 0.70 | -0.95 | -0.015 | 0.97 | -6.42 | 19.15 | 1.58 | 6 |
| TIME_STOP_BARS 12 -> 14 | 1399 | 56.7 | 0.70 | -0.95 | -0.015 | 0.97 | -6.42 | 19.15 | 1.58 | 6 |
| EXIT_EMA 5 -> 4 | 1402 | 57.6 | 0.66 | -0.92 | -0.011 | 0.98 | -4.80 | 18.62 | 1.58 | 7 |
| EXIT_EMA 5 -> 6 | 1399 | 56.5 | 0.72 | -0.95 | -0.008 | 0.99 | -2.57 | 17.17 | 1.58 | 6 |
| ATR_PERIOD 14 -> 11 | 1378 | 57.8 | 0.65 | -0.93 | -0.018 | 0.96 | -8.67 | 19.67 | 1.56 | 6 |
| ATR_PERIOD 14 -> 17 | 1412 | 55.5 | 0.74 | -0.96 | -0.018 | 0.96 | -9.91 | 22.57 | 1.61 | 6 |

## Robustness: ORB 5m parameters +-20% (IN-SAMPLE, 1x costs)

| Config | Trades | Win % | Avg win R | Avg loss R | Exp. R | PF | Net % | Max DD % | Worst day % | Lose streak |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BASE (defaults) | 738 | 32.4 | 2.85 | -1.01 | 0.238 | 1.30 | 62.94 | 9.68 | 0.52 | 13 |
| ORB_DOJI_BODY_PCT 10.0 -> 8.0 | 751 | 32.2 | 2.84 | -1.01 | 0.231 | 1.28 | 61.39 | 9.68 | 0.52 | 13 |
| ORB_DOJI_BODY_PCT 10.0 -> 12.0 | 724 | 32.9 | 2.82 | -1.01 | 0.249 | 1.32 | 65.53 | 8.50 | 0.52 | 12 |
| ORB_RANGE_MIN_PCTL 20.0 -> 16.0 | 777 | 32.0 | 2.85 | -1.01 | 0.224 | 1.28 | 62.28 | 8.79 | 0.52 | 14 |
| ORB_RANGE_MIN_PCTL 20.0 -> 24.0 | 702 | 32.8 | 2.81 | -1.01 | 0.240 | 1.31 | 62.10 | 9.02 | 0.52 | 13 |
| ORB_RANGE_MAX_PCTL 90.0 -> 72.0 | 526 | 31.6 | 3.02 | -1.01 | 0.261 | 1.37 | 57.47 | 9.73 | 0.52 | 15 |
| ORB_RANGE_MAX_PCTL 90.0 -> 99.0 | 851 | 32.5 | 2.74 | -1.00 | 0.216 | 1.28 | 64.28 | 10.35 | 0.52 | 11 |
| ORB_RANGE_LOOKBACK 20 -> 16 | 722 | 32.0 | 2.86 | -1.01 | 0.229 | 1.29 | 60.39 | 7.64 | 0.52 | 13 |
| ORB_RANGE_LOOKBACK 20 -> 24 | 743 | 32.7 | 2.84 | -1.01 | 0.249 | 1.33 | 69.28 | 8.75 | 0.52 | 13 |

## Exit reasons (full period, 1x costs)

- **RSI2 15m 1.0x**: EMA_EXIT 1159, RSI_EXIT 5, SESSION_END 61, STOP 751, STOP_IN_FILL_BAR 9
- **RSI2 1H 1.0x**: EMA_EXIT 231, SESSION_END 216, STOP 255
- **ORB 5m range-stop 1.0x**: SESSION_END 385, STOP 711, STOP_IN_FILL_BAR 5
- **ORB 5m range-stop 2R 1.0x**: SESSION_END 82, STOP 661, STOP_IN_FILL_BAR 5, TARGET 351, TARGET_PASSED 2

## Execution model

Signals use the strategy's bars (5m/15m/1H); orders, stops and targets are matched on 1-minute bars. If the 1-minute bar in which an entry filled also reached the stop, the trade is counted as stopped at the stop price (STOP_IN_FILL_BAR), even if the bar may have reversed first.

- RSI2 15m 1.0x: 9 of 1985 trades adjusted this way
- RSI2 1H 1.0x: 0 of 702 trades adjusted this way
- ORB 5m range-stop 1.0x: 5 of 1101 trades adjusted this way
- ORB 5m atr-stop 1.0x: 53 of 1101 trades adjusted this way

## Acceptance criteria

Ready only if OUT-OF-SAMPLE at 1.5x costs: >= 100 trades, PF >= 1.25, max DD <= 6%, worst day <= 2.5%, Monte Carlo firm-breach probability < 15%.

- RSI2 15m 1.5x: **NOT READY: PF 0.82 < 1.25; max DD 21.15% > 6.0%**
- RSI2 1H 1.5x: **NOT READY: PF 0.96 < 1.25**
- RSI2 15m slowEMA800 1.5x: **NOT READY: PF 0.80 < 1.25; max DD 20.23% > 6.0%**
- ORB 5m range-stop 1.5x: **NOT READY: PF 1.14 < 1.25; max DD 8.57% > 6.0%**
- ORB 5m atr-stop 1.5x: **NOT READY: PF 1.07 < 1.25; max DD 18.29% > 6.0%**
- ORB 5m range-stop 2R 1.5x: **NOT READY: PF 1.15 < 1.25; max DD 7.18% > 6.0%**
- ORB RANDOM seed1 1.5x: **NOT READY: PF 1.15 < 1.25; max DD 8.57% > 6.0%**
- ORB RANDOM seed2 1.5x: **NOT READY: PF 1.16 < 1.25; max DD 8.39% > 6.0%**
- ORB RANDOM seed3 1.5x: **NOT READY: PF 1.05 < 1.25; max DD 9.14% > 6.0%**
- ORB RANDOM seed4 1.5x: **NOT READY: PF 0.89 < 1.25; max DD 13.27% > 6.0%**
- ORB RANDOM seed5 1.5x: **NOT READY: PF 1.05 < 1.25; max DD 15.29% > 6.0%**
