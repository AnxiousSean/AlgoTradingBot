"""Smoke test: run probe/probe_bot.py under stock Backtrader on synthetic
XAUUSD-like M5 bars, to catch crashes before it goes to Studio.

This proves only that the probe runs and its logic works on STOCK Backtrader.
It says nothing about Studio's behaviour -- that is what the probe is for.
"""
import contextlib
import datetime as dt
import io
import os
import random
import sys
from zoneinfo import ZoneInfo

import backtrader as bt
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'probe'))
import probe_bot  # noqa: E402

NY = ZoneInfo('America/New_York')
SERVER = ZoneInfo('Etc/GMT-2')   # fixed UTC+2 "server" for the test
# (Etc/GMT-2 means UTC+2; sign is inverted in the tz database)


def make_bars(start_utc, end_utc, seed=1):
    rnd = random.Random(seed)
    rows, px = [], 2600.0
    t = start_utc
    while t < end_utc:
        ny = t.astimezone(NY)
        closed = (ny.hour == 17 or ny.weekday() == 5
                  or (ny.weekday() == 4 and ny.hour >= 17)
                  or (ny.weekday() == 6 and ny.hour < 18))
        if not closed:
            o = px
            c = o * (1 + rnd.gauss(0, 0.0008))
            h = max(o, c) * (1 + abs(rnd.gauss(0, 0.0004)))
            lo = min(o, c) * (1 - abs(rnd.gauss(0, 0.0004)))
            rows.append((t.astimezone(SERVER).replace(tzinfo=None), o, h, lo, c, 100))
            px = c
        t += dt.timedelta(minutes=5)
    df = pd.DataFrame(rows, columns=['dt', 'open', 'high', 'low', 'close', 'volume'])
    return df.set_index('dt')


def run_probe():
    df = make_bars(dt.datetime(2026, 2, 2, tzinfo=dt.timezone.utc),
                   dt.datetime(2026, 3, 20, tzinfo=dt.timezone.utc))
    cerebro = bt.Cerebro()
    cerebro.adddata(bt.feeds.PandasData(dataname=df, timeframe=bt.TimeFrame.Minutes,
                                        compression=5))
    cerebro.addstrategy(probe_bot.ProbeStrategy, bar_stamp='open')
    cerebro.broker.setcash(5000.0)
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        cerebro.run()
    return buf.getvalue()


def test_probe_runs_and_summarises():
    out = run_probe()
    summary = [l for l in out.splitlines() if l.startswith('PROBE|SUMMARY|')]
    assert summary, out[-2000:]
    text = '\n'.join(summary)
    for t in ('T1_MARKET', 'T2_STOP_ENTRY', 'T3_LIMIT_ENTRY', 'T4_CANCEL',
              'T5_VALID_EXPIRY', 'T6_OCO', 'T7_BRACKET_LONG', 'T8_BRACKET_SHORT'):
        line = [l for l in summary if t in l][0]
        assert 'NOT RUN' not in line and 'EXCEPTION' not in line, line
    assert 'Canceled' in [l for l in summary if 'T4_CANCEL' in l][0]
    assert 'EXPIRED' in [l for l in summary if 'T5_VALID_EXPIRY' in l][0]
    # stock bt: stocklike, mult=1 -> 1.0 value per point per unit
    assert 'value per 1.0 price move' in text
    # server is UTC+2 in our synthetic data: the vote must say +2
    votes = [l for l in summary if 'offset votes' in l][0]
    assert votes.split(':')[-1].strip().startswith('+2.0'), votes
    # never both a long and a short open: position must end flat
    assert 'EXCEPTION' not in out


if __name__ == '__main__':
    print(run_probe())


class StudioLikeData(bt.feeds.PandasData):
    """Mimics Studio's TLData: UTC bar-END stamps plus bid/ask/mid lines."""
    lines = ('ask', 'bid', 'mid')
    params = (('ask', 'ask'), ('bid', 'bid'), ('mid', 'mid'))


def test_probe_on_studio_like_feed():
    df = make_bars(dt.datetime(2026, 11, 2, tzinfo=dt.timezone.utc),
                   dt.datetime(2026, 11, 20, tzinfo=dt.timezone.utc))
    # re-stamp to UTC bar end (open + 5 min - 1 ms), like Studio
    df.index = (df.index - pd.Timedelta(hours=2) + pd.Timedelta(minutes=5)
                - pd.Timedelta(milliseconds=1))
    df['bid'] = df['close']
    df['ask'] = df['close'] + 0.30
    df['mid'] = df['close'] + 0.15
    cerebro = bt.Cerebro()
    cerebro.adddata(StudioLikeData(dataname=df, timeframe=bt.TimeFrame.Minutes, compression=5))
    cerebro.addstrategy(probe_bot.ProbeStrategy)          # default bar_stamp='end'
    cerebro.broker.setcash(5000.0)
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        cerebro.run()
    summary = [l for l in buf.getvalue().splitlines() if l.startswith('PROBE|SUMMARY|')]
    votes = [l for l in summary if 'offset votes' in l][0]
    assert votes.split(':')[-1].strip().startswith('+0.0'), votes
    sp = [l for l in summary if 'spread (ask-bid' in l][0]
    assert 'median=0.3' in sp, sp
    assert [l for l in summary if 'close equals: bid x' in l and 'ask x0' in l], summary
