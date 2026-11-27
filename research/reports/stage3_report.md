# Stage 3 research report (2024-2026, SUPERSEDED)

> Superseded by `stage3_report_2018_2026.md`. This run used a HistData clock conversion that put
> about 4 weeks a year (when US and European daylight-saving dates differ) one hour off, and fixed-point costs.

Generated 2026-11-27 04:54 from `data/NAS100_1m.csv`, 980184 1-minute bars, 2024-01-01 23:01:00 to 2026-11-13 21:14:00 UTC.
In-sample: before 2026-01-03 14:22 NY. Out-of-sample: after. OOS trading days in Monte Carlo pool: 224.
Costs: 1x = 2.5 points round trip, 1.5x = 3.75 points. Risk 0.5% ($25) per trade, 1:20 leverage, 30% margin cap. 42 backtests in 267 s.

Data source: HistData.com NSXUSD 1m bars (same feed as Dukascopy USATECHIDXUSD; not TradeLocker's feed, but matches NAS100.X within a few points, see data_check.md).

## Out-of-sample

| Config | Trades | Win % | Avg win R | Avg loss R | Exp. R | PF | Net % | Max DD % | Worst day % | Lose streak |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| RSI2 15m 1.0x | 198 | 62.1 | 0.58 | -0.87 | 0.028 | 1.06 | 1.65 | 5.26 | 1.15 | 4 |
| RSI2 1H 1.0x | 54 | 53.7 | 0.77 | -0.95 | -0.026 | 0.93 | -0.54 | 4.52 | 1.15 | 4 |
| RSI2 15m slowEMA800 1.0x | 164 | 64.0 | 0.60 | -0.87 | 0.070 | 1.22 | 4.44 | 3.18 | 0.87 | 4 |
| ORB 5m range-stop 1.0x | 112 | 36.6 | 1.90 | -1.02 | 0.047 | 1.07 | 1.66 | 4.60 | 0.57 | 8 |
| ORB 5m atr-stop 1.0x | 112 | 27.7 | 3.63 | -1.12 | 0.194 | 1.27 | 10.62 | 8.11 | 1.15 | 9 |
| ORB 5m range-stop 2R 1.0x | 112 | 38.4 | 1.58 | -1.02 | -0.020 | 0.96 | -0.91 | 4.45 | 0.57 | 8 |
| ORB RANDOM seed1 1.0x | 98 | 32.7 | 1.88 | -1.00 | -0.060 | 0.97 | -0.63 | 5.00 | 0.57 | 10 |
| ORB RANDOM seed2 1.0x | 97 | 27.8 | 1.76 | -0.99 | -0.223 | 0.76 | -5.00 | 5.35 | 0.51 | 11 |
| ORB RANDOM seed3 1.0x | 95 | 27.4 | 1.74 | -0.97 | -0.232 | 0.67 | -7.20 | 9.22 | 0.52 | 10 |
| ORB RANDOM seed4 1.0x | 98 | 31.6 | 1.84 | -0.98 | -0.092 | 0.92 | -1.69 | 8.47 | 0.52 | 13 |
| ORB RANDOM seed5 1.0x | 97 | 29.9 | 1.58 | -0.99 | -0.221 | 0.66 | -7.69 | 8.93 | 0.57 | 11 |
| RSI2 15m 1.5x | 198 | 60.6 | 0.58 | -0.86 | 0.012 | 1.01 | 0.33 | 5.85 | 1.17 | 4 |
| RSI2 1H 1.5x | 54 | 53.7 | 0.76 | -0.96 | -0.035 | 0.91 | -0.71 | 4.59 | 1.15 | 4 |
| RSI2 15m slowEMA800 1.5x | 164 | 62.2 | 0.60 | -0.84 | 0.054 | 1.16 | 3.24 | 3.56 | 0.89 | 4 |
| ORB 5m range-stop 1.5x | 112 | 36.6 | 1.88 | -1.03 | 0.033 | 1.04 | 1.11 | 4.70 | 0.58 | 8 |
| ORB 5m atr-stop 1.5x | 112 | 27.7 | 3.60 | -1.15 | 0.168 | 1.24 | 9.38 | 8.36 | 1.16 | 9 |
| ORB 5m range-stop 2R 1.5x | 112 | 38.4 | 1.57 | -1.03 | -0.034 | 0.94 | -1.46 | 4.73 | 0.58 | 8 |
| ORB RANDOM seed1 1.5x | 98 | 32.7 | 1.87 | -1.02 | -0.074 | 0.95 | -1.07 | 5.10 | 0.58 | 10 |
| ORB RANDOM seed2 1.5x | 97 | 27.8 | 1.74 | -1.00 | -0.237 | 0.74 | -5.42 | 5.58 | 0.52 | 11 |
| ORB RANDOM seed3 1.5x | 95 | 27.4 | 1.72 | -0.99 | -0.246 | 0.66 | -7.64 | 9.62 | 0.53 | 10 |
| ORB RANDOM seed4 1.5x | 98 | 31.6 | 1.82 | -1.00 | -0.106 | 0.90 | -2.15 | 8.65 | 0.53 | 13 |
| ORB RANDOM seed5 1.5x | 97 | 29.9 | 1.57 | -1.00 | -0.235 | 0.64 | -8.15 | 9.26 | 0.58 | 11 |

## In-sample

| Config | Trades | Win % | Avg win R | Avg loss R | Exp. R | PF | Net % | Max DD % | Worst day % | Lose streak |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| RSI2 15m 1.0x | 424 | 59.7 | 0.62 | -1.06 | -0.057 | 0.88 | -9.01 | 15.60 | 1.98 | 5 |
| RSI2 1H 1.0x | 155 | 54.8 | 0.81 | -0.90 | 0.038 | 1.11 | 2.51 | 4.22 | 1.24 | 7 |
| RSI2 15m slowEMA800 1.0x | 341 | 58.1 | 0.63 | -1.10 | -0.098 | 0.79 | -13.85 | 17.43 | 1.98 | 5 |
| ORB 5m range-stop 1.0x | 260 | 32.7 | 2.69 | -1.03 | 0.186 | 1.21 | 15.71 | 9.04 | 0.75 | 10 |
| ORB 5m atr-stop 1.0x | 260 | 23.8 | 4.55 | -1.13 | 0.227 | 1.22 | 22.02 | 14.71 | 1.20 | 12 |
| ORB 5m range-stop 2R 1.0x | 260 | 40.8 | 1.78 | -1.03 | 0.115 | 1.14 | 9.33 | 7.47 | 0.75 | 9 |
| ORB RANDOM seed1 1.0x | 226 | 28.8 | 2.50 | -1.03 | -0.017 | 0.95 | -3.38 | 11.64 | 0.52 | 11 |
| ORB RANDOM seed2 1.0x | 238 | 33.6 | 2.31 | -1.02 | 0.095 | 1.11 | 7.16 | 7.47 | 0.60 | 9 |
| ORB RANDOM seed3 1.0x | 230 | 29.6 | 2.97 | -1.04 | 0.149 | 1.19 | 12.42 | 6.14 | 0.75 | 12 |
| ORB RANDOM seed4 1.0x | 232 | 31.0 | 2.82 | -1.03 | 0.168 | 1.22 | 14.24 | 7.30 | 0.75 | 11 |
| ORB RANDOM seed5 1.0x | 236 | 30.1 | 2.97 | -1.00 | 0.195 | 1.30 | 19.44 | 8.94 | 0.52 | 15 |
| RSI2 15m 1.5x | 424 | 58.7 | 0.61 | -1.06 | -0.082 | 0.82 | -13.50 | 18.34 | 2.02 | 5 |
| RSI2 1H 1.5x | 155 | 54.8 | 0.80 | -0.92 | 0.023 | 1.07 | 1.60 | 4.55 | 1.27 | 7 |
| RSI2 15m slowEMA800 1.5x | 341 | 57.8 | 0.60 | -1.12 | -0.123 | 0.74 | -17.56 | 20.46 | 2.02 | 5 |
| ORB 5m range-stop 1.5x | 260 | 32.3 | 2.70 | -1.05 | 0.162 | 1.18 | 13.28 | 9.70 | 0.76 | 10 |
| ORB 5m atr-stop 1.5x | 260 | 23.8 | 4.51 | -1.17 | 0.188 | 1.17 | 17.44 | 16.37 | 1.22 | 12 |
| ORB 5m range-stop 2R 1.5x | 260 | 40.8 | 1.75 | -1.05 | 0.091 | 1.10 | 6.76 | 7.85 | 0.76 | 9 |
| ORB RANDOM seed1 1.5x | 226 | 28.8 | 2.48 | -1.06 | -0.042 | 0.92 | -5.51 | 13.25 | 0.54 | 11 |
| ORB RANDOM seed2 1.5x | 238 | 33.2 | 2.31 | -1.04 | 0.071 | 1.08 | 5.01 | 7.76 | 0.61 | 9 |
| ORB RANDOM seed3 1.5x | 230 | 28.7 | 3.04 | -1.05 | 0.125 | 1.14 | 9.84 | 6.90 | 0.76 | 12 |
| ORB RANDOM seed4 1.5x | 232 | 30.6 | 2.84 | -1.04 | 0.143 | 1.17 | 11.55 | 8.04 | 0.76 | 11 |
| ORB RANDOM seed5 1.5x | 236 | 29.7 | 2.99 | -1.02 | 0.171 | 1.26 | 17.30 | 9.14 | 0.54 | 15 |

## Monte Carlo (out-of-sample, 1.5x costs, 10000 runs, Step 1 target 8%)

| Config | Pass % | Firm breach % | Bot -7% stop % | Unfinished % | Median days to pass | Verdict |
|---|---:|---:|---:|---:|---:|---|
| RSI2 15m 1.5x | 36.8 | 0.0 | 34.0 | 29.2 | 370 | NOT READY: PF 1.01 < 1.25 |
| RSI2 1H 1.5x | 2.0 | 0.0 | 22.7 | 75.4 | 546 | NOT READY: trades 54 < 100; PF 0.91 < 1.25 |
| RSI2 15m slowEMA800 1.5x | 76.4 | 0.0 | 5.4 | 18.3 | 345 | NOT READY: PF 1.16 < 1.25 |
| ORB 5m range-stop 1.5x | 51.1 | 0.0 | 42.0 | 7.0 | 230 | NOT READY: PF 1.04 < 1.25 |
| ORB 5m atr-stop 1.5x | 71.2 | 0.0 | 28.7 | 0.0 | 81 | NOT READY: PF 1.24 < 1.25; max DD 8.36% > 6.0% |
| ORB 5m range-stop 2R 1.5x | 21.8 | 0.0 | 61.3 | 16.9 | 309 | NOT READY: PF 0.94 < 1.25 |
| ORB RANDOM seed1 1.5x | 28.5 | 0.0 | 57.1 | 14.4 | 272 | NOT READY: trades 98 < 100; PF 0.95 < 1.25 |
| ORB RANDOM seed2 1.5x | 2.9 | 0.0 | 94.0 | 3.1 | 207 | NOT READY: trades 97 < 100; PF 0.74 < 1.25 |
| ORB RANDOM seed3 1.5x | 1.4 | 0.0 | 98.1 | 0.5 | 164 | NOT READY: trades 95 < 100; PF 0.66 < 1.25; max DD 9.62% > 6.0% |
| ORB RANDOM seed4 1.5x | 20.0 | 0.0 | 70.3 | 9.6 | 255 | NOT READY: trades 98 < 100; PF 0.90 < 1.25; max DD 8.65% > 6.0% |
| ORB RANDOM seed5 1.5x | 0.4 | 0.0 | 99.4 | 0.2 | 171 | NOT READY: trades 97 < 100; PF 0.64 < 1.25; max DD 9.26% > 6.0% |

## ORB vs random direction (out-of-sample, 1x costs)

Real ORB expectancy +0.047 R over 112 trades. Random seeds: -0.060, -0.223, -0.232, -0.092, -0.221 (mean -0.165 R).
Real signal beats 5 of 5 random seeds.

## Robustness: RSI2 15m parameters +-20% (IN-SAMPLE, 1x costs)

| Config | Trades | Win % | Avg win R | Avg loss R | Exp. R | PF | Net % | Max DD % | Worst day % | Lose streak |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BASE (defaults) | 424 | 59.7 | 0.62 | -1.06 | -0.057 | 0.88 | -9.01 | 15.60 | 1.98 | 5 |
| RSI_LONG_ENTRY 10.0 -> 8.0 (RSI_SHORT_ENTRY 92.0) | 345 | 58.8 | 0.62 | -1.07 | -0.072 | 0.82 | -11.49 | 16.22 | 1.98 | 5 |
| RSI_LONG_ENTRY 10.0 -> 12.0 (RSI_SHORT_ENTRY 88.0) | 524 | 59.9 | 0.59 | -1.04 | -0.060 | 0.86 | -13.08 | 18.82 | 1.98 | 5 |
| TREND_EMA 200 -> 160 | 387 | 59.7 | 0.59 | -1.05 | -0.073 | 0.83 | -11.74 | 16.36 | 1.98 | 5 |
| TREND_EMA 200 -> 240 | 452 | 58.2 | 0.63 | -1.08 | -0.087 | 0.81 | -16.12 | 21.67 | 1.98 | 5 |
| STOP_ATR_MULT 1.5 -> 1.2 | 437 | 55.4 | 0.78 | -1.17 | -0.091 | 0.83 | -16.83 | 22.92 | 2.63 | 7 |
| STOP_ATR_MULT 1.5 -> 1.8 | 410 | 60.7 | 0.52 | -0.93 | -0.051 | 0.88 | -7.11 | 12.97 | 1.86 | 5 |
| TIME_STOP_BARS 12 -> 10 | 424 | 59.7 | 0.62 | -1.06 | -0.057 | 0.88 | -9.00 | 15.59 | 1.98 | 5 |
| TIME_STOP_BARS 12 -> 14 | 424 | 59.7 | 0.62 | -1.06 | -0.057 | 0.88 | -9.01 | 15.60 | 1.98 | 5 |
| EXIT_EMA 5 -> 4 | 426 | 61.0 | 0.57 | -1.05 | -0.059 | 0.86 | -10.21 | 16.33 | 1.98 | 5 |
| EXIT_EMA 5 -> 6 | 422 | 59.7 | 0.63 | -1.08 | -0.058 | 0.88 | -9.02 | 16.31 | 1.98 | 5 |
| ATR_PERIOD 14 -> 11 | 422 | 59.7 | 0.59 | -1.02 | -0.059 | 0.88 | -8.60 | 14.96 | 1.93 | 5 |
| ATR_PERIOD 14 -> 17 | 427 | 58.5 | 0.65 | -1.07 | -0.066 | 0.86 | -11.14 | 17.26 | 2.18 | 5 |

## Robustness: ORB 5m parameters +-20% (IN-SAMPLE, 1x costs)

| Config | Trades | Win % | Avg win R | Avg loss R | Exp. R | PF | Net % | Max DD % | Worst day % | Lose streak |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BASE (defaults) | 260 | 32.7 | 2.69 | -1.03 | 0.186 | 1.21 | 15.71 | 9.04 | 0.75 | 10 |
| ORB_DOJI_BODY_PCT 10.0 -> 8.0 | 264 | 32.2 | 2.69 | -1.03 | 0.167 | 1.19 | 14.26 | 9.34 | 0.75 | 11 |
| ORB_DOJI_BODY_PCT 10.0 -> 12.0 | 256 | 32.0 | 2.70 | -1.03 | 0.165 | 1.18 | 13.18 | 9.04 | 0.75 | 10 |
| ORB_RANGE_MIN_PCTL 20.0 -> 16.0 | 277 | 33.2 | 2.68 | -1.03 | 0.202 | 1.24 | 18.06 | 8.52 | 0.75 | 11 |
| ORB_RANGE_MIN_PCTL 20.0 -> 24.0 | 247 | 34.0 | 2.71 | -1.03 | 0.241 | 1.30 | 20.57 | 8.23 | 0.75 | 10 |
| ORB_RANGE_MAX_PCTL 90.0 -> 72.0 | 193 | 30.6 | 3.05 | -1.04 | 0.207 | 1.25 | 14.50 | 7.05 | 0.75 | 10 |
| ORB_RANGE_MAX_PCTL 90.0 -> 99.0 | 299 | 33.4 | 2.70 | -1.03 | 0.218 | 1.28 | 22.13 | 9.28 | 0.75 | 11 |
| ORB_RANGE_LOOKBACK 20 -> 16 | 258 | 32.9 | 2.66 | -1.03 | 0.188 | 1.21 | 15.05 | 8.24 | 0.75 | 10 |
| ORB_RANGE_LOOKBACK 20 -> 24 | 271 | 34.7 | 2.78 | -1.03 | 0.290 | 1.32 | 23.58 | 5.94 | 0.75 | 10 |

## Exit reasons (full period, 1x costs)

- **RSI2 15m 1.0x**: EMA_EXIT 381, RSI_EXIT 3, SESSION_END 31, STOP 207
- **RSI2 1H 1.0x**: EMA_EXIT 75, SESSION_END 74, STOP 60
- **ORB 5m range-stop 1.0x**: SESSION_END 132, STOP 240
- **ORB 5m range-stop 2R 1.0x**: SESSION_END 35, STOP 217, TARGET 120

## Acceptance criteria

Ready only if OUT-OF-SAMPLE at 1.5x costs: >= 100 trades, PF >= 1.25, max DD <= 6%, worst day <= 2.5%, Monte Carlo firm-breach probability < 15%.

- RSI2 15m 1.5x: **NOT READY: PF 1.01 < 1.25**
- RSI2 1H 1.5x: **NOT READY: trades 54 < 100; PF 0.91 < 1.25**
- RSI2 15m slowEMA800 1.5x: **NOT READY: PF 1.16 < 1.25**
- ORB 5m range-stop 1.5x: **NOT READY: PF 1.04 < 1.25**
- ORB 5m atr-stop 1.5x: **NOT READY: PF 1.24 < 1.25; max DD 8.36% > 6.0%**
- ORB 5m range-stop 2R 1.5x: **NOT READY: PF 0.94 < 1.25**
- ORB RANDOM seed1 1.5x: **NOT READY: trades 98 < 100; PF 0.95 < 1.25**
- ORB RANDOM seed2 1.5x: **NOT READY: trades 97 < 100; PF 0.74 < 1.25**
- ORB RANDOM seed3 1.5x: **NOT READY: trades 95 < 100; PF 0.66 < 1.25; max DD 9.62% > 6.0%**
- ORB RANDOM seed4 1.5x: **NOT READY: trades 98 < 100; PF 0.90 < 1.25; max DD 8.65% > 6.0%**
- ORB RANDOM seed5 1.5x: **NOT READY: trades 97 < 100; PF 0.64 < 1.25; max DD 9.26% > 6.0%**
