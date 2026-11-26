import backtrader as bt

# STAGE 0 PROBE - TradeLocker Studio capability test
# ---------------------------------------------------
# Finds out which Backtrader features TradeLocker Studio supports.
# Run it in the BACKTESTER ONLY (it places small test orders):
#   instrument = your Nasdaq 100 CFD, timeframe = 15 minutes,
#   date range = about the last 2 months (needs more than 900 bars).
# Then copy every line that starts with "PROBE|" and send it back.
# If 0.01 lots is rejected, set PROBE_SIZE to your minimum lot.

PROBE_SIZE = 0.01          # order size for the test orders (use your min lot)
PROBE_START_BAR = 30       # first bar at which order tests begin


def plog(*parts):
    # Every output line starts with PROBE| so it is easy to find.
    try:
        print("PROBE|" + " ".join(str(x) for x in parts))
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Helper functions live OUTSIDE the strategy class: TradeLocker Studio appears
# to drop custom methods from strategy classes and keep only the standard
# backtrader hooks (__init__, next, prenext, notify_order, notify_trade, stop).
# Each helper takes the strategy object as its first argument "st".
# ---------------------------------------------------------------------------
class PlainHelper(object):
    # Diagnostic: tests whether module-level classes with methods work.
    def __init__(self, x):
        self.x = x

    def doubled(self):
        return self.x * 2


def make_indicator(st, name):
    # NOTE: plain RSI(period=2) crashes with ZeroDivisionError on runs of
    # same-direction bars, so only the safe-division versions are run.
    c = st.data.close
    if name == "EMA200":
        return bt.indicators.EMA(c, period=200)
    if name == "EMA800":
        return bt.indicators.EMA(c, period=800)
    if name == "EMA5":
        return bt.indicators.EMA(c, period=5)
    if name == "RSI2_safediv":
        return bt.indicators.RSI(c, period=2, safediv=True)
    if name == "RSI2_Safe":
        return bt.indicators.RSI_Safe(c, period=2)
    if name == "ATR14":
        return bt.indicators.ATR(st.data, period=14)
    if name == "SMA20":
        return bt.indicators.SMA(c, period=20)
    if name == "Highest20":
        return bt.indicators.Highest(st.data.high, period=20)
    if name == "Lowest20":
        return bt.indicators.Lowest(st.data.low, period=20)
    if name == "CrossOver":
        return bt.indicators.CrossOver(c, bt.indicators.EMA(c, period=5))
    if name == "MACD":
        return bt.indicators.MACD(c)
    if name == "MACDHisto":
        return bt.indicators.MACDHisto(c)
    if name == "TrueRange":
        return bt.indicators.TrueRange(st.data)
    raise ValueError("unknown indicator " + name)


def env_checks(st):
    try:
        import sys
        plog("python_version", sys.version.replace("\n", " "))
    except Exception as e:
        plog("python_version FAIL", e)
    try:
        plog("backtrader_version", getattr(bt, "__version__", "unknown"))
    except Exception as e:
        plog("backtrader_version FAIL", e)

    import importlib
    for mod in ["math", "datetime", "random", "collections", "json",
                "zoneinfo", "pytz", "numpy", "pandas", "statistics", "time"]:
        try:
            importlib.import_module(mod)
            st.results["import_" + mod] = "OK"
        except Exception as e:
            st.results["import_" + mod] = "FAIL {}".format(type(e).__name__)
    try:
        from zoneinfo import ZoneInfo
        ZoneInfo("America/New_York")
        st.results["zoneinfo_NY"] = "OK"
    except Exception as e:
        st.results["zoneinfo_NY"] = "FAIL {}: {}".format(type(e).__name__, e)

    # f-strings (syntax check done via eval so this file still parses on old Python)
    try:
        eval('f"{1+1}"')
        st.results["f_strings"] = "OK"
    except Exception as e:
        st.results["f_strings"] = "FAIL {}".format(type(e).__name__)

    # params
    try:
        st.results["params"] = "OK int={} str={} float={}".format(
            st.p.probe_param_int, st.p.probe_param_str, st.p.probe_param_float)
    except Exception as e:
        st.results["params"] = "FAIL {}".format(e)

    # data feed info
    try:
        d = st.data
        st.results["n_datas"] = "OK {}".format(len(st.datas))
        st.results["data_name"] = "OK {}".format(getattr(d, "_name", None))
        tf = getattr(d.p, "timeframe", None)
        comp = getattr(d.p, "compression", None)
        st.results["data_timeframe"] = "OK timeframe={} ({}) compression={}".format(
            tf, bt.TimeFrame.getname(tf, comp) if tf is not None else "?", comp)
        st.results["data_tz_param"] = "OK {}".format(getattr(d.p, "tz", None))
    except Exception as e:
        st.results["data_info"] = "FAIL {}".format(e)

    # broker info
    try:
        b = st.broker
        st.results["broker_class"] = "OK {}".format(type(b).__name__)
        st.results["broker_getvalue"] = "OK {}".format(b.getvalue())
        st.results["broker_getcash"] = "OK {}".format(b.getcash())
    except Exception as e:
        st.results["broker_basic"] = "FAIL {}".format(e)
    try:
        ci = st.broker.getcommissioninfo(st.data)
        parts = []
        for k in ["commission", "mult", "margin", "leverage", "stocklike",
                  "commtype", "percabs", "automargin", "interest"]:
            parts.append("{}={}".format(k, getattr(ci.p, k, "n/a")))
        st.results["commission_info"] = "OK " + " ".join(parts)
    except Exception as e:
        st.results["commission_info"] = "FAIL {}".format(e)

    # order type constants
    for name in ["RSI", "RSI_Safe", "EMA", "ATR", "MACDHisto"]:
        st.results["has_ind_" + name] = "OK" if hasattr(bt.indicators, name) else "FAIL missing"
    for name in ["Market", "Limit", "Stop", "StopLimit", "StopTrail", "Close"]:
        st.results["const_Order." + name] = "OK" if hasattr(bt.Order, name) else "FAIL missing"
    for name in ["buy_bracket", "sell_bracket", "close", "cancel",
                 "order_target_size", "getposition", "add_timer", "notify_cashvalue"]:
        st.results["method_" + name] = "OK" if hasattr(st, name) else "FAIL missing"


def dt_str(st):
    try:
        return st.data.datetime.datetime(0).isoformat()
    except Exception as e:
        return "dtFAIL({})".format(e)


def track_order(st, tag, order):
    if order is None:
        st.results["order_" + tag] = "FAIL returned None"
        return
    st.pending[order.ref] = tag
    st.results["order_" + tag] = "SUBMITTED ref={}".format(order.ref)


def try_order(st, tag, kind, **kw):
    try:
        if kind == "buy":
            return st.buy(**kw)
        if kind == "sell":
            return st.sell(**kw)
        if kind == "close":
            return st.close()
        if kind == "buy_bracket":
            return st.buy_bracket(**kw)
        raise ValueError("unknown order kind " + kind)
    except Exception as e:
        st.results["order_" + tag] = "FAIL {}: {}".format(type(e).__name__, e)
        return None


def cancel_all_orders(st):
    for o in list(getattr(st, "open_orders", [])):
        try:
            if o is not None and o.alive():
                st.cancel(o)
        except Exception:
            pass
    st.open_orders = []


def indicator_values(st, where):
    for name, ind in st.ind.items():
        try:
            if name == "MACDHisto":
                val = "macd={:.4f} signal={:.4f} histo={:.4f}".format(
                    ind.macd[0], ind.signal[0], ind.histo[0])
            elif name == "MACD":
                val = "macd={:.4f} signal={:.4f}".format(ind.macd[0], ind.signal[0])
            else:
                val = "{:.4f}".format(ind[0])
            st.results["val_" + name] = "OK {} @ {} {}".format(val, dt_str(st), where)
        except Exception as e:
            st.results["val_" + name] = "FAIL {}".format(e)


def probe_step(st):
    st.bar += 1
    d = st.data
    # ---- time checks
    try:
        dt = d.datetime.datetime(0)
        if st.bar == 1:
            st.results["datetime_access"] = "OK first={} tzinfo={} date()={} time()={}".format(
                dt.isoformat(), dt.tzinfo, d.datetime.date(0), d.datetime.time(0))
        st.hour_hist[dt.hour] = st.hour_hist.get(dt.hour, 0) + 1
        if st.prev_dt is not None:
            gap = int((dt - st.prev_dt).total_seconds() // 60)
            st.gaps[gap] = st.gaps.get(gap, 0) + 1
        st.prev_dt = dt
        if len(st.first_bars) < 3:
            st.first_bars.append("{} O={} H={} L={} C={} V={}".format(
                dt.isoformat(), d.open[0], d.high[0], d.low[0], d.close[0], d.volume[0]))
        st.last_dt = dt
    except Exception as e:
        st.results["datetime_access"] = "FAIL {}".format(e)

    b = st.bar - PROBE_START_BAR
    if b < 0:
        return
    c = d.close[0]
    if not hasattr(st, "open_orders"):
        st.open_orders = []

    # A: market buy
    if b == 0:
        o = try_order(st, "A_market_buy", "buy", size=PROBE_SIZE)
        track_order(st, "A_market_buy", o)
    # B: protective sell stop below price
    if b == 2:
        pos = st.getposition(d)
        st.results["position_after_buy"] = "OK size={} price={}".format(pos.size, pos.price)
        st.vpp_v0, st.vpp_c0 = st.broker.getvalue(), c
        o = try_order(st, "B_sell_stop_protect", "sell", size=PROBE_SIZE, exectype=bt.Order.Stop, price=c * 0.97)
        track_order(st, "B_sell_stop_protect", o)
        if o is not None:
            st.open_orders.append(o)
    # C: measure money per point per 1.0 size, then close
    if b == 10:
        try:
            v1 = st.broker.getvalue()
            dc = c - st.vpp_c0
            if abs(dc) > 1e-9:
                st.results["value_per_point_per_1_size"] = "OK {:.6f} (value change {:.4f} / price change {:.4f} / size {})".format(
                    (v1 - st.vpp_v0) / dc / PROBE_SIZE, v1 - st.vpp_v0, dc, PROBE_SIZE)
            else:
                st.results["value_per_point_per_1_size"] = "INCONCLUSIVE price unchanged"
        except Exception as e:
            st.results["value_per_point_per_1_size"] = "FAIL {}".format(e)
        cancel_all_orders(st)
        o = try_order(st, "C_close", "close")
        track_order(st, "C_close", o)
    # D: native bracket order
    if b == 20:
        orders = try_order(st, "D_buy_bracket", "buy_bracket", size=PROBE_SIZE, exectype=bt.Order.Market,
                           stopprice=c * 0.97, limitprice=c * 1.03)
        if orders:
            try:
                names = ["D_bracket_main", "D_bracket_stop", "D_bracket_limit"]
                for nm, o in zip(names, orders):
                    track_order(st, nm, o)
                    st.open_orders.append(o)
                st.results["order_D_buy_bracket"] = "OK returned {} orders".format(len(orders))
            except Exception as e:
                st.results["order_D_buy_bracket"] = "FAIL {}".format(e)
    # E: cancel bracket legs, close
    if b == 35:
        st.results["position_before_E"] = "OK size={}".format(st.getposition(d).size)
        cancel_all_orders(st)
        o = try_order(st, "E_close", "close")
        track_order(st, "E_close", o)
    # F: stop-entry orders above / below (breakout style) with OCO
    if b == 45:
        hi, lo = d.high[0], d.low[0]
        o1 = try_order(st, "F_buy_stop_entry", "buy", size=PROBE_SIZE, exectype=bt.Order.Stop, price=hi + (hi - lo) * 0.1)
        track_order(st, "F_buy_stop_entry", o1)
        if o1 is not None:
            st.open_orders.append(o1)
            o2 = try_order(st, "F_sell_stop_entry_oco", "sell", size=PROBE_SIZE, exectype=bt.Order.Stop, price=lo - (hi - lo) * 0.1, oco=o1)
            track_order(st, "F_sell_stop_entry_oco", o2)
            if o2 is not None:
                st.open_orders.append(o2)
    # G: cleanup
    if b == 80:
        st.results["position_before_G"] = "OK size={}".format(st.getposition(d).size)
        cancel_all_orders(st)
        if st.getposition(d).size != 0:
            o = try_order(st, "G_close", "close")
            track_order(st, "G_close", o)
    # H: market short
    if b == 90:
        o = try_order(st, "H_market_sell_short", "sell", size=PROBE_SIZE)
        track_order(st, "H_market_sell_short", o)
    if b == 92:
        st.results["position_after_short"] = "OK size={}".format(st.getposition(d).size)
    # I: limit order far away (should stay pending, then be cancelled)
    if b == 95:
        o = try_order(st, "I_buy_limit_far", "buy", size=PROBE_SIZE, exectype=bt.Order.Limit, price=c * 0.5)
        track_order(st, "I_buy_limit_far", o)
        if o is not None:
            st.open_orders.append(o)
    if b == 100:
        cancel_all_orders(st)
        o = try_order(st, "H_close_short", "close")
        track_order(st, "H_close_short", o)


def gap_sort_key(kv):
    return -kv[1]


class ProbeStrategy(bt.Strategy):
    params = (
        ("probe_param_int", 7),
        ("probe_param_str", "hello"),
        ("probe_param_float", 1.5),
    )

    # ------------------------------------------------------------------ init
    def __init__(self):
        try:
            own = [k for k in type(self).__dict__.keys() if not k.startswith("__")]
            print("PROBE|class_methods_kept " + " ".join(sorted(own)))
            print("PROBE|class_mro " + " > ".join(c.__name__ for c in type(self).__mro__[:6]))
        except Exception as e:
            print("PROBE|class_methods_kept FAIL " + str(e))
        self.results = {}
        try:
            self.results["module_level_class"] = "OK " + str(PlainHelper(21).doubled())
        except Exception as e:
            self.results["module_level_class"] = "FAIL {}: {}".format(type(e).__name__, e)
        self.results["custom_method_kept"] = "OK" if hasattr(self, "custom_method_test") else "FAIL (Studio drops custom methods)"      # feature name -> "OK ..." / "FAIL ..."
        self.bar = 0
        self.ind = {}
        self.order_log = []
        self.trade_log = []
        self.pending = {}
        self.vpp_samples = []
        self.hour_hist = {}
        self.gaps = {}
        self.prev_dt = None
        self.first_bars = []
        self.indicator_report_done = False

        env_checks(self)

        # Indicators: each one is created separately so one failure does not
        # hide the others.
        names = ["EMA200", "EMA800", "EMA5", "RSI2_safediv", "RSI2_Safe", "ATR14",
                 "SMA20", "Highest20", "Lowest20", "CrossOver", "MACD", "MACDHisto",
                 "TrueRange"]
        for name in names:
            try:
                self.ind[name] = make_indicator(self, name)
                self.results["ind_" + name] = "OK created"
            except Exception as e:
                self.results["ind_" + name] = "FAIL {}: {}".format(type(e).__name__, e)

        # MACD .histo attribute (the user said some builds lack it)
        try:
            m = self.ind.get("MACDHisto")
            _ = m.histo if m is not None else None
            self.results["macd_histo_attr"] = "OK" if m is not None else "FAIL no MACDHisto"
        except Exception as e:
            self.results["macd_histo_attr"] = "FAIL {}: {}".format(type(e).__name__, e)



    # ------------------------------------------------------- environment

    # ------------------------------------------------------- notifications
    def notify_order(self, order):
        try:
            self.order_log.append("ref={} type={} side={} status={} size={} price={} exec_price={} exec_size={}".format(
                order.ref, order.getordername(), "BUY" if order.isbuy() else "SELL",
                order.getstatusname(), order.created.size, order.created.price,
                order.executed.price, order.executed.size))
            self.results["notify_order"] = "OK called"
            tag = self.pending.get(order.ref)
            if tag:
                self.results["order_" + tag] = "{} {} exec_price={} dt={}".format(
                    "OK" if order.status == order.Completed else "STATUS",
                    order.getstatusname(), order.executed.price, dt_str(self))
        except Exception as e:
            self.results["notify_order"] = "FAIL {}".format(e)

    def notify_trade(self, trade):
        try:
            if trade.isclosed:
                self.trade_log.append("closed pnl={:.4f} pnlcomm={:.4f} size_hist={} barlen={}".format(
                    trade.pnl, trade.pnlcomm, trade.size, trade.barlen))
                self.results["notify_trade"] = "OK closed trades seen"
        except Exception as e:
            self.results["notify_trade"] = "FAIL {}".format(e)

    # ------------------------------------------------------- helpers




    # ------------------------------------------------------- per bar
    def prenext(self):
        probe_step(self)

    def next(self):
        if not self.indicator_report_done:
            indicator_values(self, "first_next_call")
            self.indicator_report_done = True
        probe_step(self)




    # ------------------------------------------------------- report
    def stop(self):
        if not self.indicator_report_done:
            indicator_values(self, "at_stop (next() never ran: not enough bars for EMA800?)")
        try:
            self.results["final_value"] = "OK {}".format(self.broker.getvalue())
            self.results["bars_processed"] = "OK {} last={}".format(self.bar, getattr(self, "last_dt", None))
        except Exception as e:
            self.results["final_value"] = "FAIL {}".format(e)
        plog("==== FIRST BARS (compare with the chart to see if time is bar OPEN or CLOSE, and the time zone) ====")
        for line in self.first_bars:
            plog("bar", line)
        plog("==== BARS PER HOUR OF DAY (hour as stamped in data) ====")
        plog("hours", " ".join("{}:{}".format(h, self.hour_hist[h]) for h in sorted(self.hour_hist)))
        plog("==== GAPS BETWEEN BARS (minutes:count, top 8) ====")
        top = sorted(self.gaps.items(), key=gap_sort_key)[:8]
        plog("gaps", " ".join("{}:{}".format(k, v) for k, v in top))
        plog("==== ORDER EVENTS ====")
        for line in self.order_log:
            plog("order", line)
        plog("==== TRADES ====")
        for line in self.trade_log:
            plog("trade", line)
        plog("==== SUMMARY ====")
        for k in sorted(self.results):
            plog("SUMMARY", k, "=>", self.results[k])
        plog("==== END OF PROBE ====")

    def custom_method_test(self):
        # Diagnostic only: never called. __init__ checks if Studio kept it.
        return True
