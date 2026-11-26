# -*- coding: utf-8 -*-
"""
probe_bot.py -- TradeLocker Studio platform discovery probe (Phase 0).

PURPOSE: find out how TradeLocker Studio's Backtrader build behaves.
It makes no attempt to trade profitably.

!!! BACKTEST ONLY. NEVER press "Launch" with this file. !!!
It deliberately places odd orders (including size=1000) to see how the
platform reacts. If it detects a live data feed it refuses to trade.

Every log line starts with "PROBE|" so you can copy/filter them.
A compact SUMMARY block is printed again at the very end of the run.
"""
import backtrader as bt
import math
import datetime

# ----------------------------------------------------------------- CONFIG ---
RUN_ORDER_TESTS = True     # set False to only probe data/broker/indicators
RUN_IMPORT_TESTS = True    # set False if Studio rejects the script
MAX_DAILY_LINES = 25       # daily broker-value lines to print
BARS_BETWEEN_TESTS = 3     # gap between order tests
# ----------------------------------------------------------------------------


def _fmt(x, nd=6):
    try:
        if x is None:
            return "None"
        if isinstance(x, float):
            if math.isnan(x):
                return "nan"
            return ("%." + str(nd) + "f") % x
        return str(x)
    except Exception:
        return repr(x)


def _import_tests():
    """Which modules can a Studio bot import? (each in its own try)."""
    res = []
    try:
        import sys
        res.append("sys=OK(py " + sys.version.split()[0] + ")")
    except Exception as e:
        res.append("sys=FAIL(" + type(e).__name__ + ")")
    try:
        import collections
        res.append("collections=OK")
    except Exception as e:
        res.append("collections=FAIL(" + type(e).__name__ + ")")
    try:
        import json
        res.append("json=OK")
    except Exception as e:
        res.append("json=FAIL(" + type(e).__name__ + ")")
    try:
        import statistics
        res.append("statistics=OK")
    except Exception as e:
        res.append("statistics=FAIL(" + type(e).__name__ + ")")
    try:
        import time
        res.append("time=OK")
    except Exception as e:
        res.append("time=FAIL(" + type(e).__name__ + ")")
    try:
        import zoneinfo
        zoneinfo.ZoneInfo("America/New_York")
        res.append("zoneinfo=OK(NY tz loads)")
    except Exception as e:
        res.append("zoneinfo=FAIL(" + type(e).__name__ + ")")
    try:
        import numpy
        res.append("numpy=OK(" + numpy.__version__ + ")")
    except Exception as e:
        res.append("numpy=FAIL(" + type(e).__name__ + ")")
    try:
        import pandas
        res.append("pandas=OK(" + pandas.__version__ + ")")
    except Exception as e:
        res.append("pandas=FAIL(" + type(e).__name__ + ")")
    return res


class ProbeStrategy(bt.Strategy):
    params = dict(dummy=0)

    # ------------------------------------------------------------ logging --
    def P(self, tag, msg):
        line = "PROBE|" + tag + "|" + msg
        print(line, flush=True)
        return line

    def S(self, key, val):
        """record a summary fact (printed again at the end)"""
        self.summary[key] = val
        self.P("FACT", key + " = " + str(val))

    def now(self):
        try:
            return self.data.datetime.datetime(0)
        except Exception:
            return None

    # --------------------------------------------------------------- init --
    def __init__(self):
        self.summary = {}
        self.bar = 0
        self.prev_dt = None
        self.diffs = {}            # bar spacing (minutes) histogram
        self.hour_rng = {}         # hour -> [sum range/close, count]
        self.week_opens = []       # first bar after a >24h gap
        self.week_closes = []      # last bar before a >24h gap
        self.daily_lines = 0
        self.last_date = None
        self.fund_calls = 0
        self.order_log = {}        # ref -> short description
        self.last_exec_price = None
        self.test_size = None
        self.steps = []
        self.step_i = -1
        self.step_start_bar = 0
        self.step_orders = []
        self.step_state = {}
        self.trading_blocked = False
        self.step_active = False
        self.pause_until = 0
        self.ind = {}
        self.ind_err = {}
        self.ind_printed = False

        self.P("START", "probe __init__ reached")
        try:
            self.S("backtrader_version", getattr(bt, "__version__", "unknown"))
        except Exception as e:
            self.S("backtrader_version", "ERR " + repr(e))

        # ---- indicators: which ones exist / construct? ----
        d = self.data
        tests = [
            ("SMA20", lambda: bt.indicators.SMA(d.close, period=20)),
            ("EMA20", lambda: bt.indicators.EMA(d.close, period=20)),
            ("EMA50", lambda: bt.indicators.EMA(d.close, period=50)),
            ("EMA200", lambda: bt.indicators.EMA(d.close, period=200)),
            ("ATR14", lambda: bt.indicators.ATR(d, period=14)),
            ("ADX14", lambda: bt.indicators.ADX(d, period=14)),
            ("DMI14", lambda: bt.indicators.DirectionalMovement(d, period=14)),
            ("BB20_2.2", lambda: bt.indicators.BollingerBands(d.close, period=20, devfactor=2.2)),
            ("Highest20", lambda: bt.indicators.Highest(d.high, period=20)),
            ("Lowest20", lambda: bt.indicators.Lowest(d.low, period=20)),
            ("Highest55", lambda: bt.indicators.Highest(d.high, period=55)),
            ("RSI14", lambda: bt.indicators.RSI(d.close, period=14)),
            ("MACD", lambda: bt.indicators.MACD(d.close)),
            ("MACDHisto", lambda: bt.indicators.MACDHisto(d.close)),
            ("CrossOver", lambda: bt.indicators.CrossOver(d.close, bt.indicators.SMA(d.close, period=10))),
            ("Stochastic", lambda: bt.indicators.Stochastic(d)),
        ]
        ok, bad = [], []
        for name, fn in tests:
            try:
                self.ind[name] = fn()
                ok.append(name)
            except Exception as e:
                self.ind_err[name] = type(e).__name__ + ": " + str(e)[:80]
                bad.append(name)
        self.S("indicators_constructed", ",".join(ok) if ok else "NONE")
        self.S("indicators_failed", ",".join(bad) if bad else "none")
        for k, v in self.ind_err.items():
            self.P("IND_ERR", k + " -> " + v)
        # line names (e.g. does MACD have .histo?)
        for name in ("MACD", "MACDHisto", "BB20_2.2", "ADX14", "DMI14"):
            if name in self.ind:
                try:
                    self.P("IND_LINES", name + " lines=" + ",".join(self.ind[name].lines.getlinealiases()))
                except Exception as e:
                    self.P("IND_LINES", name + " ERR " + repr(e)[:80])

        # ---- environment: feeds, cerebro, broker ----
        try:
            self.S("num_datas", len(self.datas))
            for i, dd in enumerate(self.datas):
                tf = getattr(dd, "_timeframe", None)
                try:
                    tfname = bt.TimeFrame.getname(tf, getattr(dd, "_compression", 1))
                except Exception:
                    tfname = str(tf)
                self.P("DATA", "#%d name=%s class=%s timeframe=%s compression=%s" % (
                    i, getattr(dd, "_name", "?"), type(dd).__name__, tfname,
                    getattr(dd, "_compression", "?")))
                try:
                    pnames = dd.params._getkeys()
                    pv = []
                    for pn in pnames:
                        if pn in ("dataname",):
                            continue
                        try:
                            pv.append(pn + "=" + str(getattr(dd.params, pn))[:40])
                        except Exception:
                            pass
                    self.P("DATA_PARAMS", "#%d %s" % (i, "; ".join(pv)))
                except Exception as e:
                    self.P("DATA_PARAMS", "#%d ERR %r" % (i, e))
        except Exception as e:
            self.P("ERR", "datas: " + repr(e))

        try:
            env = self.env
            self.S("cerebro_class", type(env).__name__)
            self.S("cerebro_has_resampledata", hasattr(env, "resampledata"))
            self.S("cerebro_has_adddata", hasattr(env, "adddata"))
        except Exception as e:
            self.P("ERR", "env: " + repr(e))
        self.S("strategy_has_add_timer", hasattr(self, "add_timer"))

        try:
            b = self.broker
            self.S("broker_class", type(b).__module__ + "." + type(b).__name__)
            pub = [m for m in dir(b) if not m.startswith("_")]
            self.P("BROKER_DIR", ",".join(pub))
            has = []
            for attr in ("startingcash", "get_orders_open", "getcommissioninfo", "get_value",
                         "getvalue", "getcash", "getposition", "positions", "set_coc", "set_slippage_perc"):
                has.append("%s=%s" % (attr, "Y" if hasattr(b, attr) else "N"))
            self.P("BROKER_HAS", " ".join(has))
            try:
                bp = b.params._getkeys()
                self.P("BROKER_PARAMS", "; ".join(k + "=" + str(getattr(b.params, k))[:40] for k in bp))
            except Exception as e:
                self.P("BROKER_PARAMS", "ERR " + repr(e))
        except Exception as e:
            self.P("ERR", "broker: " + repr(e))

        try:
            ci = self.broker.getcommissioninfo(self.data)
            vals = []
            for k in ("commission", "mult", "margin", "leverage", "stocklike", "commtype",
                      "percabs", "interest", "automargin"):
                vals.append(k + "=" + _fmt(getattr(ci.p, k, "NA")))
            self.S("comminfo_class", type(ci).__name__)
            self.S("comminfo_params", "; ".join(vals))
        except Exception as e:
            self.S("comminfo_params", "ERR " + repr(e))

        try:
            sz = self.getsizer()
            sp = []
            try:
                for k in sz.params._getkeys():
                    sp.append(k + "=" + str(getattr(sz.params, k)))
            except Exception:
                pass
            self.S("default_sizer", type(sz).__name__ + "(" + ",".join(sp) + ")")
        except Exception as e:
            self.S("default_sizer", "ERR " + repr(e))

        try:
            sdir = [m for m in dir(self) if not m.startswith("_")]
            std = set(dir(bt.Strategy))
            extra = [m for m in sdir if m not in std and m not in self.__dict__
                     and m not in ProbeStrategy.__dict__]
            self.P("STRATEGY_EXTRA_ATTRS", ",".join(extra) if extra else "none")
        except Exception as e:
            self.P("ERR", "strategy dir: " + repr(e))

        if RUN_IMPORT_TESTS:
            try:
                self.S("imports", " ".join(_import_tests()))
            except Exception as e:
                self.S("imports", "ERR " + repr(e))

        self._build_steps()

    # --------------------------------------------------------- callbacks --
    def prenext(self):
        if self.bar == 0:
            self.P("PRENEXT", "prenext called (indicators warming up)")
        self._observe()

    def nextstart(self):
        self.P("NEXTSTART", "first next() at bar %d dt=%s" % (self.bar, self.now()))
        self.next()

    def notify_fund(self, cash, value, fundvalue, shares):
        if self.fund_calls < 2:
            self.P("FUND", "cash=%s value=%s fundvalue=%s shares=%s" % (
                _fmt(cash, 2), _fmt(value, 2), _fmt(fundvalue, 4), _fmt(shares, 4)))
        self.fund_calls += 1

    def notify_order(self, order):
        try:
            st = order.getstatusname()
            kind = order.ordtypename()
            ex = bt.Order.ExecTypes[order.exectype] if order.exectype is not None else "?"
            desc = self.order_log.get(order.ref, "")
            if order.status == order.Submitted:
                return
            if order.status == order.Accepted and order.exectype == bt.Order.Market:
                return
            msg = "ref=%d %s %s %s req_size=%s req_price=%s status=%s" % (
                order.ref, desc, kind, ex, _fmt(order.created.size, 4),
                _fmt(order.created.price, 5), st)
            if order.status == order.Completed or order.status == order.Partial:
                e = order.executed
                msg += " | exec_size=%s exec_price=%s exec_value=%s exec_comm=%s exec_margin=%s" % (
                    _fmt(e.size, 4), _fmt(e.price, 5), _fmt(e.value, 4), _fmt(e.comm, 4),
                    _fmt(getattr(e, "margin", None), 4))
                self.last_exec_price = e.price
            msg += " | pos_after=%s value=%s cash=%s" % (
                _fmt(self.position.size, 4), _fmt(self.broker.getvalue(), 2),
                _fmt(self.broker.getcash(), 2))
            self.P("ORDER", "%s %s" % (self.now(), msg))
            if order.status in (order.Margin, order.Rejected):
                self.P("ORDER_INFO", "ref=%d info=%s" % (order.ref, str(getattr(order, "info", ""))[:120]))
        except Exception as e:
            self.P("ERR", "notify_order: " + repr(e))

    def notify_trade(self, trade):
        try:
            if trade.isclosed:
                msg = "CLOSED entry=%s exit=%s pnl=%s pnlcomm=%s barlen=%s" % (
                    _fmt(trade.price, 5), _fmt(self.last_exec_price, 5),
                    _fmt(trade.pnl, 4), _fmt(trade.pnlcomm, 4), trade.barlen)
                st = self.step_state
                if st.get("open_size") and self.last_exec_price is not None:
                    dp = (self.last_exec_price - trade.price) * st["open_size"]
                    if dp != 0:
                        mult = trade.pnl / dp
                        msg += " implied_multiplier=%s" % _fmt(mult, 2)
                        self.summary.setdefault("implied_multiplier_list", []).append(round(mult, 2))
                self.P("TRADE", "%s %s" % (self.now(), msg))
            elif trade.justopened:
                self.P("TRADE", "%s OPENED size=%s price=%s" % (
                    self.now(), _fmt(trade.size, 4), _fmt(trade.price, 5)))
        except Exception as e:
            self.P("ERR", "notify_trade: " + repr(e))

    # ------------------------------------------------------ observations --
    def _observe(self):
        """data timing / timezone / broker value - runs every bar"""
        self.bar += 1
        dt = self.now()
        if dt is None:
            return
        if self.bar <= 3:
            self.P("BAR", "#%d dt=%s tzinfo=%s O=%s H=%s L=%s C=%s V=%s" % (
                self.bar, dt, dt.tzinfo, _fmt(self.data.open[0], 5), _fmt(self.data.high[0], 5),
                _fmt(self.data.low[0], 5), _fmt(self.data.close[0], 5), _fmt(self.data.volume[0], 1)))
        if self.prev_dt is not None:
            mins = int(round((dt - self.prev_dt).total_seconds() / 60.0))
            self.diffs[mins] = self.diffs.get(mins, 0) + 1
            if mins > 24 * 60:
                if len(self.week_opens) < 6:
                    self.P("GAP", "gap of %.1f h: last bar before=%s (%s)  first bar after=%s (%s)" % (
                        mins / 60.0, self.prev_dt, self.prev_dt.strftime("%a"), dt, dt.strftime("%a")))
                self.week_opens.append(dt)
                self.week_closes.append(self.prev_dt)
        self.prev_dt = dt
        try:
            c = self.data.close[0]
            if c > 0:
                h = dt.hour
                r = (self.data.high[0] - self.data.low[0]) / c
                a = self.hour_rng.setdefault(h, [0.0, 0])
                a[0] += r
                a[1] += 1
        except Exception:
            pass

        # daily broker snapshot
        d = dt.date()
        if d != self.last_date:
            self.last_date = d
            if self.daily_lines < MAX_DAILY_LINES:
                self.daily_lines += 1
                self.P("DAY", self._acct_line())

    def _acct_line(self):
        try:
            v = self.broker.getvalue()
            c = self.broker.getcash()
            ps = self.position.size
            pp = self.position.price
            mult = self._mult()
            opnl = ps * (self.data.close[0] - pp) * mult if ps else 0.0
            return "%s %s value=%s cash=%s value-cash=%s pos=%s pos_price=%s manual_open_pnl(mult=%s)=%s" % (
                self.now(), self.now().strftime("%a"), _fmt(v, 2), _fmt(c, 2), _fmt(v - c, 2),
                _fmt(ps, 4), _fmt(pp, 5), _fmt(mult, 0), _fmt(opnl, 2))
        except Exception as e:
            return "ERR " + repr(e)

    def _mult(self):
        try:
            return float(self.broker.getcommissioninfo(self.data).p.mult)
        except Exception:
            return 1.0

    def next(self):
        self._observe()
        if self.bar == 260 and not self.ind_printed:
            self._print_indicator_values()
        if RUN_ORDER_TESTS:
            try:
                self._run_steps()
            except Exception as e:
                self.P("ERR", "step runner: " + repr(e))

    def _print_indicator_values(self):
        self.ind_printed = True
        for name, ind in self.ind.items():
            try:
                vals = []
                for ln in ind.lines.getlinealiases():
                    vals.append(ln + "=" + _fmt(getattr(ind.lines, ln)[0], 5))
                self.P("IND_VAL", "%s %s %s" % (self.now(), name, " ".join(vals)))
            except Exception as e:
                self.P("IND_VAL", name + " ERR " + repr(e)[:80])

    # ------------------------------------------------------- order tests --
    def _ord(self, o, desc):
        if o is None:
            self.P("ORDER", "%s %s -> returned None" % (self.now(), desc))
            return None
        try:
            self.order_log[o.ref] = desc
        except Exception:
            pass
        self.step_orders.append(o)
        return o

    def _px(self):
        return float(self.data.close[0])

    def _build_steps(self):
        # (name, start_fn, bars_to_run)
        self.steps = [
            ("size_0.01_market_buy", self.t_size_small, 6),
            ("size_1000_market_buy", self.t_size_big, 6),
            ("netting_sell_then_buy", self.t_netting, 6),
            ("stop_entry", self.t_stop_entry, 12),
            ("limit_entry", self.t_limit_entry, 12),
            ("cancel_order", self.t_cancel, 4),
            ("buy_bracket", self.t_buy_bracket, 150),
            ("sell_bracket", self.t_sell_bracket, 150),
            ("stoptrail_exit", self.t_stoptrail, 150),
            ("manual_stop_then_close", self.t_manual_stop_close, 8),
        ]

    def _live(self):
        try:
            for dd in self.datas:
                if dd.islive():
                    return True
        except Exception:
            pass
        return False

    def _run_steps(self):
        if self.trading_blocked:
            return
        if self._live():
            self.trading_blocked = True
            self.S("LIVE_FEED_DETECTED", "order tests DISABLED - this probe is backtest-only")
            return
        if self.bar < 30 or self.step_i >= len(self.steps):
            return
        if not self.step_active:
            if self.bar >= self.pause_until:
                if self.step_i < 0:
                    self.step_i = 0
                self._start_step()
            return
        name, fn, nbars = self.steps[self.step_i]
        st = self.step_state
        age = self.bar - self.step_start_bar
        hook = st.get("hook")
        if hook is not None:
            try:
                hook(age)
            except Exception as e:
                self.P("ERR", name + " hook: " + repr(e))
        if 0 < age < 5 and st.get("watch_value"):
            self.P("HOLD", name + " age=%d " % age + self._acct_line())
            if self.position.size:
                try:
                    v, c = self.broker.getvalue(), float(self.data.close[0])
                    if "pv" in st and c != st["pc"]:
                        ratio = (v - st["pv"]) / (self.position.size * (c - st["pc"]))
                        self.P("EQUITY_CHECK", "d(value)/d(size*price)=%s  (~multiplier => getvalue() is "
                               "EQUITY incl. open P&L; ~0 => balance only)" % _fmt(ratio, 1))
                        self.summary.setdefault("equity_check_ratios", []).append(round(ratio, 1))
                    st["pv"], st["pc"] = v, c
                except Exception as e:
                    self.P("ERR", "equity check " + repr(e))
        if age >= nbars or st.get("done"):
            self._finish_step()

    def _start_step(self):
        name, fn, nbars = self.steps[self.step_i]
        self.step_active = True
        self.step_start_bar = self.bar
        self.step_orders = []
        self.step_state = {"start_value": self.broker.getvalue()}
        self.P("STEP", "=== %s start %s price=%s pos=%s" % (name, self.now(), _fmt(self._px(), 5),
                                                           _fmt(self.position.size, 4)))
        try:
            fn()
        except Exception as e:
            self.P("STEP_ERR", name + " start raised " + type(e).__name__ + ": " + str(e)[:120])
            self.summary["step_" + name] = "EXCEPTION " + type(e).__name__ + ": " + str(e)[:80]

    def _finish_step(self):
        name = self.steps[self.step_i][0]
        res = []
        for o in self.step_orders:
            try:
                res.append("%s:%s" % (self.order_log.get(o.ref, o.ref), o.getstatusname()))
            except Exception:
                pass
        alive = [o for o in self.step_orders if o.alive()]
        for o in alive:
            try:
                self.cancel(o)
            except Exception as e:
                self.P("ERR", "cancel at finish: " + repr(e))
        flat_needed = self.position.size != 0
        if flat_needed:
            try:
                self.close()
            except Exception as e:
                self.P("ERR", "close at finish: " + repr(e))
        key = "step_" + name
        if key not in self.summary:
            self.summary[key] = " ".join(res) + (" | probe_had_to_close_pos" if flat_needed else "") + (
                " | probe_cancelled_alive=%d" % len(alive) if alive else "")
        self.P("STEP", "=== %s end: %s" % (name, self.summary[key]))
        self.step_active = False
        self.step_i += 1
        self.pause_until = self.bar + BARS_BETWEEN_TESTS
        if self.step_i >= len(self.steps):
            self.S("order_tests", "all steps finished at %s" % self.now())

    # individual tests ---------------------------------------------------
    def _choose_test_size(self):
        """after the two size tests: pick a small safe size for the rest"""
        if self.test_size is not None:
            return self.test_size
        small = self.summary.get("step_size_0.01_market_buy", "")
        big = self.summary.get("step_size_1000_market_buy", "")
        if "Completed" in small and "Completed" not in big:
            self.test_size = 0.01
        elif "Completed" in big and "Completed" not in small:
            self.test_size = 1000
        else:
            m = self._mult()
            self.test_size = 0.01 if m >= 1000 else 1000
        self.S("test_size_used_for_later_steps", self.test_size)
        return self.test_size

    def t_size_small(self):
        self.step_state["open_size"] = 0.01
        self.step_state["watch_value"] = True
        self._ord(self.buy(size=0.01), "BUY_MKT_0.01")
        self.step_state["hook"] = self._close_at(4)

    def t_size_big(self):
        self.step_state["open_size"] = 1000
        self.step_state["watch_value"] = True
        self._ord(self.buy(size=1000), "BUY_MKT_1000")
        self.step_state["hook"] = self._close_at(4)

    def _close_at(self, n):
        def hook(age):
            if age == n and self.position.size != 0:
                self.P("STEP", "closing with self.close() pos=%s" % _fmt(self.position.size, 4))
                self._ord(self.close(), "CLOSE()")
        return hook

    def t_netting(self):
        sz = self._choose_test_size()
        self.step_state["open_size"] = -sz
        self._ord(self.sell(size=sz), "SELL_MKT")

        def hook(age):
            if age == 2:
                self.P("NETTING", "pos before opposite buy=%s" % _fmt(self.position.size, 4))
                self._ord(self.buy(size=sz), "OPPOSITE_BUY")
            if age == 4:
                self.S("netting_result", "position after sell %s then buy %s = %s (0 means netting)" % (
                    sz, sz, _fmt(self.position.size, 4)))
        self.step_state["hook"] = hook

    def t_stop_entry(self):
        sz = self._choose_test_size()
        p = self._px()
        self.step_state["open_size"] = sz
        self._ord(self.buy(size=sz, exectype=bt.Order.Stop, price=p * 1.0005, valid=None), "BUY_STOP+5bp")
        self.step_state["hook"] = self._close_at(10)

    def t_limit_entry(self):
        sz = self._choose_test_size()
        p = self._px()
        self.step_state["open_size"] = sz
        self._ord(self.buy(size=sz, exectype=bt.Order.Limit, price=p * 0.9997), "BUY_LIMIT-3bp")
        self.step_state["hook"] = self._close_at(10)

    def t_cancel(self):
        sz = self._choose_test_size()
        p = self._px()
        o = self._ord(self.buy(size=sz, exectype=bt.Order.Limit, price=p * 0.95), "FAR_LIMIT")

        def hook(age):
            if age == 1 and o is not None:
                self.P("STEP", "calling self.cancel(ref=%d)" % o.ref)
                self.cancel(o)
            if age == 3 and o is not None:
                self.S("cancel_result", o.getstatusname())
        self.step_state["hook"] = hook

    def _bracket(self, side):
        sz = self._choose_test_size()
        p = self._px()
        self.step_state["open_size"] = sz if side == "buy" else -sz
        if side == "buy":
            os_ = self.buy_bracket(size=sz, exectype=bt.Order.Market,
                                   stopprice=p * 0.998, limitprice=p * 1.002)
        else:
            os_ = self.sell_bracket(size=sz, exectype=bt.Order.Market,
                                    stopprice=p * 1.002, limitprice=p * 0.998)
        if os_ is None:
            self.S("step_" + side + "_bracket", "returned None")
            return
        names = ["MAIN", "STOP", "TP"]
        try:
            for i, o in enumerate(os_):
                self._ord(o, side.upper() + "_BRACKET_" + names[i])
            self.P("BRACKET", "%s returned %d orders" % (side, len(os_)))
        except Exception as e:
            self.P("ERR", "bracket iterate: " + repr(e))

        def hook(age):
            if self.step_orders and all(not o.alive() for o in self.step_orders) and age > 1:
                self.P("BRACKET", "%s all legs resolved at age %d, pos=%s" % (
                    side, age, _fmt(self.position.size, 4)))
                self.step_state["done"] = True
        self.step_state["hook"] = hook

    def t_buy_bracket(self):
        self._bracket("buy")

    def t_sell_bracket(self):
        self._bracket("sell")

    def t_stoptrail(self):
        sz = self._choose_test_size()
        self.step_state["open_size"] = sz
        self._ord(self.buy(size=sz), "BUY_MKT")

        def hook(age):
            if age == 1 and self.position.size > 0:
                self._ord(self.sell(size=sz, exectype=bt.Order.StopTrail, trailpercent=0.002),
                          "SELL_STOPTRAIL_0.2%")
            if age > 2 and self.position.size == 0:
                self.step_state["done"] = True
        self.step_state["hook"] = hook

    def t_manual_stop_close(self):
        """fallback plan if brackets fail: market entry + separate stop order.
        Checks that close() does NOT auto-cancel the pending stop (orphan risk)."""
        sz = self._choose_test_size()
        self.step_state["open_size"] = sz
        self._ord(self.buy(size=sz), "BUY_MKT")
        st = {}

        def hook(age):
            if age == 1 and self.position.size > 0:
                st["stop"] = self._ord(self.sell(size=sz, exectype=bt.Order.Stop,
                                                 price=self._px() * 0.99), "SELL_STOP_-1%")
            if age == 2:
                self._ord(self.close(), "CLOSE()")
            if age == 4 and "stop" in st:
                self.S("orphan_stop_after_close", "stop status after close() = %s (Accepted/Submitted = still alive, must cancel manually)"
                       % st["stop"].getstatusname())
                try:
                    oo = self.broker.get_orders_open()
                    self.S("get_orders_open_works", "yes, %d open" % len(oo))
                except Exception as e:
                    self.S("get_orders_open_works", "no: " + repr(e)[:60])
                self.cancel(st["stop"])
        self.step_state["hook"] = hook

    # --------------------------------------------------------------- stop --
    def stop(self):
        try:
            self._summary()
        except Exception as e:
            print("PROBE|ERR|summary " + repr(e), flush=True)

    def _summary(self):
        P = self.P
        if not self.ind_printed:
            self._print_indicator_values()
        P("SUMMARY", "================ PROBE SUMMARY ================")
        P("SUMMARY", "bars=%d first=%s last=%s" % (self.bar, self._first_dt(), self.now()))
        if self.diffs:
            top = sorted(self.diffs.items(), key=lambda kv: -kv[1])[:5]
            P("SUMMARY", "bar_spacing_minutes(top5)=" + ", ".join("%dm:%d" % kv for kv in top))
            P("SUMMARY", "bar_resolution_guess=%d minutes" % top[0][0])
        if self.week_opens:
            wo = {}
            for d in self.week_opens:
                k = d.strftime("%a %H:%M")
                wo[k] = wo.get(k, 0) + 1
            wc = {}
            for d in self.week_closes:
                k = d.strftime("%a %H:%M")
                wc[k] = wc.get(k, 0) + 1
            P("SUMMARY", "week_open_bar_times=" + ", ".join("%s x%d" % kv for kv in sorted(wo.items())))
            P("SUMMARY", "week_close_bar_times=" + ", ".join("%s x%d" % kv for kv in sorted(wc.items())))
            P("SUMMARY", "HINT: FX opens Sun 17:00 New York = Sun 21:00/22:00 UTC; server time GMT+2/+3 = Mon 00:00")
        if self.hour_rng:
            prof = []
            for h in range(24):
                if h in self.hour_rng and self.hour_rng[h][1] > 0:
                    prof.append("%02d:%.0f" % (h, 1e5 * self.hour_rng[h][0] / self.hour_rng[h][1]))
            P("SUMMARY", "avg_bar_range_by_hour(x1e-5 of price)=" + " ".join(prof))
            P("SUMMARY", "HINT: in UTC the busiest hours are ~12-16 (London/NY overlap) and quietest ~21-23")
        P("SUMMARY", "HINT: equity_check_ratios ~= multiplier -> getvalue() is equity; ~0 -> balance only; "
                     "~2x multiplier -> double-count bug (backtrader leverage= quirk)")
        for k in sorted(self.summary.keys()):
            P("SUMMARY", "%s = %s" % (k, self.summary[k]))
        P("SUMMARY", "final value=%s cash=%s" % (_fmt(self.broker.getvalue(), 2), _fmt(self.broker.getcash(), 2)))
        P("SUMMARY", "================ END SUMMARY ==================")

    def _first_dt(self):
        try:
            return bt.num2date(self.data.datetime.array[0])
        except Exception:
            return "?"
