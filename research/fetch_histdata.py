"""Download free NAS100 1-minute bars (HistData.com "NSXUSD") and save them as a
close-stamped UTC CSV for the harness.

    python fetch_histdata.py --start-year 2024 --end 2026-11

Output: data/NAS100_1m.csv  (datetime,open,high,low,close,volume)
  - datetime = bar CLOSE time in UTC (same convention as TradeLocker Studio)

HistData's readme says "EST without daylight saving", but the data shows the
clock is UTC-5, moving to UTC-4 on the EUROPEAN daylight-saving dates (last
Sunday of March to last Sunday of October). Checked in research/reports/data_check.md:
winter prices match Dukascopy's UTC feed exactly, the 09:30 New York open and
the 16:15 close land at the right UTC time in every season (including the 2-3
weeks a year when US and European clocks differ), and summer prices match the
TradeLocker NAS100.X prices recorded by the Studio probe.

Days with badly incomplete US cash sessions (e.g. Feb-Jul 2023, about half the
minutes missing) are removed completely; see MIN_SESSION_COVERAGE.

Finished years come as one file per year, the current year as one per month.
HistData's CFD is not TradeLocker's NAS100.X; Studio's backtester stays the
final check.
"""
import argparse
import datetime as dt
import io
import os
import re
import time
import urllib.parse
import urllib.request
import zipfile
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from tl_prop_bot import utc_to_ny  # noqa: E402

MIN_SESSION_COVERAGE = 0.90    # drop a day if under 90% of its 390 cash-session minutes exist


def last_sunday(year, month):
    d = dt.date(year, month, 28)
    while d.month == month:
        d += dt.timedelta(days=1)
    d -= dt.timedelta(days=1)
    while d.weekday() != 6:
        d -= dt.timedelta(days=1)
    return d


def histdata_to_utc(t):
    """HistData clock: UTC-5, or UTC-4 while EU summer time is in force
    (last Sunday March 01:00 UTC to last Sunday October 01:00 UTC)."""
    guess = t + dt.timedelta(hours=5)
    start = dt.datetime.combine(last_sunday(t.year, 3), dt.time(1, 0))
    end = dt.datetime.combine(last_sunday(t.year, 10), dt.time(1, 0))
    return guess - dt.timedelta(hours=1) if start <= guess - dt.timedelta(hours=1) < end else guess

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "data", "histdata")
PAGE = "https://www.histdata.com/download-free-forex-historical-data/?/ascii/1-minute-bar-quotes/nsxusd/{path}"
GET = "https://www.histdata.com/get.php"


def download(period):
    """period = "2024" (year) or "2026/3" (month). Returns CSV text."""
    if "/" in period:
        y, m = period.split("/")
        datemonth = "{}{:02d}".format(y, int(m))
    else:
        y, datemonth = period, period
    out = os.path.join(RAW, "NSXUSD_" + datemonth + ".zip")
    if not (os.path.exists(out) and os.path.getsize(out) > 1000):
        page_url = PAGE.format(path=period)
        with urllib.request.urlopen(page_url, timeout=60) as r:
            html = r.read().decode("utf-8", "replace")
        m = re.search(r'name="tk" id="tk" value="([0-9a-f]+)"', html)
        if not m:
            raise RuntimeError("no download token on " + page_url)
        body = urllib.parse.urlencode({"tk": m.group(1), "date": y, "datemonth": datemonth,
                                       "platform": "ASCII", "timeframe": "M1",
                                       "fxpair": "NSXUSD"}).encode()
        req = urllib.request.Request(GET, data=body, headers={"Referer": page_url})
        with urllib.request.urlopen(req, timeout=120) as r:
            data = r.read()
        if len(data) < 1000:
            raise RuntimeError("empty download for " + period)
        with open(out, "wb") as f:
            f.write(data)
        time.sleep(3)
    with zipfile.ZipFile(out) as z:
        name = [n for n in z.namelist() if n.endswith(".csv")][0]
        return z.read(name).decode()


def parse(text):
    rows = []
    for line in text.splitlines():
        p = line.strip().split(";")
        if len(p) < 5:
            continue
        t = dt.datetime.strptime(p[0], "%Y%m%d %H%M%S")
        close_utc = histdata_to_utc(t) + dt.timedelta(minutes=1)   # bar open -> bar close UTC
        rows.append((close_utc, float(p[1]), float(p[2]), float(p[3]), float(p[4]),
                     float(p[5]) if len(p) > 5 else 0.0))
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--start-year", type=int, default=2024)
    ap.add_argument("--end", default="2026-11", help="last month YYYY-MM (current year by month)")
    ap.add_argument("--out", default=os.path.join(HERE, "data", "NAS100_1m.csv"))
    a = ap.parse_args()
    os.makedirs(RAW, exist_ok=True)
    end_y, end_m = [int(x) for x in a.end.split("-")]
    periods = [str(y) for y in range(a.start_year, end_y)]
    periods += ["{}/{}".format(end_y, m) for m in range(1, end_m + 1)]
    rows = []
    for p in periods:
        try:
            got = parse(download(p))
            print(p, len(got), "bars")
            rows += got
        except Exception as e:      # noqa: BLE001
            print(p, "FAILED:", e)
    rows.sort()
    # drop New York days whose US cash session is badly incomplete
    sess = {}
    for r in rows:
        ny = utc_to_ny(r[0] - dt.timedelta(minutes=1))
        m = ny.hour * 60 + ny.minute
        if ny.weekday() < 5 and 9 * 60 + 30 <= m < 16 * 60:
            sess[ny.date()] = sess.get(ny.date(), 0) + 1
    bad = set(d for d, n in sess.items() if n < MIN_SESSION_COVERAGE * 390)
    if bad:
        print("dropping", len(bad), "incomplete days:", ", ".join(str(d) for d in sorted(bad)))
        rows = [r for r in rows if utc_to_ny(r[0] - dt.timedelta(minutes=1)).date() not in bad]
    with open(a.out, "w") as f:
        f.write("datetime,open,high,low,close,volume\n")
        last = None
        for r in rows:
            if r[0] == last:
                continue
            last = r[0]
            f.write("{:%Y-%m-%d %H:%M:%S},{:.3f},{:.3f},{:.3f},{:.3f},{:.0f}\n".format(*r))
    print("wrote", len(rows), "bars to", a.out)


if __name__ == "__main__":
    main()
