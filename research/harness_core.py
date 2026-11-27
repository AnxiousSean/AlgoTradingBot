"""Shared pieces of the local research harness: build a Backtrader run of the
SAME tl_prop_bot.py file Studio runs, with costs modelled the way Studio's
broker values NAS100.X (size in lots, $10 per point per lot)."""
import datetime as dt
import os
import random
import sys

import backtrader as bt
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import tl_prop_bot  # noqa: E402


class LotCommission(bt.CommInfoBase):
    """Lots x points x VALUE_PER_POINT_PER_LOT, plus a fixed cost per lot per side.
    cost_points is the ROUND-TRIP spread+slippage in index points."""
    params = (
        ("stocklike", False),
        ("commtype", bt.CommInfoBase.COMM_FIXED),
        ("value_per_point", 10.0),
        ("cost_points", 2.5),
        ("leverage_", 20.0),
    )

    def __init__(self):
        super().__init__()
        self.p.mult = self.p.value_per_point
        self.p.commission = self.p.cost_points / 2.0 * self.p.value_per_point

    def _getcommission(self, size, price, pseudoexec):
        return abs(size) * self.p.commission

    def get_margin(self, price):
        return price * self.p.value_per_point / self.p.leverage_


def synthetic_bars(days=120, seed=7, start=dt.datetime(2026, 1, 5), minutes=5, price=30000.0):
    """NAS100-like 5m bars around the clock on weekdays, stamped at bar CLOSE
    (like Studio). Trending regimes + bigger moves in the US cash session.
    Only for testing that the code works, never for judging a strategy."""
    rng = random.Random(seed)
    rows = []
    t = start
    end = start + dt.timedelta(days=days)
    drift = 0.0
    while t < end:
        bar_open = t
        t = t + dt.timedelta(minutes=minutes)
        ny = tl_prop_bot.utc_to_ny(bar_open)
        if ny.weekday() == 5 or (ny.weekday() == 4 and ny.hour >= 17) or (ny.weekday() == 6 and ny.hour < 18):
            continue
        if ny.hour == 17:            # daily break 17:00-18:00 NY
            continue
        if rng.random() < 0.002:
            drift = rng.gauss(0, 0.15)
        in_session = (ny.hour > 9 or (ny.hour == 9 and ny.minute >= 30)) and ny.hour < 16
        vol = 14.0 if in_session else 5.0
        o = price
        path = [o]
        for _ in range(4):
            path.append(path[-1] + drift + rng.gauss(0, vol / 2.0))
        c = path[-1]
        h = max(path) + abs(rng.gauss(0, vol / 4))
        lo = min(path) - abs(rng.gauss(0, vol / 4))
        rows.append((t, round(o, 2), round(h, 2), round(lo, 2), round(c, 2), 100))
        price = c
    df = pd.DataFrame(rows, columns=["datetime", "open", "high", "low", "close", "volume"])
    return df.set_index("datetime")


def resample(df, minutes):
    """Close-stamped resample (bar labelled by its end time)."""
    rule = str(minutes) + "min"
    out = df.resample(rule, label="right", closed="right").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
    return out.dropna()


def run_bot(df, minutes, settings=None, cost_points=2.5, value_per_point=10.0, leverage=20.0,
            news=None, verbose=False):
    """Run TLPropBot on a close-stamped OHLCV DataFrame. Returns the strategy."""
    s = dict(settings or {})
    s.setdefault("VERBOSE", verbose)
    # Research runs need the whole trade sequence; the Monte Carlo applies the
    # target / drawdown rules afterwards. Pass USE_TARGET_LOCK=True to test the lock.
    s.setdefault("USE_TARGET_LOCK", False)
    s.setdefault("VALUE_PER_POINT_PER_LOT", value_per_point)
    s.setdefault("LEVERAGE", leverage)
    old_news = list(tl_prop_bot.SETTINGS["NEWS_EVENTS_NY"])
    tl_prop_bot.SETTINGS["NEWS_EVENTS_NY"] = list(news or [])
    try:
        cerebro = bt.Cerebro(stdstats=False)
        feed = bt.feeds.PandasData(dataname=df, timeframe=bt.TimeFrame.Minutes, compression=minutes)
        cerebro.adddata(feed)
        cerebro.broker.setcash(float(s.get("INITIAL_BALANCE", tl_prop_bot.SETTINGS["INITIAL_BALANCE"])))
        cerebro.broker.addcommissioninfo(LotCommission(value_per_point=value_per_point,
                                                       cost_points=cost_points, leverage_=leverage))
        cerebro.addstrategy(tl_prop_bot.TLPropBot, **s)
        return cerebro.run()[0]
    finally:
        tl_prop_bot.SETTINGS["NEWS_EVENTS_NY"] = old_news
