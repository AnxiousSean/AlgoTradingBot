"""SCALP (many small trades) research run. Same data, costs, 70/30 split,
Monte Carlo and acceptance rules as run_research.py.

    python run_scalp.py --procs 4
"""
import argparse
import datetime as dt
import os
import statistics
import time

import run_research as rr

BASE = {"STRATEGY": "SCALP"}
GRID = [("SCALP_FAST_EMA", 9, None, None), ("SCALP_SLOW_EMA", 50, None, None),
        ("SCALP_STOP_ATR", 0.5, None, None), ("SCALP_TARGET_R", 1.0, None, None),
        ("SCALP_MAX_HOLD_MIN", 15, None, None)]


def build_jobs():
    c1, c15 = rr.BASE_COST, rr.BASE_COST * 1.5
    jobs = [("SCALP 1m NO COSTS", 1, dict(BASE), 0.0)]
    for c, tag in ((c1, "1.0x"), (c15, "1.5x")):
        jobs += [("SCALP 1m " + tag, 1, dict(BASE), c),
                 ("SCALP 1m target 0.5R " + tag, 1, dict(BASE, SCALP_TARGET_R=0.5), c),
                 ("SCALP 1m target 2R " + tag, 1, dict(BASE, SCALP_TARGET_R=2.0), c),
                 ("SCALP 3m " + tag, 3, dict(BASE), c)]
    for sd in (1, 2, 3):
        jobs.append(("SCALP RANDOM seed{} 1.0x".format(sd), 1,
                     dict(BASE, RANDOM_DIRECTION=True, RANDOM_SEED=sd), c1))
    for label, s in rr.grid_variants(BASE, GRID):
        jobs.append(("GRID " + label, 1, s, c1))
    return jobs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--procs", type=int, default=4)
    ap.add_argument("--mc-runs", type=int, default=10000)
    ap.add_argument("--out", default="scalp_report.md")
    a = ap.parse_args()
    one = rr.bars_for(1)
    cut_utc = rr.split_date(one)
    import tl_prop_bot as tb
    cut_ny = tb.utc_to_ny(cut_utc.to_pydatetime())
    oos_days = sorted(set(tb.trading_day_of(tb.utc_to_ny(t.to_pydatetime()))
                          for t in one.index[one.index >= cut_utc][::60]))
    oos_days = [d for d in oos_days if d.weekday() < 5]
    jobs = build_jobs()
    t0 = time.time()
    res = {r["name"]: r for r in rr.run_many(jobs, a.procs)}
    elapsed = time.time() - t0

    L = ["# SCALP research report (many small trades)", ""]
    L.append("Generated {} from {} 1-minute bars, {} to {} UTC. In-sample before {:%Y-%m-%d} NY, "
             "out-of-sample after. {} backtests in {:.0f} s.".format(
                 dt.datetime.now().strftime("%Y-%m-%d %H:%M"), len(one), one.index[0], one.index[-1],
                 cut_ny, len(jobs), elapsed))
    L.append("")
    L.append("Strategy: 1-minute trend pullback. Long when EMA9 > EMA50 and a bar dips to EMA9 and closes "
             "above it as an up-bar (short = mirror). Stop beyond that bar by 0.5 x ATR(14) (at least 0.03% "
             "of price), target 1R placed after the 2-minute minimum hold, exit after 15 minutes, "
             "5-minute pause between trades, max 10 trades a day, 0.25% ($12.50) risk per trade, "
             "entries 09:45-15:00 NY. Costs: 2.5 points round trip at NAS100 30,000 (scaled with price); "
             "1.5x = 3.75 points.")
    L.append("")
    names = [j[0] for j in jobs if not j[0].startswith("GRID")]
    for period, lo, hi in (("Out-of-sample", cut_ny, None), ("In-sample", None, cut_ny)):
        rows = [(n, rr.metrics(rr.subset(res[n]["trades"], lo, hi))) for n in names]
        L += ["## " + period, "", rr.table(rows), ""]
    L += ["## Monte Carlo (out-of-sample, 1.5x costs, {} runs, Step 1 target 8%)".format(a.mc_runs), "",
          "| Config | Pass % | Firm breach % | Bot -7% stop % | Unfinished % | Median days to pass | Verdict |",
          "|---|---:|---:|---:|---:|---:|---|"]
    verdicts = {}
    for n in names:
        if not n.endswith("1.5x"):
            continue
        tr = rr.subset(res[n]["trades"], cut_ny, None)
        mc = rr.monte_carlo(tr, oos_days, runs=a.mc_runs)
        v = rr.verdict(rr.metrics(tr), mc)
        verdicts[n] = v
        L.append("| {} | {} | {} | {} | {} | {} | {} |".format(
            n, rr.fmt(mc["PASS"], 1), rr.fmt(mc["BREACH"], 1), rr.fmt(mc["STOPPED"], 1),
            rr.fmt(mc["UNFINISHED"], 1), rr.fmt(mc["median_days"], 0), v))
    L.append("")
    L += ["## Real signal vs random direction (1x costs)", ""]
    for period, lo, hi in (("Out-of-sample", cut_ny, None), ("In-sample", None, cut_ny)):
        real = rr.metrics(rr.subset(res["SCALP 1m 1.0x"]["trades"], lo, hi))
        exps = [rr.metrics(rr.subset(res["SCALP RANDOM seed{} 1.0x".format(s)]["trades"], lo, hi))["expectancy_r"]
                for s in (1, 2, 3)]
        L.append("- {}: real {:+.3f} R over {} trades; random {} (mean {:+.3f}); real beats {} of 3.".format(
            period, real["expectancy_r"], real["trades"], ", ".join("{:+.3f}".format(e) for e in exps),
            statistics.mean(exps), len([e for e in exps if real["expectancy_r"] > e])))
    L.append("")
    rows = [("BASE (defaults)", rr.metrics(rr.subset(res["SCALP 1m 1.0x"]["trades"], None, cut_ny)))]
    for j in jobs:
        if j[0].startswith("GRID"):
            rows.append((j[0][5:], rr.metrics(rr.subset(res[j[0]]["trades"], None, cut_ny))))
    L += ["## Robustness: parameters +-20% (IN-SAMPLE, 1x costs)", "", rr.table(rows), ""]
    L += ["## Exit reasons and cost share (full period)", ""]
    for n in ("SCALP 1m NO COSTS", "SCALP 1m 1.0x", "SCALP 3m 1.0x"):
        tr = res[n]["trades"]
        cnt = {}
        for t in tr:
            cnt[t["reason"]] = cnt.get(t["reason"], 0) + 1
        held = statistics.median([t["held_min"] for t in tr if t["held_min"] is not None]) if tr else 0
        L.append("- **{}**: {} trades; {}; median hold {:.0f} min; {} adjusted for stop-in-fill-bar".format(
            n, len(tr), ", ".join("{} {}".format(k, v) for k, v in sorted(cnt.items())), held, res[n]["adjusted"]))
    L.append("")
    L += ["## Acceptance (OOS, 1.5x costs: >=100 trades, PF >= 1.25, max DD <= 6%, worst day <= 2.5%, "
          "MC breach < 15%)", ""]
    for n, v in verdicts.items():
        L.append("- {}: **{}**".format(n, v))
    out = os.path.join(rr.REPORTS, a.out)
    with open(out, "w") as f:
        f.write("\n".join(L) + "\n")
    print("wrote", out)


if __name__ == "__main__":
    main()
