# Data check: NAS100 1-minute data (HistData NSXUSD)

1. Studio NAS100.X closes (Sept 2026, summer time) minus this data at the same UTC time: [np.float64(2.62), np.float64(2.26), np.float64(6.49), np.float64(0.28), np.float64(0.28), np.float64(0.25), np.float64(2.54)]
2. Dukascopy UTC feed, 23641 overlapping minutes (Nov-Dec 2024): median |price diff| 0.000, correlation of 1m changes 1.0000
3. Jun-Aug: average 1m range in the 5 minutes from 12:30 / 13:30 / 14:30 UTC = 16.0 / 30.4 / 19.7
3. Dec-Feb: average 1m range in the 5 minutes from 12:30 / 13:30 / 14:30 UTC = 6.0 / 14.5 / 29.0

Expected: cash open 09:30 New York = 13:30 UTC in summer, 14:30 UTC in winter.

Range: 2024-01-01 23:01:00 to 2026-11-13 21:14:00 UTC, 980184 bars.
