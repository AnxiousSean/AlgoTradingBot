"""Mechanical checks of TLPropBot on synthetic data: does every trade obey the
prop rules? (Says nothing about profitability.)"""
import datetime as dt

import pytest

from harness_core import resample, run_bot, synthetic_bars


@pytest.fixture(scope="module")
def bars5():
    return synthetic_bars(days=150, seed=11)


def check_rules(strat, label):
    recs = strat.trade_records
    assert recs, label + ": expected some trades on synthetic data"
    g = strat.guard
    assert g.firm_breach is None, g.firm_breach
    per_day = {}
    for r in recs:
        ny_in, ny_out = r["entry_time_ny"], r["exit_time_ny"]
        assert ny_in is not None and r["stop"] is not None
        assert r["held_min"] >= 2.0, (label, r)                       # min hold
        assert ny_in.weekday() < 5
        t_in = ny_in.hour * 60 + ny_in.minute
        first = 9 * 60 + 35 if label.startswith("ORB") else 9 * 60 + 45
        assert first <= t_in <= 15 * 60 + 15, (label, r)              # entry window (+1 bar)
        t_out = ny_out.hour * 60 + ny_out.minute
        assert t_out <= 16 * 60, (label, r)                           # flat by session end
        assert not (ny_in.weekday() == 4 and t_in >= 14 * 60), r      # Friday last 3h
        assert r["lots"] <= 0.30 + 1e-9
        risk = abs(r["entry"] - r["stop"]) * r["lots"] * 10.0
        assert risk <= 25.0 * 1.05 + 1e-9, (label, r)                 # 0.5% of 5000 (+gap at fill)
        per_day[r["day"]] = per_day.get(r["day"], 0) + 1
    assert max(per_day.values()) <= 3
    assert g.worst_day_pct > -4.0
    return recs


def test_rsi2_15m(bars5):
    strat = run_bot(resample(bars5, 15), 15, {"STRATEGY": "RSI2"})
    recs = check_rules(strat, "RSI2")
    reasons = set(r["reason"] for r in recs)
    assert reasons <= {"EMA_EXIT", "RSI_EXIT", "TIME_STOP", "STOP", "SESSION_END",
                       "DAILY_STOP", "TOTAL_STOP", "TARGET_LOCK", "NEWS_FLATTEN", "WEEKEND"}


def test_rsi2_1h_with_slow_trend(bars5):
    strat = run_bot(resample(bars5, 60), 60, {"STRATEGY": "RSI2", "USE_SLOW_TREND": True,
                                               "SLOW_TREND_EMA": 200, "TREND_EMA": 50})
    if strat.trade_records:
        check_rules(strat, "RSI2-1H")


@pytest.mark.parametrize("extra", [{}, {"ORB_STOP_MODE": "atr"}, {"ORB_TARGET_R": 2.0},
                                   {"RANDOM_DIRECTION": True}])
def test_orb_5m(bars5, extra):
    s = {"STRATEGY": "ORB"}
    s.update(extra)
    strat = run_bot(bars5, 5, s)
    recs = check_rules(strat, "ORB " + str(extra))
    assert len(set(r["day"] for r in recs)) == len(recs)              # one trade per day


def test_orb_random_is_seeded(bars5):
    a = run_bot(bars5, 5, {"STRATEGY": "ORB", "RANDOM_DIRECTION": True, "RANDOM_SEED": 3})
    b = run_bot(bars5, 5, {"STRATEGY": "ORB", "RANDOM_DIRECTION": True, "RANDOM_SEED": 3})
    c = run_bot(bars5, 5, {"STRATEGY": "ORB", "RANDOM_DIRECTION": True, "RANDOM_SEED": 4})
    da = [r["direction"] for r in a.trade_records]
    assert da == [r["direction"] for r in b.trade_records]
    assert da != [r["direction"] for r in c.trade_records]


def test_news_blackout_blocks_entries(bars5):
    base = run_bot(bars5, 5, {"STRATEGY": "ORB"})
    first = base.trade_records[0]["entry_time_ny"]
    news = [first.strftime("%Y-%m-%d %H:%M")]
    blocked = run_bot(bars5, 5, {"STRATEGY": "ORB"}, news=news)
    ev = dt.datetime.strptime(news[0], "%Y-%m-%d %H:%M")
    for r in blocked.trade_records:
        assert not (ev - dt.timedelta(minutes=20) <= r["entry_time_ny"] <= ev + dt.timedelta(minutes=10))


def test_daily_stop_with_huge_risk(bars5):
    # 2% per trade and 3 entries/day: the internal 2.5% daily stop must hold
    strat = run_bot(resample(bars5, 15), 15, {"STRATEGY": "RSI2", "RISK_PER_TRADE_PCT": 2.0,
                                               "MAX_LOT": 5.0})
    assert strat.guard.firm_breach is None
    assert strat.guard.worst_day_pct > -4.0


def test_target_lock_stops_trading(bars5):
    strat = run_bot(bars5, 5, {"STRATEGY": "ORB", "USE_TARGET_LOCK": True, "STEP_TARGET_PCT": 0.5,
                               "TARGET_BUFFER_PCT": 0.0})
    g = strat.guard
    if not g.target_locked:
        pytest.skip("synthetic run never reached +0.5%")
    lock_eq = g.target_level
    # after the lock no new trade may start
    eq = 5000.0
    locked_at = None
    for r in strat.trade_records:
        if locked_at is not None:
            assert r["entry_time_ny"] < locked_at
        eq += r["pnl"]
        if eq >= lock_eq and locked_at is None:
            locked_at = r["exit_time_ny"]
