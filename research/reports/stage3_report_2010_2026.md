# Stage 3 research report — 2010-2026, 1-minute execution, yearly accounts, with SR (current)

Generated 2026-11-27 20:55 from `data/NAS100_1m_all.csv`, 5094353 1-minute bars, 2010-11-14 23:02:00 to 2026-11-13 21:14:00 UTC.
In-sample: before 2022-01-25 19:10 NY. Out-of-sample: after. OOS trading days in Monte Carlo pool: 1146.
Costs: 1x = 2.5 points round trip at NAS100 30,000 (scaled with price, e.g. about 0.5 points at 6,300 in 2018), 1.5x = 3.75 points. Risk 0.5% ($25) per trade, 1:20 leverage, 30% margin cap. 58 backtests in 4126 s.

Each calendar year is simulated as a fresh $5,000 account (indicators warmed up on the previous 45 days, whose trades are dropped), so a losing year cannot drain the account and stop later years from trading.

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
| SR 15m 1.0x | 1378 | 40.4 | 1.41 | -0.99 | -0.021 | 0.94 | -17.34 | 38.82 | 1.61 | 18 |
| SR 1H 1.0x | 390 | 47.7 | 0.91 | -0.81 | 0.014 | 1.09 | 4.77 | 5.55 | 0.71 | 6 |
| SR 15m trend-filter 1.0x | 1038 | 42.2 | 1.39 | -0.98 | 0.021 | 1.01 | 2.19 | 24.54 | 1.61 | 11 |
| ORB RANDOM seed1 1.0x | 513 | 31.2 | 2.25 | -1.01 | 0.009 | 1.06 | 7.55 | 18.36 | 0.51 | 27 |
| ORB RANDOM seed2 1.0x | 503 | 31.0 | 2.18 | -0.99 | -0.006 | 1.02 | 2.54 | 22.33 | 0.57 | 15 |
| ORB RANDOM seed3 1.0x | 501 | 31.7 | 2.50 | -1.00 | 0.109 | 1.19 | 24.84 | 10.57 | 1.36 | 13 |
| RSI2 15m 1.5x | 986 | 56.3 | 0.62 | -0.94 | -0.060 | 0.86 | -22.84 | 26.12 | 1.50 | 6 |
| RSI2 1H 1.5x | 341 | 49.6 | 0.81 | -0.84 | -0.023 | 0.96 | -2.15 | 6.26 | 1.38 | 8 |
| RSI2 15m slowEMA800 1.5x | 807 | 56.0 | 0.63 | -0.95 | -0.063 | 0.86 | -19.17 | 22.30 | 1.50 | 6 |
| ORB 5m range-stop 1.5x | 583 | 34.5 | 2.44 | -1.02 | 0.171 | 1.21 | 32.97 | 8.57 | 1.36 | 10 |
| ORB 5m atr-stop 1.5x | 583 | 23.0 | 4.42 | -1.07 | 0.190 | 1.24 | 50.79 | 18.29 | 1.16 | 23 |
| ORB 5m range-stop 2R 1.5x | 583 | 39.3 | 1.76 | -1.02 | 0.070 | 1.08 | 12.20 | 15.41 | 1.36 | 10 |
| SR 15m 1.5x | 1378 | 40.4 | 1.38 | -1.01 | -0.042 | 0.91 | -26.84 | 45.31 | 1.63 | 18 |
| SR 1H 1.5x | 390 | 47.7 | 0.90 | -0.82 | 0.003 | 1.06 | 3.36 | 5.71 | 0.73 | 6 |
| SR 15m trend-filter 1.5x | 1038 | 42.2 | 1.37 | -1.00 | 0.002 | 0.98 | -4.39 | 28.94 | 1.63 | 11 |
| ORB RANDOM seed1 1.5x | 513 | 31.0 | 2.25 | -1.02 | -0.005 | 1.04 | 4.93 | 19.30 | 0.52 | 27 |
| ORB RANDOM seed2 1.5x | 503 | 30.8 | 2.18 | -1.00 | -0.019 | 1.00 | -0.08 | 23.49 | 0.58 | 15 |
| ORB RANDOM seed3 1.5x | 501 | 31.5 | 2.50 | -1.01 | 0.095 | 1.17 | 22.24 | 11.63 | 1.36 | 13 |
| SR RANDOM seed1 1.0x | 1356 | 39.6 | 1.42 | -0.98 | -0.030 | 0.92 | -22.64 | 24.62 | 1.55 | 10 |
| SR RANDOM seed1 1.5x | 1356 | 39.3 | 1.41 | -1.00 | -0.051 | 0.89 | -32.51 | 33.51 | 1.61 | 10 |
| SR RANDOM seed2 1.0x | 1366 | 39.2 | 1.38 | -0.98 | -0.057 | 0.90 | -29.51 | 41.29 | 1.62 | 13 |
| SR RANDOM seed2 1.5x | 1366 | 38.9 | 1.37 | -1.00 | -0.078 | 0.86 | -39.48 | 50.65 | 1.63 | 13 |
| SR RANDOM seed3 1.0x | 1347 | 39.9 | 1.42 | -0.98 | -0.025 | 0.97 | -7.99 | 22.61 | 1.44 | 11 |
| SR RANDOM seed3 1.5x | 1347 | 39.8 | 1.40 | -1.00 | -0.046 | 0.94 | -17.39 | 27.13 | 1.46 | 11 |

## In-sample

| Config | Trades | Win % | Avg win R | Avg loss R | Exp. R | PF | Net % | Max DD % | Worst day % | Lose streak |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| RSI2 15m 1.0x | 2586 | 57.0 | 0.70 | -0.95 | -0.007 | 0.98 | -7.75 | 18.24 | 1.58 | 7 |
| RSI2 1H 1.0x | 960 | 46.4 | 0.84 | -0.85 | -0.068 | 0.84 | -29.90 | 33.24 | 1.49 | 10 |
| RSI2 15m slowEMA800 1.0x | 2162 | 56.6 | 0.71 | -0.95 | -0.015 | 0.96 | -12.96 | 18.08 | 1.55 | 8 |
| ORB 5m range-stop 1.0x | 1452 | 29.2 | 2.92 | -1.02 | 0.134 | 1.16 | 66.41 | 17.16 | 0.53 | 27 |
| ORB 5m atr-stop 1.0x | 1452 | 18.7 | 6.11 | -1.07 | 0.278 | 1.36 | 145.57 | 15.74 | 0.54 | 35 |
| ORB 5m range-stop 2R 1.0x | 1452 | 36.7 | 1.83 | -1.02 | 0.023 | 1.04 | 13.27 | 13.50 | 0.54 | 15 |
| SR 15m 1.0x | 3393 | 38.9 | 1.42 | -1.00 | -0.057 | 0.90 | -66.81 | 79.43 | 1.51 | 15 |
| SR 1H 1.0x | 1095 | 44.5 | 0.91 | -0.78 | -0.028 | 0.91 | -16.65 | 29.46 | 1.00 | 6 |
| SR 15m trend-filter 1.0x | 2458 | 40.0 | 1.42 | -0.98 | -0.022 | 0.94 | -27.36 | 39.85 | 1.45 | 15 |
| ORB RANDOM seed1 1.0x | 1293 | 29.9 | 2.73 | -1.01 | 0.105 | 1.14 | 49.17 | 13.99 | 0.53 | 17 |
| ORB RANDOM seed2 1.0x | 1301 | 29.4 | 2.77 | -1.01 | 0.100 | 1.13 | 49.12 | 27.28 | 0.53 | 24 |
| ORB RANDOM seed3 1.0x | 1310 | 28.7 | 2.85 | -1.01 | 0.095 | 1.12 | 45.26 | 23.71 | 0.53 | 20 |
| RSI2 15m 1.5x | 2586 | 56.7 | 0.69 | -0.96 | -0.026 | 0.94 | -27.34 | 30.80 | 1.64 | 7 |
| RSI2 1H 1.5x | 960 | 46.1 | 0.83 | -0.86 | -0.080 | 0.82 | -34.95 | 38.15 | 1.51 | 10 |
| RSI2 15m slowEMA800 1.5x | 2162 | 56.2 | 0.69 | -0.97 | -0.034 | 0.92 | -29.60 | 31.77 | 1.58 | 8 |
| ORB 5m range-stop 1.5x | 1452 | 29.1 | 2.91 | -1.03 | 0.116 | 1.13 | 56.24 | 18.03 | 0.54 | 27 |
| ORB 5m atr-stop 1.5x | 1452 | 18.7 | 6.08 | -1.10 | 0.243 | 1.32 | 130.91 | 17.03 | 0.57 | 35 |
| ORB 5m range-stop 2R 1.5x | 1452 | 36.6 | 1.81 | -1.04 | 0.005 | 1.01 | 2.77 | 14.74 | 0.55 | 15 |
| SR 15m 1.5x | 3393 | 38.8 | 1.40 | -1.03 | -0.085 | 0.87 | -92.13 | 103.20 | 1.53 | 15 |
| SR 1H 1.5x | 1095 | 44.1 | 0.90 | -0.79 | -0.043 | 0.88 | -22.48 | 34.29 | 1.02 | 6 |
| SR 15m trend-filter 1.5x | 2458 | 39.8 | 1.40 | -1.01 | -0.047 | 0.91 | -44.93 | 55.77 | 1.50 | 15 |
| ORB RANDOM seed1 1.5x | 1293 | 29.6 | 2.73 | -1.03 | 0.086 | 1.11 | 40.38 | 15.12 | 0.54 | 17 |
| ORB RANDOM seed2 1.5x | 1301 | 29.3 | 2.76 | -1.03 | 0.081 | 1.11 | 40.06 | 28.96 | 0.54 | 24 |
| ORB RANDOM seed3 1.5x | 1310 | 28.5 | 2.85 | -1.03 | 0.077 | 1.10 | 36.17 | 25.14 | 0.54 | 20 |
| SR RANDOM seed1 1.0x | 3376 | 40.9 | 1.44 | -1.00 | -0.002 | 1.02 | 15.06 | 30.76 | 1.39 | 13 |
| SR RANDOM seed1 1.5x | 3376 | 40.7 | 1.43 | -1.03 | -0.029 | 0.98 | -10.80 | 42.95 | 1.42 | 13 |
| SR RANDOM seed2 1.0x | 3346 | 40.6 | 1.43 | -1.00 | -0.011 | 1.01 | 6.25 | 35.37 | 1.46 | 13 |
| SR RANDOM seed2 1.5x | 3346 | 40.4 | 1.41 | -1.03 | -0.039 | 0.97 | -19.83 | 50.47 | 1.50 | 13 |
| SR RANDOM seed3 1.0x | 3353 | 39.1 | 1.43 | -0.99 | -0.043 | 0.94 | -40.53 | 68.78 | 1.51 | 15 |
| SR RANDOM seed3 1.5x | 3353 | 39.1 | 1.41 | -1.02 | -0.070 | 0.90 | -65.61 | 90.23 | 1.53 | 15 |

## Monte Carlo (out-of-sample, 1.5x costs, 10000 runs, Step 1 target 8%)

| Config | Pass % | Firm breach % | Bot -7% stop % | Unfinished % | Median days to pass | Verdict |
|---|---:|---:|---:|---:|---:|---|
| RSI2 15m 1.5x | 5.0 | 0.0 | 88.8 | 6.2 | 279 | NOT READY: PF 0.86 < 1.25; max DD 26.12% > 6.0% |
| RSI2 1H 1.5x | 6.3 | 0.0 | 23.3 | 70.4 | 511 | NOT READY: PF 0.96 < 1.25; max DD 6.26% > 6.0% |
| RSI2 15m slowEMA800 1.5x | 5.1 | 0.0 | 84.7 | 10.3 | 298 | NOT READY: PF 0.86 < 1.25; max DD 22.30% > 6.0% |
| ORB 5m range-stop 1.5x | 79.8 | 0.0 | 19.2 | 1.0 | 149 | NOT READY: PF 1.21 < 1.25; max DD 8.57% > 6.0% |
| ORB 5m atr-stop 1.5x | 70.8 | 0.0 | 29.2 | 0.0 | 72 | NOT READY: PF 1.24 < 1.25; max DD 18.29% > 6.0% |
| ORB 5m range-stop 2R 1.5x | 64.3 | 0.0 | 27.1 | 8.7 | 258 | NOT READY: PF 1.08 < 1.25; max DD 15.41% > 6.0% |
| SR 15m 1.5x | 18.9 | 0.0 | 80.3 | 0.8 | 147 | NOT READY: PF 0.91 < 1.25; max DD 45.31% > 6.0% |
| SR 1H 1.5x | 28.3 | 0.0 | 14.4 | 57.3 | 450 | NOT READY: PF 1.06 < 1.25 |
| SR 15m trend-filter 1.5x | 37.6 | 0.0 | 57.6 | 4.8 | 210 | NOT READY: PF 0.98 < 1.25; max DD 28.94% > 6.0% |
| ORB RANDOM seed1 1.5x | 51.0 | 0.0 | 45.3 | 3.7 | 187 | NOT READY: PF 1.04 < 1.25; max DD 19.30% > 6.0% |
| ORB RANDOM seed2 1.5x | 42.6 | 0.0 | 53.8 | 3.6 | 188 | NOT READY: PF 1.00 < 1.25; max DD 23.49% > 6.0% |
| ORB RANDOM seed3 1.5x | 70.8 | 0.0 | 27.0 | 2.2 | 168 | NOT READY: PF 1.17 < 1.25; max DD 11.63% > 6.0% |
| SR RANDOM seed1 1.5x | 14.2 | 0.0 | 85.2 | 0.6 | 154 | NOT READY: PF 0.89 < 1.25; max DD 33.51% > 6.0% |
| SR RANDOM seed2 1.5x | 10.0 | 0.0 | 89.7 | 0.3 | 130 | NOT READY: PF 0.86 < 1.25; max DD 50.65% > 6.0% |
| SR RANDOM seed3 1.5x | 25.9 | 0.0 | 72.6 | 1.5 | 165 | NOT READY: PF 0.94 < 1.25; max DD 27.13% > 6.0% |

## ORB vs random direction (1x costs)

- Out-of-sample: real +0.184 R over 583 trades; random seeds +0.009, -0.006, +0.109 (mean +0.037 R); real beats 3 of 3.
- In-sample: real +0.134 R over 1452 trades; random seeds +0.105, +0.100, +0.095 (mean +0.100 R); real beats 3 of 3.

## SR vs random direction (1x costs)

- Out-of-sample: real -0.021 R over 1378 trades; random seeds -0.030, -0.057, -0.025 (mean -0.037 R); real beats 3 of 3.
- In-sample: real -0.057 R over 3393 trades; random seeds -0.002, -0.011, -0.043 (mean -0.019 R); real beats 0 of 3.

## Robustness: RSI2 15m parameters +-20% (IN-SAMPLE, 1x costs)

| Config | Trades | Win % | Avg win R | Avg loss R | Exp. R | PF | Net % | Max DD % | Worst day % | Lose streak |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BASE (defaults) | 2586 | 57.0 | 0.70 | -0.95 | -0.007 | 0.98 | -7.75 | 18.24 | 1.58 | 7 |
| RSI_LONG_ENTRY 10.0 -> 8.0 (RSI_SHORT_ENTRY 92.0) | 2008 | 56.5 | 0.71 | -0.95 | -0.009 | 0.97 | -9.42 | 18.92 | 1.55 | 6 |
| RSI_LONG_ENTRY 10.0 -> 12.0 (RSI_SHORT_ENTRY 88.0) | 3125 | 57.4 | 0.68 | -0.95 | -0.016 | 0.97 | -18.22 | 21.96 | 1.58 | 8 |
| TREND_EMA 200 -> 160 | 2367 | 56.6 | 0.69 | -0.94 | -0.021 | 0.94 | -23.22 | 27.34 | 1.58 | 9 |
| TREND_EMA 200 -> 240 | 2762 | 56.4 | 0.71 | -0.95 | -0.016 | 0.97 | -16.29 | 22.11 | 1.58 | 7 |
| STOP_ATR_MULT 1.5 -> 1.2 | 2721 | 52.3 | 0.90 | -1.01 | -0.010 | 0.98 | -10.71 | 27.41 | 1.58 | 9 |
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
| BASE (defaults) | 3393 | 38.9 | 1.42 | -1.00 | -0.057 | 0.90 | -66.81 | 79.43 | 1.51 | 15 |
| SR_PIVOT_BARS 3 -> 2 | 2998 | 38.9 | 1.38 | -0.99 | -0.070 | 0.89 | -64.14 | 72.55 | 1.46 | 12 |
| SR_PIVOT_BARS 3 -> 4 | 3629 | 39.4 | 1.43 | -1.00 | -0.043 | 0.95 | -38.40 | 52.31 | 1.51 | 14 |
| SR_ZONE_ATR 0.1 -> 0.08 | 3278 | 38.7 | 1.42 | -1.00 | -0.063 | 0.90 | -65.36 | 77.41 | 1.51 | 14 |
| SR_ZONE_ATR 0.1 -> 0.12 | 3515 | 38.6 | 1.43 | -1.00 | -0.063 | 0.89 | -74.62 | 88.11 | 1.51 | 15 |
| SR_STOP_ATR 0.25 -> 0.2 | 3576 | 38.6 | 1.48 | -1.01 | -0.047 | 0.93 | -49.33 | 67.34 | 1.50 | 14 |
| SR_STOP_ATR 0.25 -> 0.3 | 3221 | 39.5 | 1.38 | -0.99 | -0.051 | 0.92 | -54.31 | 66.41 | 1.47 | 14 |
| SR_LOOKBACK_BARS 200 -> 160 | 3626 | 39.2 | 1.43 | -1.00 | -0.047 | 0.92 | -59.89 | 72.16 | 1.51 | 16 |
| SR_LOOKBACK_BARS 200 -> 240 | 3193 | 39.5 | 1.41 | -1.00 | -0.048 | 0.92 | -52.26 | 63.47 | 1.45 | 13 |
| SR_MAX_RR 3.0 -> 2.4 | 3415 | 39.4 | 1.41 | -1.00 | -0.051 | 0.92 | -54.27 | 68.67 | 1.51 | 15 |
| SR_MAX_RR 3.0 -> 3.6 | 3383 | 38.8 | 1.43 | -1.00 | -0.055 | 0.90 | -65.87 | 77.28 | 1.51 | 15 |
| SR_MIN_RR 1.0 -> 0.8 | 4312 | 40.9 | 1.29 | -1.01 | -0.069 | 0.88 | -106.15 | 113.51 | 1.47 | 14 |
| SR_MIN_RR 1.0 -> 1.2 | 2800 | 37.6 | 1.51 | -0.99 | -0.052 | 0.90 | -54.82 | 69.04 | 1.38 | 13 |
| SR_MAX_PIERCE_ATR 0.5 -> 0.4 | 3337 | 38.7 | 1.42 | -1.00 | -0.062 | 0.89 | -71.24 | 84.41 | 1.51 | 15 |
| SR_MAX_PIERCE_ATR 0.5 -> 0.6 | 3416 | 38.9 | 1.42 | -1.00 | -0.056 | 0.90 | -66.74 | 79.50 | 1.51 | 15 |

## Exit reasons (full period, 1x costs)

- **RSI2 15m 1.0x**: EMA_EXIT 2095, RSI_EXIT 7, SESSION_END 110, STOP 1344, STOP_IN_FILL_BAR 16
- **RSI2 1H 1.0x**: EMA_EXIT 432, SESSION_END 368, STOP 501
- **ORB 5m range-stop 1.0x**: SESSION_END 670, STOP 1359, STOP_IN_FILL_BAR 6
- **ORB 5m range-stop 2R 1.0x**: SESSION_END 137, STOP 1238, STOP_IN_FILL_BAR 6, TARGET 647, TARGET_PASSED 7
- **SR 15m 1.0x**: SESSION_END 920, STOP 2624, STOP_IN_FILL_BAR 33, TARGET 1013, TARGET_PASSED 181
- **SR 1H 1.0x**: SESSION_END 797, STOP 528, STOP_IN_FILL_BAR 4, TARGET 126, TARGET_PASSED 30

## Execution model

Signals use the strategy's bars (5m/15m/1H); orders, stops and targets are matched on 1-minute bars. If the 1-minute bar in which an entry filled also reached the stop, the trade is counted as stopped at the stop price (STOP_IN_FILL_BAR), even if the bar may have reversed first.

- RSI2 15m 1.0x: 16 of 3572 trades adjusted this way
- RSI2 1H 1.0x: 0 of 1301 trades adjusted this way
- ORB 5m range-stop 1.0x: 6 of 2035 trades adjusted this way
- ORB 5m atr-stop 1.0x: 117 of 2035 trades adjusted this way
- SR 15m 1.0x: 33 of 4771 trades adjusted this way
- SR 1H 1.0x: 4 of 1485 trades adjusted this way

## Acceptance criteria

Ready only if OUT-OF-SAMPLE at 1.5x costs: >= 100 trades, PF >= 1.25, max DD <= 6%, worst day <= 2.5%, Monte Carlo firm-breach probability < 15%.

- RSI2 15m 1.5x: **NOT READY: PF 0.86 < 1.25; max DD 26.12% > 6.0%**
- RSI2 1H 1.5x: **NOT READY: PF 0.96 < 1.25; max DD 6.26% > 6.0%**
- RSI2 15m slowEMA800 1.5x: **NOT READY: PF 0.86 < 1.25; max DD 22.30% > 6.0%**
- ORB 5m range-stop 1.5x: **NOT READY: PF 1.21 < 1.25; max DD 8.57% > 6.0%**
- ORB 5m atr-stop 1.5x: **NOT READY: PF 1.24 < 1.25; max DD 18.29% > 6.0%**
- ORB 5m range-stop 2R 1.5x: **NOT READY: PF 1.08 < 1.25; max DD 15.41% > 6.0%**
- SR 15m 1.5x: **NOT READY: PF 0.91 < 1.25; max DD 45.31% > 6.0%**
- SR 1H 1.5x: **NOT READY: PF 1.06 < 1.25**
- SR 15m trend-filter 1.5x: **NOT READY: PF 0.98 < 1.25; max DD 28.94% > 6.0%**
- ORB RANDOM seed1 1.5x: **NOT READY: PF 1.04 < 1.25; max DD 19.30% > 6.0%**
- ORB RANDOM seed2 1.5x: **NOT READY: PF 1.00 < 1.25; max DD 23.49% > 6.0%**
- ORB RANDOM seed3 1.5x: **NOT READY: PF 1.17 < 1.25; max DD 11.63% > 6.0%**
- SR RANDOM seed1 1.5x: **NOT READY: PF 0.89 < 1.25; max DD 33.51% > 6.0%**
- SR RANDOM seed2 1.5x: **NOT READY: PF 0.86 < 1.25; max DD 50.65% > 6.0%**
- SR RANDOM seed3 1.5x: **NOT READY: PF 0.94 < 1.25; max DD 27.13% > 6.0%**
