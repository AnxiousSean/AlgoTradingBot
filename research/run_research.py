"""Stage 3 research runner.

Runs the SAME tl_prop_bot.py strategy file on local NAS100 data and writes
markdown reports to research/reports/.

    python run_research.py                    # everything
    python run_research.py --quick            # fewer robustness runs

What it does (matches the project brief):
  * costs: every test at 1x and 1.5x the round-trip cost (default 2.5 points)
  * split: first 70% of the calendar = in-sample, last 30% = out-of-sample
           (trades are assigned by entry time; indicators warm up on all data)
  * robustness: each key parameter at -20% / +20%, on IN-SAMPLE only
  * Monte Carlo: 10,000 runs resampling out-of-sample DAYS against the
    4% daily / 10% max / step-target rules
  * comparisons: RSI2 vs ORB, ORB vs RANDOM_DIRECTION (several seeds)

Research runs switch OFF the bot's target lock and its permanent -7% stop so
the full trade sequence can be measured; the Monte Carlo then applies the
prop rules (and the bot's internal stops) to that sequence.
"""
import argparse
import datetime as dt
import math
import multiprocessing as mp
import os
import random
import statistics
import time

import pandas as pd

from harness_core import resample, run_bot

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data", "NAS100_1m.csv")
REPORTS = os.path.join(HERE, "reports")
INITIAL = 5000.0
BASE_COST = 2.5
RESEARCH_SETTINGS = {"USE_TARGET_LOCK": False, "INTERNAL_TOTAL_STOP_PCT": 99.0}

# ------------------------------------------------------------------ acceptance
ACCEPT = {"trades": 100, "pf": 1.25, "max_dd_pct": 6.0, "worst_day_pct": 2.5, "breach_prob": 15.0}


# ------------------------------------------------------------------ data
def load_bars(path=None):
    path = path or os.environ.get("NAS100_CSV", DATA)
    """CSV with datetime (UTC, bar CLOSE), open, high, low, close, volume."""
    df = pd.read_csv(path, parse_dates=["datetime"]).set_index("datetime").sort_index()
    df = df[~df.index.duplicated(keep="last")]
    return df


_BARS = {}


def bars_for(minutes):
    if minutes not in _BARS:
        one = load_bars()
        _BARS[minutes] = one if minutes == 1 else resample(one, minutes)
    return _BARS[minutes]


# ------------------------------------------------------------------ one run
def run_config(job):
    name, minutes, settings, cost = job
    s = dict(RESEARCH_SETTINGS)
    s.update(settings)
    t0 = time.time()
    strat = run_bot(bars_for(minutes), minutes, s, cost_points=cost)
    recs = []
    for r in strat.trade_records:
        recs.append({k: r[k] for k in ("entry_time_ny", "exit_time_ny", "day", "direction", "lots",
                                       "entry", "stop", "pnl", "r", "reason", "held_min")})
    return {"name": name, "minutes": minutes, "settings": settings, "cost": cost,
            "trades": recs, "seconds": time.time() - t0}


def run_many(jobs, procs):
    if procs <= 1:
        return [run_config(j) for j in jobs]
    with mp.Pool(procs) as pool:
        return pool.map(run_config, jobs)


# ------------------------------------------------------------------ metrics
def split_date(df):
    start, end = df.index[0], df.index[-1]
    return start + (end - start) * 0.70


def subset(trades, lo=None, hi=None):
    out = []
    for t in trades:
        e = t["entry_time_ny"]
        if lo is not None and e < lo:
            continue
        if hi is not None and e >= hi:
            continue
        out.append(t)
    return out


def metrics(trades):
    n = len(trades)
    if n == 0:
        return {"trades": 0}
    pnl = [t["pnl"] for t in trades]
    rs = [t["r"] for t in trades if t["r"] is not None]
    wins = [r for r in rs if r > 0]
    losses = [r for r in rs if r <= 0]
    gross_w = sum(p for p in pnl if p > 0)
    gross_l = -sum(p for p in pnl if p <= 0)
    eq, peak, max_dd = INITIAL, INITIAL, 0.0
    for p in pnl:
        eq += p
        peak = max(peak, eq)
        max_dd = max(max_dd, peak - eq)
    days = {}
    for t in trades:
        days[t["day"]] = days.get(t["day"], 0.0) + t["pnl"]
    streak = best = 0
    for p in pnl:
        streak = streak + 1 if p <= 0 else 0
        best = max(best, streak)
    return {
        "trades": n,
        "win_rate": 100.0 * len(wins) / len(rs) if rs else 0.0,
        "avg_win_r": statistics.mean(wins) if wins else 0.0,
        "avg_loss_r": statistics.mean(losses) if losses else 0.0,
        "expectancy_r": statistics.mean(rs) if rs else 0.0,
        "pf": gross_w / gross_l if gross_l > 0 else float("inf"),
        "net": sum(pnl),
        "net_pct": 100.0 * sum(pnl) / INITIAL,
        "max_dd_pct": 100.0 * max_dd / INITIAL,
        "worst_day_pct": 100.0 * -min(0.0, min(days.values())) / INITIAL,
        "losing_streak": best,
        "trade_days": len(days),
    }


# ------------------------------------------------------------------ Monte Carlo
def monte_carlo(trades, all_days, target_pct=8.0, runs=10000, seed=1, max_days=750,
                internal_daily=2.5, internal_total=7.0, firm_daily=4.0, firm_max=10.0, min_days=3):
    """Resample whole DAYS (with their trades in order) from the out-of-sample
    period, including days with no trade, and walk the prop rules forward.
    Outcomes: PASS (target reached with >= min trading days), BREACH (firm
    daily or max-loss limit crossed), STOPPED (bot's own -7% stop hit), or
    UNFINISHED after max_days trading days."""
    by_day = {}
    for t in trades:
        by_day.setdefault(t["day"], []).append(t["pnl"])
    pool = [by_day.get(d, []) for d in all_days]
    if not pool:
        return None
    rng = random.Random(seed)
    target = INITIAL * (1 + target_pct / 100.0)
    floor = INITIAL * (1 - firm_max / 100.0)
    stop_floor = INITIAL * (1 - internal_total / 100.0)
    out = {"PASS": 0, "BREACH": 0, "STOPPED": 0, "UNFINISHED": 0}
    days_to_pass = []
    for _ in range(runs):
        eq = INITIAL
        traded = 0
        result = "UNFINISHED"
        for day_i in range(1, max_days + 1):
            day = pool[rng.randrange(len(pool))]
            start = eq
            allowed_int = internal_daily / 100.0 * min(INITIAL, start)
            allowed_firm = firm_daily / 100.0 * min(INITIAL, start)
            if day:
                traded += 1
            for p in day:
                eq += p
                if eq <= start - allowed_firm or eq <= floor:
                    result = "BREACH"
                    break
                if eq <= start - allowed_int:
                    break                      # bot stops for the day
            if result == "BREACH":
                break
            if eq <= stop_floor:
                result = "STOPPED"
                break
            if eq >= target and traded >= min_days:
                result = "PASS"
                days_to_pass.append(day_i)
                break
        out[result] += 1
    res = {k: 100.0 * v / runs for k, v in out.items()}
    res["median_days"] = statistics.median(days_to_pass) if days_to_pass else None
    return res


# ------------------------------------------------------------------ jobs
RSI2_BASE = {"STRATEGY": "RSI2"}
ORB_BASE = {"STRATEGY": "ORB"}
RSI2_GRID = [("RSI_LONG_ENTRY", 10.0, "RSI_SHORT_ENTRY", 90.0), ("TREND_EMA", 200, None, None),
             ("STOP_ATR_MULT", 1.5, None, None), ("TIME_STOP_BARS", 12, None, None),
             ("EXIT_EMA", 5, None, None), ("ATR_PERIOD", 14, None, None)]
ORB_GRID = [("ORB_DOJI_BODY_PCT", 10.0, None, None), ("ORB_RANGE_MIN_PCTL", 20.0, None, None),
            ("ORB_RANGE_MAX_PCTL", 90.0, None, None), ("ORB_RANGE_LOOKBACK", 20, None, None)]


def grid_variants(base, grid):
    out = []
    for key, val, mirror_key, mirror_val in grid:
        for f in (0.8, 1.2):
            s = dict(base)
            v = val * f
            if isinstance(val, int):
                v = max(1, int(round(v)))
            if key == "ORB_RANGE_MAX_PCTL":
                v = min(99.0, v)
            s[key] = v
            label = "{} {} -> {}".format(key, val, round(v, 2))
            if mirror_key:
                s[mirror_key] = 100.0 - v     # keep RSI thresholds symmetric
                label += " ({} {})".format(mirror_key, round(100.0 - v, 2))
            out.append((label, s))
    return out


def build_jobs(quick):
    jobs = []
    for cost_mult in (1.0, 1.5):
        c = BASE_COST * cost_mult
        tag = "{}x".format(cost_mult)
        jobs += [
            ("RSI2 15m " + tag, 15, dict(RSI2_BASE), c),
            ("RSI2 1H " + tag, 60, dict(RSI2_BASE), c),
            ("RSI2 15m slowEMA800 " + tag, 15, dict(RSI2_BASE, USE_SLOW_TREND=True), c),
            ("ORB 5m range-stop " + tag, 5, dict(ORB_BASE), c),
            ("ORB 5m atr-stop " + tag, 5, dict(ORB_BASE, ORB_STOP_MODE="atr"), c),
            ("ORB 5m range-stop 2R " + tag, 5, dict(ORB_BASE, ORB_TARGET_R=2.0), c),
        ]
        seeds = (1, 2, 3) if quick else (1, 2, 3, 4, 5)
        for sd in seeds:
            jobs.append(("ORB RANDOM seed{} {}".format(sd, tag), 5,
                         dict(ORB_BASE, RANDOM_DIRECTION=True, RANDOM_SEED=sd), c))
    grid = RSI2_GRID if not quick else RSI2_GRID[:3]
    for label, s in grid_variants(RSI2_BASE, grid):
        jobs.append(("GRID RSI2 15m " + label, 15, s, BASE_COST))
    ogrid = ORB_GRID if not quick else ORB_GRID[:2]
    for label, s in grid_variants(ORB_BASE, ogrid):
        jobs.append(("GRID ORB 5m " + label, 5, s, BASE_COST))
    return jobs


# ------------------------------------------------------------------ report
def fmt(v, d=2):
    if v is None:
        return "-"
    if isinstance(v, float):
        if math.isinf(v):
            return "inf"
        return ("{:." + str(d) + "f}").format(v)
    return str(v)


COLS = [("trades", "Trades", 0), ("win_rate", "Win %", 1), ("avg_win_r", "Avg win R", 2),
        ("avg_loss_r", "Avg loss R", 2), ("expectancy_r", "Exp. R", 3), ("pf", "PF", 2),
        ("net_pct", "Net %", 2), ("max_dd_pct", "Max DD %", 2), ("worst_day_pct", "Worst day %", 2),
        ("losing_streak", "Lose streak", 0)]


def table(rows):
    head = "| Config | " + " | ".join(c[1] for c in COLS) + " |"
    sep = "|---|" + "|".join("---:" for _ in COLS) + "|"
    lines = [head, sep]
    for name, m in rows:
        if m.get("trades", 0) == 0:
            lines.append("| " + name + " | 0 |" + " |" * (len(COLS) - 1))
            continue
        lines.append("| " + name + " | " + " | ".join(fmt(m.get(k), d) for k, _, d in COLS) + " |")
    return "\n".join(lines)


def verdict(m, mc):
    fails = []
    if m.get("trades", 0) < ACCEPT["trades"]:
        fails.append("trades {} < {}".format(m.get("trades", 0), ACCEPT["trades"]))
    if m.get("trades", 0) and m["pf"] < ACCEPT["pf"]:
        fails.append("PF {:.2f} < {}".format(m["pf"], ACCEPT["pf"]))
    if m.get("trades", 0) and m["max_dd_pct"] > ACCEPT["max_dd_pct"]:
        fails.append("max DD {:.2f}% > {}%".format(m["max_dd_pct"], ACCEPT["max_dd_pct"]))
    if m.get("trades", 0) and m["worst_day_pct"] > ACCEPT["worst_day_pct"]:
        fails.append("worst day {:.2f}% > {}%".format(m["worst_day_pct"], ACCEPT["worst_day_pct"]))
    if mc is None or mc["BREACH"] >= ACCEPT["breach_prob"]:
        fails.append("MC breach {}% >= {}%".format(fmt(mc and mc["BREACH"], 1), ACCEPT["breach_prob"]))
    return ("READY" if not fails else "NOT READY: " + "; ".join(fails))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true")
    ap.add_argument("--procs", type=int, default=max(1, mp.cpu_count()))
    ap.add_argument("--mc-runs", type=int, default=10000)
    ap.add_argument("--data", default=None, help="1-minute CSV (default data/NAS100_1m.csv)")
    ap.add_argument("--out", default="stage3_report.md")
    a = ap.parse_args()
    if a.data:
        os.environ["NAS100_CSV"] = os.path.abspath(a.data)
    os.makedirs(REPORTS, exist_ok=True)

    one = bars_for(1)
    cut_utc = split_date(one)
    import tl_prop_bot
    cut_ny = tl_prop_bot.utc_to_ny(cut_utc.to_pydatetime())
    # firm trading days in the out-of-sample period (for Monte Carlo day pool)
    oos_days = sorted(set(tl_prop_bot.trading_day_of(tl_prop_bot.utc_to_ny(t.to_pydatetime()))
                          for t in one.index[one.index >= cut_utc][::60]))
    oos_days = [d for d in oos_days if d.weekday() < 5]

    jobs = build_jobs(a.quick)
    t0 = time.time()
    results = run_many(jobs, a.procs)
    elapsed = time.time() - t0
    res = {r["name"]: r for r in results}

    lines = ["# Stage 3 research report", ""]
    lines.append("Generated {} from `{}`, {} 1-minute bars, {} to {} UTC.".format(
        dt.datetime.now().strftime("%Y-%m-%d %H:%M"),
        os.path.relpath(os.environ.get("NAS100_CSV", DATA), HERE), len(one),
        one.index[0], one.index[-1]))
    lines.append("In-sample: before {:%Y-%m-%d %H:%M} NY. Out-of-sample: after. "
                 "OOS trading days in Monte Carlo pool: {}.".format(cut_ny, len(oos_days)))
    lines.append("Costs: 1x = {} points round trip, 1.5x = {} points. Risk 0.5% ($25) per trade, "
                 "1:20 leverage, 30% margin cap. {} backtests in {:.0f} s.".format(
                     BASE_COST, BASE_COST * 1.5, len(jobs), elapsed))
    lines.append("")
    lines.append("Data source: HistData.com NSXUSD 1m bars (same feed as Dukascopy USATECHIDXUSD; not TradeLocker's feed, but matches NAS100.X within a few points, see data_check.md).")
    lines.append("")

    main_names = [j[0] for j in jobs if not j[0].startswith("GRID")]
    for period, lo, hi in (("Out-of-sample", cut_ny, None), ("In-sample", None, cut_ny)):
        rows = [(n, metrics(subset(res[n]["trades"], lo, hi))) for n in main_names]
        lines += ["## " + period, "", table(rows), ""]

    # Monte Carlo + verdict on OOS 1.5x
    lines += ["## Monte Carlo (out-of-sample, 1.5x costs, {} runs, Step 1 target 8%)".format(a.mc_runs), "",
              "| Config | Pass % | Firm breach % | Bot -7% stop % | Unfinished % | Median days to pass | Verdict |",
              "|---|---:|---:|---:|---:|---:|---|"]
    verdicts = {}
    for n in main_names:
        if not n.endswith("1.5x"):
            continue
        tr = subset(res[n]["trades"], cut_ny, None)
        mc = monte_carlo(tr, oos_days, runs=a.mc_runs)
        v = verdict(metrics(tr), mc)
        verdicts[n] = v
        lines.append("| {} | {} | {} | {} | {} | {} | {} |".format(
            n, fmt(mc["PASS"], 1), fmt(mc["BREACH"], 1), fmt(mc["STOPPED"], 1),
            fmt(mc["UNFINISHED"], 1), fmt(mc["median_days"], 0), v))
    lines.append("")

    # ORB vs random
    lines += ["## ORB vs random direction (out-of-sample, 1x costs)", ""]
    real = metrics(subset(res["ORB 5m range-stop 1.0x"]["trades"], cut_ny, None))
    rnd = [metrics(subset(res[n]["trades"], cut_ny, None)) for n in main_names
           if n.startswith("ORB RANDOM") and n.endswith("1.0x")]
    rnd = [m for m in rnd if m.get("trades")]
    if rnd and real.get("trades"):
        exps = [m["expectancy_r"] for m in rnd]
        lines.append("Real ORB expectancy {:+.3f} R over {} trades. Random seeds: {} "
                     "(mean {:+.3f} R).".format(real["expectancy_r"], real["trades"],
                                                ", ".join("{:+.3f}".format(e) for e in exps),
                                                statistics.mean(exps)))
        better = len([e for e in exps if real["expectancy_r"] > e])
        lines.append("Real signal beats {} of {} random seeds.".format(better, len(exps)))
    lines.append("")

    # Robustness grid
    for strat, base_name in (("RSI2 15m", "RSI2 15m 1.0x"), ("ORB 5m", "ORB 5m range-stop 1.0x")):
        rows = [("BASE (defaults)", metrics(subset(res[base_name]["trades"], None, cut_ny)))]
        for j in jobs:
            if j[0].startswith("GRID " + strat):
                rows.append((j[0].replace("GRID " + strat + " ", ""), metrics(subset(res[j[0]]["trades"], None, cut_ny))))
        lines += ["## Robustness: {} parameters +-20% (IN-SAMPLE, 1x costs)".format(strat), "", table(rows), ""]

    # Exit reasons
    lines += ["## Exit reasons (full period, 1x costs)", ""]
    for n in ("RSI2 15m 1.0x", "RSI2 1H 1.0x", "ORB 5m range-stop 1.0x", "ORB 5m range-stop 2R 1.0x"):
        cnt = {}
        for t in res[n]["trades"]:
            cnt[t["reason"]] = cnt.get(t["reason"], 0) + 1
        lines.append("- **{}**: {}".format(n, ", ".join("{} {}".format(k, v) for k, v in sorted(cnt.items()))))
    lines.append("")
    lines += ["## Acceptance criteria", "",
              "Ready only if OUT-OF-SAMPLE at 1.5x costs: >= 100 trades, PF >= 1.25, max DD <= 6%, "
              "worst day <= 2.5%, Monte Carlo firm-breach probability < 15%.", ""]
    for n, v in verdicts.items():
        lines.append("- {}: **{}**".format(n, v))
    out = os.path.join(REPORTS, a.out)
    with open(out, "w") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))
    print("\nwrote", out)


if __name__ == "__main__":
    main()
