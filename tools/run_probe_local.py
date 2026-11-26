"""Run probe_bot.py locally on synthetic data to verify it never crashes.

Usage: .venv/bin/python tools/run_probe_local.py [lots|units]
  lots  : commission info with mult=100000 (size 1 = 1 standard lot)
  units : default backtrader broker (size 1 = 1 unit of base currency)
"""
import sys, os, datetime, random, importlib.util
import backtrader as bt
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("probe_bot", os.path.join(HERE, "..", "probe_bot.py"))
probe = importlib.util.module_from_spec(spec); sys.modules["probe_bot"] = probe; spec.loader.exec_module(probe)


def synthetic_h1(start="2024-01-07 22:00", bars=2000, seed=1):
    random.seed(seed)
    rows, t, p = [], pd.Timestamp(start), 1.10
    while len(rows) < bars:
        # FX week: Sun 22:00 UTC -> Fri 21:00 UTC
        wd, h = t.weekday(), t.hour
        closed = (wd == 4 and h >= 21) or wd == 5 or (wd == 6 and h < 22)
        if not closed:
            vol = 0.0012 if 12 <= h <= 16 else 0.0005
            o = p; c = o * (1 + random.gauss(0, vol))
            hi = max(o, c) * (1 + abs(random.gauss(0, vol / 2)))
            lo = min(o, c) * (1 - abs(random.gauss(0, vol / 2)))
            rows.append((t, o, hi, lo, c, 100)); p = c
        t += pd.Timedelta(hours=1)
    df = pd.DataFrame(rows, columns=["dt", "open", "high", "low", "close", "volume"]).set_index("dt")
    return df


def main(mode):
    cer = bt.Cerebro(stdstats=False)
    cer.adddata(bt.feeds.PandasData(dataname=synthetic_h1(), timeframe=bt.TimeFrame.Minutes, compression=60), name="EURUSD")
    cer.broker.setcash(5000.0)
    if mode == "lots":
        cer.broker.setcommission(commission=5.0, commtype=bt.CommInfoBase.COMM_FIXED, mult=100000,
                                 margin=1100.0, stocklike=False)  # NOTE: leverage= double-counts open P&L in getvalue()
    cer.addstrategy(probe.ProbeStrategy)
    cer.run()


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "lots")
