# Data check: NAS100 1-minute data (HistData NSXUSD, 2018-2026)

HistData's clock is UTC-5, switching to UTC-4 on the EUROPEAN daylight-saving dates. `fetch_histdata.py` converts it to UTC bar-close stamps. Checks:

1. TradeLocker NAS100.X closes from the Studio probe (Sept 2026) minus this data at the same UTC time: [2.62, 2.26, 6.49, 0.28, 0.28, 0.25, 2.54] points.
2. Dukascopy's UTC feed, 21708 overlapping minutes (Nov-Dec 2024): median price difference 0.000, correlation of 1-minute changes 1.0000.
3. Session timing (all years):
   - July: open (09:30-09:34 NY) 1m range = 3.6x the 09:00-09:29 average; median last bar of the day 16:14 NY
   - January: open (09:30-09:34 NY) 1m range = 3.5x the 09:00-09:29 average; median last bar of the day 16:14 NY
   - US/EU mismatch weeks in March: open (09:30-09:34 NY) 1m range = 3.2x the 09:00-09:29 average; median last bar of the day 16:14 NY
4. Cash-session coverage: 2098 trading days kept, median 390 of 390 minutes, minimum 361.
   Days under 90% coverage were removed (US holidays, half days, and much of Feb-Jul 2023 where HistData is missing about half the minutes).

| Year | Bars | First close | Last close |
|---|---:|---:|---:|
| 2018 | 338137 | 6383 | 6341 |
| 2019 | 332125 | 6338 | 8745 |
| 2020 | 331897 | 8750 | 12883 |
| 2021 | 336453 | 12897 | 16341 |
| 2022 | 333944 | 16385 | 10958 |
| 2023 | 192779 | 11022 | 16824 |
| 2024 | 327162 | 16829 | 21036 |
| 2025 | 330940 | 21056 | 25249 |
| 2026 | 291451 | 25283 | 27862 |
