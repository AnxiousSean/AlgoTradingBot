"""Download free NAS100 (Dukascopy "USATECHIDXUSD") 1-minute BID candles and
save them as a close-stamped UTC CSV the harness can read.

    python fetch_dukascopy.py --start 2024-11-25 --end 2026-11-26

Output: data/NAS100_1m.csv with columns datetime,open,high,low,close,volume
  - datetime = bar CLOSE time in UTC (same convention as TradeLocker Studio)
  - flat zero-volume minutes (market closed) are dropped

Notes: Dukascopy's CFD is not TradeLocker's NAS100.X. Prices and session
details differ slightly, which is why Studio's backtest stays the final check.
"""
import argparse
import concurrent.futures as cf
import datetime as dt
import lzma
import os
import struct
import time
import urllib.request

URL = "https://datafeed.dukascopy.com/datafeed/USATECHIDXUSD/{y}/{m:02d}/{d:02d}/BID_candles_min_1.bi5"
HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "data", "raw")
SCALE = 1000.0
PAUSE = 2.0          # seconds between requests (Dukascopy rate-limits)


def fetch_day(day):
    path = os.path.join(RAW, day.strftime("%Y%m%d") + ".bi5")
    if os.path.exists(path):
        return day, path
    url = URL.format(y=day.year, m=day.month - 1, d=day.day)   # month is 0-based
    for attempt in range(40):
        try:
            time.sleep(PAUSE)
            with urllib.request.urlopen(url, timeout=30) as r:
                data = r.read()
            with open(path + ".part", "wb") as f:
                f.write(data)
            os.replace(path + ".part", path)
            return day, path
        except Exception as e:          # noqa: BLE001
            if getattr(e, "code", None) == 404:
                open(path, "wb").close()
                return day, path
            # 429 = too many requests: back off politely
            time.sleep(min(300, 15 * (attempt + 1)))
    raise RuntimeError("failed " + url)


def parse_day(day, path):
    blob = open(path, "rb").read()
    if not blob:
        return []
    raw = lzma.decompress(blob)
    rows = []
    base = dt.datetime(day.year, day.month, day.day)
    for i in range(len(raw) // 24):
        t, o, c, lo, hi, v = struct.unpack(">5if", raw[i * 24:(i + 1) * 24])
        if v <= 0 and o == c == lo == hi:
            continue                     # market closed filler
        close_time = base + dt.timedelta(seconds=t + 60)
        rows.append((close_time, o / SCALE, hi / SCALE, lo / SCALE, c / SCALE, v))
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", default="2024-11-25")
    ap.add_argument("--end", default="2026-11-26")
    ap.add_argument("--out", default=os.path.join(HERE, "data", "NAS100_1m.csv"))
    ap.add_argument("--threads", type=int, default=1)
    a = ap.parse_args()
    os.makedirs(RAW, exist_ok=True)
    d0 = dt.date.fromisoformat(a.start)
    d1 = dt.date.fromisoformat(a.end)
    days = [d0 + dt.timedelta(days=i) for i in range((d1 - d0).days)]
    with cf.ThreadPoolExecutor(a.threads) as ex:
        done = list(ex.map(fetch_day, days))
    n = 0
    with open(a.out, "w") as f:
        f.write("datetime,open,high,low,close,volume\n")
        for day, path in sorted(done):
            for r in parse_day(day, path):
                f.write("{:%Y-%m-%d %H:%M:%S},{:.3f},{:.3f},{:.3f},{:.3f},{:.4f}\n".format(*r))
                n += 1
    print("wrote", n, "bars to", a.out)


if __name__ == "__main__":
    main()
