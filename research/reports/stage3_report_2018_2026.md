# Stage 3 research report

Generated 2026-11-27 05:41 from `data/NAS100_1m_2018.csv`, 2814888 1-minute bars, 2018-01-01 21:31:00 to 2026-11-13 21:14:00 UTC.
In-sample: before 2024-03-17 07:43 NY. Out-of-sample: after. OOS trading days in Monte Carlo pool: 684.
Costs: 1x = 2.5 points round trip at NAS100 30,000 (scaled with price, e.g. about 0.5 points at 6,300 in 2018), 1.5x = 3.75 points. Risk 0.5% ($25) per trade, 1:20 leverage, 30% margin cap. 42 backtests in 666 s.

Data source: HistData.com NSXUSD 1m bars (same feed as Dukascopy USATECHIDXUSD; not TradeLocker's feed, but matches NAS100.X within a few points, see data_check.md).

## Out-of-sample

| Config | Trades | Win % | Avg win R | Avg loss R | Exp. R | PF | Net % | Max DD % | Worst day % | Lose streak |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| RSI2 15m 1.0x | 562 | 59.6 | 0.60 | -1.01 | -0.053 | 0.86 | -12.91 | 19.10 | 1.95 | 5 |
| RSI2 1H 1.0x | 194 | 53.6 | 0.82 | -0.93 | 0.007 | 1.05 | 1.36 | 6.59 | 1.15 | 7 |
| RSI2 15m slowEMA800 1.0x | 464 | 59.5 | 0.61 | -1.03 | -0.056 | 0.85 | -12.07 | 20.19 | 1.95 | 5 |
| ORB 5m range-stop 1.0x | 363 | 35.5 | 2.30 | -1.02 | 0.164 | 1.20 | 18.68 | 7.26 | 0.74 | 10 |
| ORB 5m atr-stop 1.0x | 363 | 25.6 | 4.02 | -1.11 | 0.201 | 1.25 | 32.44 | 8.95 | 1.19 | 14 |
| ORB 5m range-stop 2R 1.0x | 363 | 41.6 | 1.74 | -1.01 | 0.132 | 1.20 | 17.14 | 6.50 | 0.74 | 10 |
| ORB RANDOM seed1 1.0x | 318 | 33.0 | 2.48 | -1.00 | 0.150 | 1.22 | 17.80 | 7.69 | 0.59 | 11 |
| ORB RANDOM seed2 1.0x | 323 | 32.2 | 2.41 | -1.00 | 0.099 | 1.19 | 15.37 | 8.53 | 0.68 | 13 |
| ORB RANDOM seed3 1.0x | 313 | 31.0 | 2.51 | -1.00 | 0.087 | 1.12 | 10.09 | 8.76 | 0.57 | 9 |
| ORB RANDOM seed4 1.0x | 318 | 28.6 | 2.27 | -1.00 | -0.064 | 0.91 | -7.80 | 13.00 | 0.59 | 17 |
| ORB RANDOM seed5 1.0x | 314 | 31.2 | 2.47 | -1.00 | 0.079 | 1.12 | 9.83 | 13.82 | 0.68 | 8 |
| RSI2 15m 1.5x | 562 | 58.9 | 0.59 | -1.01 | -0.069 | 0.83 | -16.61 | 21.36 | 1.98 | 5 |
| RSI2 1H 1.5x | 194 | 53.6 | 0.81 | -0.94 | -0.003 | 1.02 | 0.67 | 6.81 | 1.15 | 7 |
| RSI2 15m slowEMA800 1.5x | 464 | 58.6 | 0.60 | -1.02 | -0.072 | 0.81 | -15.49 | 22.03 | 1.98 | 5 |
| ORB 5m range-stop 1.5x | 363 | 35.3 | 2.31 | -1.03 | 0.149 | 1.18 | 16.57 | 7.59 | 0.75 | 10 |
| ORB 5m atr-stop 1.5x | 363 | 25.3 | 4.04 | -1.14 | 0.175 | 1.21 | 28.31 | 10.02 | 1.20 | 14 |
| ORB 5m range-stop 2R 1.5x | 363 | 41.3 | 1.74 | -1.02 | 0.117 | 1.18 | 15.01 | 6.76 | 0.75 | 10 |
| ORB RANDOM seed1 1.5x | 318 | 33.0 | 2.46 | -1.01 | 0.135 | 1.19 | 15.97 | 8.19 | 0.60 | 11 |
| ORB RANDOM seed2 1.5x | 323 | 31.9 | 2.42 | -1.01 | 0.084 | 1.16 | 13.56 | 8.76 | 0.69 | 13 |
| ORB RANDOM seed3 1.5x | 313 | 31.0 | 2.50 | -1.02 | 0.073 | 1.10 | 8.31 | 9.14 | 0.58 | 9 |
| ORB RANDOM seed4 1.5x | 318 | 28.6 | 2.25 | -1.01 | -0.079 | 0.89 | -9.59 | 13.22 | 0.60 | 17 |
| ORB RANDOM seed5 1.5x | 314 | 30.9 | 2.48 | -1.01 | 0.064 | 1.10 | 8.06 | 14.38 | 0.69 | 8 |

## In-sample

| Config | Trades | Win % | Avg win R | Avg loss R | Exp. R | PF | Net % | Max DD % | Worst day % | Lose streak |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| RSI2 15m 1.0x | 1328 | 58.9 | 0.68 | -1.03 | -0.020 | 0.96 | -8.64 | 24.34 | 2.45 | 6 |
| RSI2 1H 1.0x | 447 | 50.1 | 0.78 | -0.95 | -0.083 | 0.81 | -16.14 | 19.83 | 1.87 | 7 |
| RSI2 15m slowEMA800 1.0x | 1096 | 58.0 | 0.69 | -1.04 | -0.034 | 0.93 | -15.21 | 27.34 | 2.45 | 6 |
| ORB 5m range-stop 1.0x | 738 | 32.7 | 2.84 | -1.03 | 0.236 | 1.29 | 62.63 | 9.87 | 1.80 | 13 |
| ORB 5m atr-stop 1.0x | 738 | 22.4 | 5.92 | -1.13 | 0.451 | 1.55 | 154.52 | 14.94 | 4.05 | 17 |
| ORB 5m range-stop 2R 1.0x | 738 | 37.4 | 1.81 | -1.03 | 0.030 | 1.01 | 1.84 | 12.34 | 1.80 | 10 |
| ORB RANDOM seed1 1.0x | 645 | 30.2 | 2.54 | -1.01 | 0.062 | 1.07 | 13.07 | 13.21 | 0.64 | 17 |
| ORB RANDOM seed2 1.0x | 654 | 30.9 | 2.62 | -1.02 | 0.105 | 1.12 | 22.43 | 11.37 | 1.80 | 19 |
| ORB RANDOM seed3 1.0x | 651 | 30.6 | 2.58 | -1.00 | 0.096 | 1.12 | 22.47 | 11.93 | 0.70 | 13 |
| ORB RANDOM seed4 1.0x | 659 | 31.9 | 2.46 | -1.00 | 0.104 | 1.16 | 29.61 | 12.12 | 0.64 | 19 |
| ORB RANDOM seed5 1.0x | 646 | 28.5 | 2.55 | -1.02 | -0.003 | 0.96 | -7.71 | 14.87 | 1.80 | 13 |
| RSI2 15m 1.5x | 1328 | 58.7 | 0.67 | -1.04 | -0.035 | 0.93 | -17.28 | 29.96 | 2.46 | 6 |
| RSI2 1H 1.5x | 447 | 49.9 | 0.77 | -0.95 | -0.092 | 0.80 | -17.82 | 21.40 | 1.87 | 7 |
| RSI2 15m slowEMA800 1.5x | 1096 | 57.9 | 0.68 | -1.05 | -0.048 | 0.89 | -22.53 | 32.06 | 2.46 | 6 |
| ORB 5m range-stop 1.5x | 738 | 32.5 | 2.84 | -1.04 | 0.223 | 1.27 | 58.65 | 10.10 | 1.81 | 13 |
| ORB 5m atr-stop 1.5x | 738 | 22.4 | 5.90 | -1.15 | 0.426 | 1.51 | 146.65 | 15.35 | 4.07 | 17 |
| ORB 5m range-stop 2R 1.5x | 738 | 37.3 | 1.81 | -1.04 | 0.017 | 0.99 | -2.17 | 14.10 | 1.81 | 10 |
| ORB RANDOM seed1 1.5x | 645 | 30.1 | 2.54 | -1.02 | 0.048 | 1.05 | 9.74 | 13.67 | 0.64 | 17 |
| ORB RANDOM seed2 1.5x | 654 | 30.9 | 2.60 | -1.03 | 0.092 | 1.10 | 18.85 | 11.84 | 1.81 | 19 |
| ORB RANDOM seed3 1.5x | 651 | 30.4 | 2.58 | -1.01 | 0.082 | 1.10 | 19.09 | 12.34 | 0.70 | 13 |
| ORB RANDOM seed4 1.5x | 659 | 31.9 | 2.45 | -1.01 | 0.091 | 1.14 | 26.04 | 12.41 | 0.64 | 19 |
| ORB RANDOM seed5 1.5x | 646 | 28.3 | 2.55 | -1.03 | -0.016 | 0.94 | -11.14 | 17.08 | 1.81 | 13 |

## Monte Carlo (out-of-sample, 1.5x costs, 10000 runs, Step 1 target 8%)

| Config | Pass % | Firm breach % | Bot -7% stop % | Unfinished % | Median days to pass | Verdict |
|---|---:|---:|---:|---:|---:|---|
| RSI2 15m 1.5x | 2.9 | 0.0 | 93.2 | 3.9 | 270 | NOT READY: PF 0.83 < 1.25; max DD 21.36% > 6.0% |
| RSI2 1H 1.5x | 14.4 | 0.0 | 13.6 | 72.0 | 528 | NOT READY: PF 1.02 < 1.25; max DD 6.81% > 6.0% |
| RSI2 15m slowEMA800 1.5x | 2.4 | 0.0 | 92.8 | 4.8 | 274 | NOT READY: PF 0.81 < 1.25; max DD 22.03% > 6.0% |
| ORB 5m range-stop 1.5x | 75.1 | 0.0 | 23.6 | 1.3 | 159 | NOT READY: PF 1.18 < 1.25; max DD 7.59% > 6.0% |
| ORB 5m atr-stop 1.5x | 67.4 | 0.0 | 32.6 | 0.0 | 71 | NOT READY: PF 1.21 < 1.25; max DD 10.02% > 6.0% |
| ORB 5m range-stop 2R 1.5x | 83.7 | 0.0 | 12.0 | 4.3 | 224 | NOT READY: PF 1.18 < 1.25; max DD 6.76% > 6.0% |
| ORB RANDOM seed1 1.5x | 76.9 | 0.0 | 21.1 | 2.0 | 170 | NOT READY: PF 1.19 < 1.25; max DD 8.19% > 6.0% |
| ORB RANDOM seed2 1.5x | 68.0 | 0.0 | 30.7 | 1.3 | 151 | NOT READY: PF 1.16 < 1.25; max DD 8.76% > 6.0% |
| ORB RANDOM seed3 1.5x | 58.2 | 0.0 | 40.2 | 1.6 | 148 | NOT READY: PF 1.10 < 1.25; max DD 9.14% > 6.0% |
| ORB RANDOM seed4 1.5x | 25.1 | 0.0 | 73.1 | 1.8 | 160 | NOT READY: PF 0.89 < 1.25; max DD 13.22% > 6.0% |
| ORB RANDOM seed5 1.5x | 60.1 | 0.0 | 37.8 | 2.1 | 164 | NOT READY: PF 1.10 < 1.25; max DD 14.38% > 6.0% |

## ORB vs random direction (out-of-sample, 1x costs)

Real ORB expectancy +0.164 R over 363 trades. Random seeds: +0.150, +0.099, +0.087, -0.064, +0.079 (mean +0.070 R).
Real signal beats 5 of 5 random seeds.

## Robustness: RSI2 15m parameters +-20% (IN-SAMPLE, 1x costs)

| Config | Trades | Win % | Avg win R | Avg loss R | Exp. R | PF | Net % | Max DD % | Worst day % | Lose streak |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BASE (defaults) | 1328 | 58.9 | 0.68 | -1.03 | -0.020 | 0.96 | -8.64 | 24.34 | 2.45 | 6 |
| RSI_LONG_ENTRY 10.0 -> 8.0 (RSI_SHORT_ENTRY 92.0) | 1036 | 58.8 | 0.68 | -1.02 | -0.021 | 0.96 | -7.83 | 19.25 | 2.45 | 6 |
| RSI_LONG_ENTRY 10.0 -> 12.0 (RSI_SHORT_ENTRY 88.0) | 1606 | 59.6 | 0.66 | -1.03 | -0.027 | 0.95 | -13.74 | 31.64 | 2.45 | 8 |
| TREND_EMA 200 -> 160 | 1241 | 59.1 | 0.67 | -1.03 | -0.025 | 0.95 | -12.03 | 27.51 | 2.45 | 6 |
| TREND_EMA 200 -> 240 | 1394 | 58.5 | 0.68 | -1.02 | -0.020 | 0.97 | -8.23 | 24.04 | 2.45 | 6 |
| STOP_ATR_MULT 1.5 -> 1.2 | 1359 | 55.9 | 0.88 | -1.14 | -0.012 | 0.98 | -4.64 | 27.11 | 3.06 | 6 |
| STOP_ATR_MULT 1.5 -> 1.8 | 1297 | 61.7 | 0.56 | -0.92 | -0.009 | 0.99 | -2.48 | 16.23 | 2.14 | 6 |
| TIME_STOP_BARS 12 -> 10 | 1328 | 58.9 | 0.68 | -1.03 | -0.020 | 0.96 | -8.64 | 24.34 | 2.45 | 6 |
| TIME_STOP_BARS 12 -> 14 | 1328 | 58.9 | 0.68 | -1.03 | -0.020 | 0.96 | -8.64 | 24.34 | 2.45 | 6 |
| EXIT_EMA 5 -> 4 | 1331 | 59.7 | 0.65 | -1.00 | -0.018 | 0.96 | -8.64 | 25.10 | 2.45 | 6 |
| EXIT_EMA 5 -> 6 | 1327 | 58.7 | 0.70 | -1.04 | -0.015 | 0.98 | -5.49 | 22.07 | 2.45 | 6 |
| ATR_PERIOD 14 -> 11 | 1313 | 59.9 | 0.64 | -1.00 | -0.020 | 0.96 | -8.51 | 22.85 | 2.45 | 6 |
| ATR_PERIOD 14 -> 17 | 1333 | 58.3 | 0.72 | -1.05 | -0.018 | 0.96 | -9.04 | 25.28 | 2.75 | 6 |

## Robustness: ORB 5m parameters +-20% (IN-SAMPLE, 1x costs)

| Config | Trades | Win % | Avg win R | Avg loss R | Exp. R | PF | Net % | Max DD % | Worst day % | Lose streak |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BASE (defaults) | 738 | 32.7 | 2.84 | -1.03 | 0.236 | 1.29 | 62.63 | 9.87 | 1.80 | 13 |
| ORB_DOJI_BODY_PCT 10.0 -> 8.0 | 751 | 32.5 | 2.84 | -1.03 | 0.230 | 1.28 | 61.08 | 9.87 | 1.80 | 13 |
| ORB_DOJI_BODY_PCT 10.0 -> 12.0 | 724 | 33.1 | 2.82 | -1.03 | 0.248 | 1.31 | 65.22 | 8.69 | 1.80 | 12 |
| ORB_RANGE_MIN_PCTL 20.0 -> 16.0 | 777 | 32.3 | 2.84 | -1.03 | 0.222 | 1.27 | 61.69 | 8.98 | 1.80 | 14 |
| ORB_RANGE_MIN_PCTL 20.0 -> 24.0 | 702 | 33.0 | 2.80 | -1.03 | 0.239 | 1.30 | 61.79 | 9.21 | 1.80 | 13 |
| ORB_RANGE_MAX_PCTL 90.0 -> 72.0 | 526 | 31.7 | 3.01 | -1.02 | 0.261 | 1.37 | 57.61 | 9.91 | 0.70 | 15 |
| ORB_RANGE_MAX_PCTL 90.0 -> 99.0 | 851 | 32.8 | 2.74 | -1.02 | 0.215 | 1.27 | 64.05 | 10.48 | 1.80 | 11 |
| ORB_RANGE_LOOKBACK 20 -> 16 | 722 | 32.3 | 2.85 | -1.02 | 0.228 | 1.29 | 59.93 | 7.83 | 1.80 | 13 |
| ORB_RANGE_LOOKBACK 20 -> 24 | 743 | 33.0 | 2.83 | -1.02 | 0.248 | 1.32 | 69.08 | 8.94 | 1.80 | 13 |

## Exit reasons (full period, 1x costs)

- **RSI2 15m 1.0x**: DAILY_STOP 1, EMA_EXIT 1150, RSI_EXIT 4, SESSION_END 59, STOP 676
- **RSI2 1H 1.0x**: EMA_EXIT 227, SESSION_END 207, STOP 207
- **ORB 5m range-stop 1.0x**: SESSION_END 388, STOP 713
- **ORB 5m range-stop 2R 1.0x**: SESSION_END 82, STOP 662, TARGET 355, TARGET_PASSED 2

## Acceptance criteria

Ready only if OUT-OF-SAMPLE at 1.5x costs: >= 100 trades, PF >= 1.25, max DD <= 6%, worst day <= 2.5%, Monte Carlo firm-breach probability < 15%.

- RSI2 15m 1.5x: **NOT READY: PF 0.83 < 1.25; max DD 21.36% > 6.0%**
- RSI2 1H 1.5x: **NOT READY: PF 1.02 < 1.25; max DD 6.81% > 6.0%**
- RSI2 15m slowEMA800 1.5x: **NOT READY: PF 0.81 < 1.25; max DD 22.03% > 6.0%**
- ORB 5m range-stop 1.5x: **NOT READY: PF 1.18 < 1.25; max DD 7.59% > 6.0%**
- ORB 5m atr-stop 1.5x: **NOT READY: PF 1.21 < 1.25; max DD 10.02% > 6.0%**
- ORB 5m range-stop 2R 1.5x: **NOT READY: PF 1.18 < 1.25; max DD 6.76% > 6.0%**
- ORB RANDOM seed1 1.5x: **NOT READY: PF 1.19 < 1.25; max DD 8.19% > 6.0%**
- ORB RANDOM seed2 1.5x: **NOT READY: PF 1.16 < 1.25; max DD 8.76% > 6.0%**
- ORB RANDOM seed3 1.5x: **NOT READY: PF 1.10 < 1.25; max DD 9.14% > 6.0%**
- ORB RANDOM seed4 1.5x: **NOT READY: PF 0.89 < 1.25; max DD 13.22% > 6.0%**
- ORB RANDOM seed5 1.5x: **NOT READY: PF 1.10 < 1.25; max DD 14.38% > 6.0%**
