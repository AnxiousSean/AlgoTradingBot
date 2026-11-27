# Stage 3 research report — 2010-2026, 1-minute execution, with SR (current)

Generated 2026-11-27 09:00 from `data/NAS100_1m_all.csv`, 5094353 1-minute bars, 2010-11-14 23:02:00 to 2026-11-13 21:14:00 UTC.
In-sample: before 2022-01-25 19:10 NY. Out-of-sample: after. OOS trading days in Monte Carlo pool: 1146.
Costs: 1x = 2.5 points round trip at NAS100 30,000 (scaled with price, e.g. about 0.5 points at 6,300 in 2018), 1.5x = 3.75 points. Risk 0.5% ($25) per trade, 1:20 leverage, 30% margin cap. 58 backtests in 4451 s.

Data source: HistData.com NSXUSD 1m bars (same feed as Dukascopy USATECHIDXUSD; not TradeLocker's feed, but matches NAS100.X within a few points, see data_check.md).

## Out-of-sample

| Config | Trades | Win % | Avg win R | Avg loss R | Exp. R | PF | Net % | Max DD % | Worst day % | Lose streak |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| RSI2 15m 1.0x | 986 | 56.8 | 0.63 | -0.94 | -0.046 | 0.90 | -17.04 | 20.79 | 1.47 | 6 |
| RSI2 1H 1.0x | 341 | 49.6 | 0.82 | -0.84 | -0.013 | 0.98 | -0.97 | 5.73 | 1.36 | 8 |
| RSI2 15m slowEMA800 1.0x | 807 | 56.5 | 0.64 | -0.95 | -0.049 | 0.90 | -14.32 | 19.30 | 1.47 | 6 |
| ORB 5m range-stop 1.0x | 583 | 34.8 | 2.43 | -1.02 | 0.184 | 1.23 | 36.00 | 7.75 | 1.36 | 10 |
| ORB 5m atr-stop 1.0x | 583 | 23.2 | 4.41 | -1.05 | 0.214 | 1.28 | 56.86 | 17.65 | 1.15 | 23 |
| ORB 5m range-stop 2R 1.0x | 583 | 39.6 | 1.76 | -1.01 | 0.084 | 1.11 | 15.25 | 14.38 | 1.36 | 10 |
| SR 15m 1.0x | 1354 | 40.0 | 1.42 | -0.99 | -0.028 | 0.93 | -15.83 | 29.83 | 1.15 | 17 |
| SR 1H 1.0x | 390 | 47.7 | 0.91 | -0.81 | 0.014 | 1.09 | 4.80 | 5.55 | 0.71 | 6 |
| SR 15m trend-filter 1.0x | 1038 | 42.2 | 1.39 | -0.98 | 0.021 | 1.01 | 1.98 | 24.75 | 1.61 | 11 |
| ORB RANDOM seed1 1.0x | 508 | 29.9 | 2.40 | -1.00 | 0.018 | 1.02 | 2.09 | 15.17 | 0.52 | 23 |
| ORB RANDOM seed2 1.0x | 494 | 28.1 | 2.33 | -1.00 | -0.065 | 0.89 | -15.19 | 25.32 | 1.36 | 11 |
| ORB RANDOM seed3 1.0x | 511 | 30.5 | 2.25 | -0.99 | -0.004 | 1.01 | 1.31 | 10.13 | 0.57 | 13 |
| RSI2 15m 1.5x | 984 | 56.4 | 0.62 | -0.94 | -0.058 | 0.87 | -21.71 | 24.90 | 1.38 | 6 |
| RSI2 1H 1.5x | 341 | 49.6 | 0.81 | -0.84 | -0.023 | 0.96 | -2.29 | 6.26 | 1.38 | 8 |
| RSI2 15m slowEMA800 1.5x | 805 | 56.1 | 0.63 | -0.95 | -0.061 | 0.87 | -18.28 | 21.29 | 1.38 | 6 |
| ORB 5m range-stop 1.5x | 583 | 34.5 | 2.44 | -1.02 | 0.171 | 1.21 | 32.97 | 8.57 | 1.36 | 10 |
| ORB 5m atr-stop 1.5x | 583 | 23.0 | 4.42 | -1.07 | 0.190 | 1.24 | 50.79 | 18.29 | 1.16 | 23 |
| ORB 5m range-stop 2R 1.5x | 583 | 39.3 | 1.76 | -1.02 | 0.070 | 1.08 | 12.20 | 15.41 | 1.36 | 10 |
| SR 15m 1.5x | 1269 | 40.3 | 1.41 | -1.02 | -0.045 | 0.92 | -10.29 | 17.24 | 0.58 | 11 |
| SR 1H 1.5x | 390 | 47.7 | 0.90 | -0.82 | 0.003 | 1.06 | 3.44 | 5.71 | 0.73 | 6 |
| SR 15m trend-filter 1.5x | 1038 | 42.2 | 1.37 | -1.00 | 0.002 | 0.99 | -2.71 | 27.55 | 1.31 | 11 |
| ORB RANDOM seed1 1.5x | 508 | 29.7 | 2.40 | -1.01 | 0.005 | 1.00 | -0.50 | 15.56 | 0.52 | 23 |
| ORB RANDOM seed2 1.5x | 494 | 27.9 | 2.33 | -1.01 | -0.078 | 0.87 | -17.59 | 27.41 | 1.36 | 11 |
| ORB RANDOM seed3 1.5x | 511 | 30.1 | 2.27 | -1.00 | -0.018 | 0.99 | -1.22 | 10.51 | 0.58 | 13 |
| SR RANDOM seed1 1.0x | 1360 | 38.5 | 1.35 | -0.98 | -0.084 | 0.85 | -42.87 | 48.77 | 1.62 | 12 |
| SR RANDOM seed1 1.5x | 1360 | 38.3 | 1.33 | -1.00 | -0.105 | 0.82 | -50.95 | 56.69 | 1.63 | 12 |
| SR RANDOM seed2 1.0x | 1350 | 40.1 | 1.40 | -0.98 | -0.026 | 0.95 | -9.64 | 19.85 | 0.87 | 14 |
| SR RANDOM seed2 1.5x | 908 | 37.6 | 1.46 | -1.02 | -0.087 | 0.89 | -6.95 | 8.86 | 0.33 | 15 |
| SR RANDOM seed3 1.0x | 1353 | 42.4 | 1.37 | -0.98 | 0.014 | 1.05 | 14.37 | 11.73 | 1.51 | 13 |
| SR RANDOM seed3 1.5x | 1353 | 42.4 | 1.35 | -1.00 | -0.007 | 1.02 | 4.63 | 12.29 | 1.56 | 13 |

## In-sample

| Config | Trades | Win % | Avg win R | Avg loss R | Exp. R | PF | Net % | Max DD % | Worst day % | Lose streak |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| RSI2 15m 1.0x | 2586 | 57.0 | 0.70 | -0.95 | -0.007 | 0.98 | -7.75 | 18.24 | 1.58 | 7 |
| RSI2 1H 1.0x | 960 | 46.4 | 0.84 | -0.85 | -0.068 | 0.84 | -29.90 | 33.24 | 1.49 | 10 |
| RSI2 15m slowEMA800 1.0x | 2162 | 56.6 | 0.71 | -0.95 | -0.015 | 0.96 | -12.96 | 18.08 | 1.55 | 8 |
| ORB 5m range-stop 1.0x | 1452 | 29.2 | 2.92 | -1.02 | 0.134 | 1.16 | 66.41 | 17.16 | 0.53 | 27 |
| ORB 5m atr-stop 1.0x | 1452 | 18.7 | 6.11 | -1.07 | 0.278 | 1.36 | 145.57 | 15.74 | 0.54 | 35 |
| ORB 5m range-stop 2R 1.0x | 1452 | 36.7 | 1.83 | -1.02 | 0.023 | 1.04 | 13.27 | 13.50 | 0.54 | 15 |
| SR 15m 1.0x | 3393 | 38.9 | 1.42 | -1.00 | -0.057 | 0.91 | -62.30 | 74.92 | 1.51 | 15 |
| SR 1H 1.0x | 1095 | 44.5 | 0.91 | -0.78 | -0.028 | 0.91 | -16.55 | 29.46 | 1.00 | 6 |
| SR 15m trend-filter 1.0x | 2458 | 40.0 | 1.42 | -0.98 | -0.022 | 0.94 | -27.26 | 39.85 | 1.45 | 15 |
| ORB RANDOM seed1 1.0x | 1309 | 28.0 | 2.79 | -1.01 | 0.055 | 1.09 | 34.84 | 15.70 | 0.53 | 24 |
| ORB RANDOM seed2 1.0x | 1306 | 28.6 | 2.80 | -1.01 | 0.079 | 1.11 | 41.95 | 14.41 | 0.53 | 24 |
| ORB RANDOM seed3 1.0x | 1303 | 28.9 | 2.94 | -1.01 | 0.132 | 1.17 | 61.43 | 13.78 | 0.53 | 20 |
| RSI2 15m 1.5x | 2586 | 56.7 | 0.69 | -0.96 | -0.026 | 0.94 | -27.27 | 30.73 | 1.60 | 7 |
| RSI2 1H 1.5x | 960 | 46.1 | 0.83 | -0.86 | -0.080 | 0.82 | -34.95 | 38.15 | 1.51 | 10 |
| RSI2 15m slowEMA800 1.5x | 2162 | 56.2 | 0.69 | -0.97 | -0.034 | 0.92 | -29.57 | 31.73 | 1.58 | 8 |
| ORB 5m range-stop 1.5x | 1452 | 29.1 | 2.91 | -1.03 | 0.116 | 1.13 | 56.24 | 18.03 | 0.54 | 27 |
| ORB 5m atr-stop 1.5x | 1452 | 18.7 | 6.08 | -1.10 | 0.243 | 1.32 | 130.91 | 17.03 | 0.57 | 35 |
| ORB 5m range-stop 2R 1.5x | 1452 | 36.6 | 1.81 | -1.04 | 0.005 | 1.01 | 2.77 | 14.74 | 0.55 | 15 |
| SR 15m 1.5x | 3392 | 38.8 | 1.40 | -1.03 | -0.084 | 0.88 | -77.11 | 88.18 | 1.29 | 15 |
| SR 1H 1.5x | 1095 | 44.1 | 0.90 | -0.79 | -0.043 | 0.88 | -22.35 | 34.28 | 1.02 | 6 |
| SR 15m trend-filter 1.5x | 2458 | 39.8 | 1.40 | -1.01 | -0.047 | 0.91 | -43.64 | 54.48 | 1.29 | 15 |
| ORB RANDOM seed1 1.5x | 1309 | 27.9 | 2.78 | -1.02 | 0.037 | 1.07 | 25.71 | 16.88 | 0.54 | 24 |
| ORB RANDOM seed2 1.5x | 1306 | 28.6 | 2.79 | -1.03 | 0.060 | 1.09 | 32.73 | 16.62 | 0.54 | 24 |
| ORB RANDOM seed3 1.5x | 1303 | 28.7 | 2.94 | -1.02 | 0.114 | 1.14 | 52.10 | 15.10 | 0.54 | 20 |
| SR RANDOM seed1 1.0x | 3343 | 41.2 | 1.46 | -1.00 | 0.012 | 1.06 | 41.34 | 16.56 | 1.51 | 12 |
| SR RANDOM seed1 1.5x | 3343 | 41.1 | 1.44 | -1.03 | -0.015 | 1.02 | 15.91 | 21.17 | 1.55 | 12 |
| SR RANDOM seed2 1.0x | 3350 | 38.7 | 1.43 | -1.00 | -0.060 | 0.90 | -61.51 | 67.20 | 1.26 | 14 |
| SR RANDOM seed2 1.5x | 3346 | 38.0 | 1.41 | -1.02 | -0.098 | 0.85 | -84.44 | 86.25 | 1.26 | 14 |
| SR RANDOM seed3 1.0x | 3341 | 40.3 | 1.45 | -1.00 | -0.013 | 1.04 | 28.07 | 24.33 | 1.46 | 16 |
| SR RANDOM seed3 1.5x | 3341 | 40.0 | 1.43 | -1.02 | -0.040 | 1.00 | 2.07 | 37.20 | 1.50 | 16 |

## Monte Carlo (out-of-sample, 1.5x costs, 10000 runs, Step 1 target 8%)

| Config | Pass % | Firm breach % | Bot -7% stop % | Unfinished % | Median days to pass | Verdict |
|---|---:|---:|---:|---:|---:|---|
| RSI2 15m 1.5x | 5.2 | 0.0 | 87.6 | 7.2 | 271 | NOT READY: PF 0.87 < 1.25; max DD 24.90% > 6.0% |
| RSI2 1H 1.5x | 6.4 | 0.0 | 24.0 | 69.6 | 511 | NOT READY: PF 0.96 < 1.25; max DD 6.26% > 6.0% |
| RSI2 15m slowEMA800 1.5x | 5.6 | 0.0 | 83.5 | 11.0 | 299 | NOT READY: PF 0.87 < 1.25; max DD 21.29% > 6.0% |
| ORB 5m range-stop 1.5x | 79.8 | 0.0 | 19.2 | 1.0 | 149 | NOT READY: PF 1.21 < 1.25; max DD 8.57% > 6.0% |
| ORB 5m atr-stop 1.5x | 70.8 | 0.0 | 29.2 | 0.0 | 72 | NOT READY: PF 1.24 < 1.25; max DD 18.29% > 6.0% |
| ORB 5m range-stop 2R 1.5x | 64.3 | 0.0 | 27.1 | 8.7 | 258 | NOT READY: PF 1.08 < 1.25; max DD 15.41% > 6.0% |
| SR 15m 1.5x | 9.4 | 0.0 | 65.6 | 24.9 | 358 | NOT READY: PF 0.92 < 1.25; max DD 17.24% > 6.0% |
| SR 1H 1.5x | 28.3 | 0.0 | 14.2 | 57.5 | 447 | NOT READY: PF 1.06 < 1.25 |
| SR 15m trend-filter 1.5x | 39.5 | 0.0 | 55.0 | 5.6 | 224 | NOT READY: PF 0.99 < 1.25; max DD 27.55% > 6.0% |
| ORB RANDOM seed1 1.5x | 43.5 | 0.0 | 52.8 | 3.7 | 188 | NOT READY: PF 1.00 < 1.25; max DD 15.56% > 6.0% |
| ORB RANDOM seed2 1.5x | 20.2 | 0.0 | 76.4 | 3.4 | 194 | NOT READY: PF 0.87 < 1.25; max DD 27.41% > 6.0% |
| ORB RANDOM seed3 1.5x | 42.4 | 0.0 | 54.4 | 3.2 | 183 | NOT READY: PF 0.99 < 1.25; max DD 10.51% > 6.0% |
| SR RANDOM seed1 1.5x | 5.3 | 0.0 | 94.6 | 0.1 | 131 | NOT READY: PF 0.82 < 1.25; max DD 56.69% > 6.0% |
| SR RANDOM seed2 1.5x | 0.6 | 0.0 | 37.1 | 62.3 | 502 | NOT READY: PF 0.89 < 1.25; max DD 8.86% > 6.0% |
| SR RANDOM seed3 1.5x | 50.8 | 0.0 | 47.6 | 1.5 | 163 | NOT READY: PF 1.02 < 1.25; max DD 12.29% > 6.0% |

## ORB vs random direction (1x costs)

- Out-of-sample: real +0.184 R over 583 trades; random seeds +0.018, -0.065, -0.004 (mean -0.017 R); real beats 3 of 3.
- In-sample: real +0.134 R over 1452 trades; random seeds +0.055, +0.079, +0.132 (mean +0.089 R); real beats 3 of 3.

## SR vs random direction (1x costs)

- Out-of-sample: real -0.028 R over 1354 trades; random seeds -0.084, -0.026, +0.014 (mean -0.032 R); real beats 1 of 3.
- In-sample: real -0.057 R over 3393 trades; random seeds +0.012, -0.060, -0.013 (mean -0.020 R); real beats 1 of 3.

## Robustness: RSI2 15m parameters +-20% (IN-SAMPLE, 1x costs)

| Config | Trades | Win % | Avg win R | Avg loss R | Exp. R | PF | Net % | Max DD % | Worst day % | Lose streak |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BASE (defaults) | 2586 | 57.0 | 0.70 | -0.95 | -0.007 | 0.98 | -7.75 | 18.24 | 1.58 | 7 |
| RSI_LONG_ENTRY 10.0 -> 8.0 (RSI_SHORT_ENTRY 92.0) | 2008 | 56.5 | 0.71 | -0.95 | -0.009 | 0.97 | -9.42 | 18.92 | 1.55 | 6 |
| RSI_LONG_ENTRY 10.0 -> 12.0 (RSI_SHORT_ENTRY 88.0) | 3125 | 57.4 | 0.68 | -0.95 | -0.016 | 0.97 | -18.22 | 21.96 | 1.58 | 8 |
| TREND_EMA 200 -> 160 | 2367 | 56.6 | 0.69 | -0.94 | -0.021 | 0.94 | -23.19 | 27.31 | 1.56 | 9 |
| TREND_EMA 200 -> 240 | 2762 | 56.4 | 0.71 | -0.95 | -0.016 | 0.97 | -16.29 | 22.11 | 1.58 | 7 |
| STOP_ATR_MULT 1.5 -> 1.2 | 2721 | 52.3 | 0.90 | -1.01 | -0.010 | 0.98 | -10.70 | 27.41 | 1.58 | 9 |
| STOP_ATR_MULT 1.5 -> 1.8 | 2464 | 60.1 | 0.57 | -0.88 | -0.006 | 0.98 | -5.60 | 18.70 | 1.53 | 7 |

## Robustness: ORB 5m parameters +-20% (IN-SAMPLE, 1x costs)

| Config | Trades | Win % | Avg win R | Avg loss R | Exp. R | PF | Net % | Max DD % | Worst day % | Lose streak |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BASE (defaults) | 1452 | 29.2 | 2.92 | -1.02 | 0.134 | 1.16 | 66.41 | 17.16 | 0.53 | 27 |
| ORB_DOJI_BODY_PCT 10.0 -> 8.0 | 1479 | 29.1 | 2.94 | -1.02 | 0.137 | 1.17 | 70.28 | 17.16 | 0.53 | 27 |
| ORB_DOJI_BODY_PCT 10.0 -> 12.0 | 1419 | 29.6 | 2.88 | -1.02 | 0.136 | 1.17 | 68.39 | 16.55 | 0.53 | 26 |
| ORB_RANGE_MIN_PCTL 20.0 -> 16.0 | 1505 | 29.4 | 2.91 | -1.02 | 0.138 | 1.16 | 69.21 | 17.86 | 0.53 | 27 |
| ORB_RANGE_MIN_PCTL 20.0 -> 24.0 | 1376 | 29.7 | 2.84 | -1.01 | 0.133 | 1.16 | 64.14 | 16.84 | 0.53 | 26 |
| ORB_RANGE_MAX_PCTL 90.0 -> 72.0 | 1053 | 27.6 | 3.15 | -1.02 | 0.136 | 1.18 | 54.18 | 21.05 | 0.54 | 29 |
| ORB_RANGE_MAX_PCTL 90.0 -> 99.0 | 1673 | 29.8 | 2.81 | -1.01 | 0.130 | 1.16 | 75.22 | 16.94 | 0.53 | 23 |
| ORB_RANGE_LOOKBACK 20 -> 16 | 1440 | 29.2 | 2.86 | -1.02 | 0.115 | 1.15 | 59.90 | 18.24 | 0.53 | 27 |
| ORB_RANGE_LOOKBACK 20 -> 24 | 1464 | 29.7 | 2.89 | -1.01 | 0.146 | 1.18 | 75.45 | 16.35 | 0.53 | 27 |

## Robustness: SR 15m parameters +-20% (IN-SAMPLE, 1x costs)

| Config | Trades | Win % | Avg win R | Avg loss R | Exp. R | PF | Net % | Max DD % | Worst day % | Lose streak |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BASE (defaults) | 3393 | 38.9 | 1.42 | -1.00 | -0.057 | 0.91 | -62.30 | 74.92 | 1.51 | 15 |
| SR_PIVOT_BARS 3 -> 2 | 2998 | 38.9 | 1.38 | -0.99 | -0.070 | 0.90 | -61.29 | 69.70 | 1.40 | 12 |
| SR_PIVOT_BARS 3 -> 4 | 3629 | 39.4 | 1.43 | -1.00 | -0.043 | 0.95 | -37.79 | 51.71 | 1.45 | 14 |
| SR_ZONE_ATR 0.1 -> 0.08 | 3278 | 38.7 | 1.42 | -1.00 | -0.063 | 0.90 | -61.90 | 73.95 | 1.51 | 14 |
| SR_ZONE_ATR 0.1 -> 0.12 | 3514 | 38.6 | 1.43 | -1.00 | -0.063 | 0.90 | -67.27 | 80.76 | 1.51 | 15 |
| SR_STOP_ATR 0.25 -> 0.2 | 3576 | 38.6 | 1.48 | -1.01 | -0.047 | 0.93 | -50.30 | 67.71 | 1.50 | 14 |
| SR_STOP_ATR 0.25 -> 0.3 | 3221 | 39.5 | 1.38 | -0.99 | -0.051 | 0.92 | -51.83 | 63.93 | 1.47 | 14 |
| SR_LOOKBACK_BARS 200 -> 160 | 3626 | 39.2 | 1.43 | -1.00 | -0.047 | 0.92 | -58.64 | 70.90 | 1.51 | 16 |
| SR_LOOKBACK_BARS 200 -> 240 | 3193 | 39.5 | 1.41 | -1.00 | -0.048 | 0.92 | -51.54 | 62.75 | 1.45 | 13 |
| SR_MAX_RR 3.0 -> 2.4 | 3415 | 39.4 | 1.41 | -1.00 | -0.051 | 0.92 | -52.27 | 66.67 | 1.51 | 15 |
| SR_MAX_RR 3.0 -> 3.6 | 3383 | 38.8 | 1.43 | -1.00 | -0.055 | 0.91 | -61.94 | 73.35 | 1.51 | 15 |
| SR_MIN_RR 1.0 -> 0.8 | 4296 | 40.9 | 1.29 | -1.01 | -0.067 | 0.88 | -85.03 | 92.24 | 1.35 | 14 |
| SR_MIN_RR 1.0 -> 1.2 | 2800 | 37.6 | 1.51 | -0.99 | -0.052 | 0.91 | -53.16 | 67.30 | 1.27 | 13 |
| SR_MAX_PIERCE_ATR 0.5 -> 0.4 | 3337 | 38.7 | 1.42 | -1.00 | -0.062 | 0.90 | -65.46 | 78.64 | 1.43 | 15 |
| SR_MAX_PIERCE_ATR 0.5 -> 0.6 | 3416 | 38.9 | 1.42 | -1.00 | -0.056 | 0.91 | -62.37 | 75.12 | 1.51 | 15 |

## Exit reasons (full period, 1x costs)

- **RSI2 15m 1.0x**: EMA_EXIT 2095, RSI_EXIT 7, SESSION_END 110, STOP 1344, STOP_IN_FILL_BAR 16
- **RSI2 1H 1.0x**: EMA_EXIT 432, SESSION_END 368, STOP 501
- **ORB 5m range-stop 1.0x**: SESSION_END 670, STOP 1359, STOP_IN_FILL_BAR 6
- **ORB 5m range-stop 2R 1.0x**: SESSION_END 137, STOP 1238, STOP_IN_FILL_BAR 6, TARGET 647, TARGET_PASSED 7
- **SR 15m 1.0x**: SESSION_END 900, STOP 2621, STOP_IN_FILL_BAR 33, TARGET 1012, TARGET_PASSED 181
- **SR 1H 1.0x**: SESSION_END 797, STOP 528, STOP_IN_FILL_BAR 4, TARGET 126, TARGET_PASSED 30

## Execution model

Signals use the strategy's bars (5m/15m/1H); orders, stops and targets are matched on 1-minute bars. If the 1-minute bar in which an entry filled also reached the stop, the trade is counted as stopped at the stop price (STOP_IN_FILL_BAR), even if the bar may have reversed first.

- RSI2 15m 1.0x: 16 of 3572 trades adjusted this way
- RSI2 1H 1.0x: 0 of 1301 trades adjusted this way
- ORB 5m range-stop 1.0x: 6 of 2035 trades adjusted this way
- ORB 5m atr-stop 1.0x: 117 of 2035 trades adjusted this way
- SR 15m 1.0x: 33 of 4747 trades adjusted this way
- SR 1H 1.0x: 4 of 1485 trades adjusted this way

## Acceptance criteria

Ready only if OUT-OF-SAMPLE at 1.5x costs: >= 100 trades, PF >= 1.25, max DD <= 6%, worst day <= 2.5%, Monte Carlo firm-breach probability < 15%.

- RSI2 15m 1.5x: **NOT READY: PF 0.87 < 1.25; max DD 24.90% > 6.0%**
- RSI2 1H 1.5x: **NOT READY: PF 0.96 < 1.25; max DD 6.26% > 6.0%**
- RSI2 15m slowEMA800 1.5x: **NOT READY: PF 0.87 < 1.25; max DD 21.29% > 6.0%**
- ORB 5m range-stop 1.5x: **NOT READY: PF 1.21 < 1.25; max DD 8.57% > 6.0%**
- ORB 5m atr-stop 1.5x: **NOT READY: PF 1.24 < 1.25; max DD 18.29% > 6.0%**
- ORB 5m range-stop 2R 1.5x: **NOT READY: PF 1.08 < 1.25; max DD 15.41% > 6.0%**
- SR 15m 1.5x: **NOT READY: PF 0.92 < 1.25; max DD 17.24% > 6.0%**
- SR 1H 1.5x: **NOT READY: PF 1.06 < 1.25**
- SR 15m trend-filter 1.5x: **NOT READY: PF 0.99 < 1.25; max DD 27.55% > 6.0%**
- ORB RANDOM seed1 1.5x: **NOT READY: PF 1.00 < 1.25; max DD 15.56% > 6.0%**
- ORB RANDOM seed2 1.5x: **NOT READY: PF 0.87 < 1.25; max DD 27.41% > 6.0%**
- ORB RANDOM seed3 1.5x: **NOT READY: PF 0.99 < 1.25; max DD 10.51% > 6.0%**
- SR RANDOM seed1 1.5x: **NOT READY: PF 0.82 < 1.25; max DD 56.69% > 6.0%**
- SR RANDOM seed2 1.5x: **NOT READY: PF 0.89 < 1.25; max DD 8.86% > 6.0%**
- SR RANDOM seed3 1.5x: **NOT READY: PF 1.02 < 1.25; max DD 12.29% > 6.0%**
