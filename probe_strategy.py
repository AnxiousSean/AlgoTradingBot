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


def _p(*parts):
    # Every output line starts with PROBE| so it is easy to find.
    try:
        print("PROBE|" + " ".join(str(x) for x in parts))
    except Exception:
        pass


class ProbeStrategy(bt.Strategy):
    params = (
        ("probe_param_int", 7),
        ("probe_param_str", "hello"),
        ("probe_param_float", 1.5),
    )

    # ------------------------------------------------------------------ init
    def __init__(self):
        self.results = {}      # feature name -> "OK ..." / "FAIL ..."
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

        self._env_checks()

        # Indicators: each one is created separately so one failure does not
        # hide the others.
        names = ["EMA200", "EMA800", "EMA5", "RSI2_safediv", "RSI2_Safe", "ATR14",
                 "SMA20", "Highest20", "Lowest20", "CrossOver", "MACD", "MACDHisto",
                 "TrueRange"]
        for name in names:
            try:
                self.ind[name] = self._make_indicator(name)
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

    def _make_indicator(self, name):
        # NOTE: plain RSI(period=2) crashes with ZeroDivisionError on runs of
        # same-direction bars, so only the safe-division versions are run.
        c = self.data.close
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
            return bt.indicators.ATR(self.data, period=14)
        if name == "SMA20":
            return bt.indicators.SMA(c, period=20)
        if name == "Highest20":
            return bt.indicators.Highest(self.data.high, period=20)
        if name == "Lowest20":
            return bt.indicators.Lowest(self.data.low, period=20)
        if name == "CrossOver":
            return bt.indicators.CrossOver(c, bt.indicators.EMA(c, period=5))
        if name == "MACD":
            return bt.indicators.MACD(c)
        if name == "MACDHisto":
            return bt.indicators.MACDHisto(c)
        if name == "TrueRange":
            return bt.indicators.TrueRange(self.data)
        raise ValueError("unknown indicator " + name)

    # ------------------------------------------------------- environment
    def _env_checks(self):
        try:
            import sys
            _p("python_version", sys.version.replace("\n", " "))
        except Exception as e:
            _p("python_version FAIL", e)
        try:
            _p("backtrader_version", getattr(bt, "__version__", "unknown"))
        except Exception as e:
            _p("backtrader_version FAIL", e)

        for mod in ["math", "datetime", "random", "collections", "json",
                    "zoneinfo", "pytz", "numpy", "pandas", "statistics", "time"]:
            try:
                __import__(mod)
                self.results["import_" + mod] = "OK"
            except Exception as e:
                self.results["import_" + mod] = "FAIL {}".format(type(e).__name__)
        try:
            from zoneinfo import ZoneInfo
            ZoneInfo("America/New_York")
            self.results["zoneinfo_NY"] = "OK"
        except Exception as e:
            self.results["zoneinfo_NY"] = "FAIL {}: {}".format(type(e).__name__, e)

        # f-strings (syntax check done via eval so this file still parses on old Python)
        try:
            eval('f"{1+1}"')
            self.results["f_strings"] = "OK"
        except Exception as e:
            self.results["f_strings"] = "FAIL {}".format(type(e).__name__)

        # params
        try:
            self.results["params"] = "OK int={} str={} float={}".format(
                self.p.probe_param_int, self.p.probe_param_str, self.p.probe_param_float)
        except Exception as e:
            self.results["params"] = "FAIL {}".format(e)

        # data feed info
        try:
            d = self.data
            self.results["n_datas"] = "OK {}".format(len(self.datas))
            self.results["data_name"] = "OK {}".format(getattr(d, "_name", None))
            tf = getattr(d.p, "timeframe", None)
            comp = getattr(d.p, "compression", None)
            self.results["data_timeframe"] = "OK timeframe={} ({}) compression={}".format(
                tf, bt.TimeFrame.getname(tf, comp) if tf is not None else "?", comp)
            self.results["data_tz_param"] = "OK {}".format(getattr(d.p, "tz", None))
        except Exception as e:
            self.results["data_info"] = "FAIL {}".format(e)

        # broker info
        try:
            b = self.broker
            self.results["broker_class"] = "OK {}".format(type(b).__name__)
            self.results["broker_getvalue"] = "OK {}".format(b.getvalue())
            self.results["broker_getcash"] = "OK {}".format(b.getcash())
        except Exception as e:
            self.results["broker_basic"] = "FAIL {}".format(e)
        try:
            ci = self.broker.getcommissioninfo(self.data)
            parts = []
            for k in ["commission", "mult", "margin", "leverage", "stocklike",
                      "commtype", "percabs", "automargin", "interest"]:
                parts.append("{}={}".format(k, getattr(ci.p, k, "n/a")))
            self.results["commission_info"] = "OK " + " ".join(parts)
        except Exception as e:
            self.results["commission_info"] = "FAIL {}".format(e)

        # order type constants
        for name in ["RSI", "RSI_Safe", "EMA", "ATR", "MACDHisto"]:
            self.results["has_ind_" + name] = "OK" if hasattr(bt.indicators, name) else "FAIL missing"
        for name in ["Market", "Limit", "Stop", "StopLimit", "StopTrail", "Close"]:
            self.results["const_Order." + name] = "OK" if hasattr(bt.Order, name) else "FAIL missing"
        for name in ["buy_bracket", "sell_bracket", "close", "cancel",
                     "order_target_size", "getposition", "add_timer", "notify_cashvalue"]:
            self.results["method_" + name] = "OK" if hasattr(self, name) else "FAIL missing"

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
                    order.getstatusname(), order.executed.price, self._dt_str())
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
    def _dt_str(self):
        try:
            return self.data.datetime.datetime(0).isoformat()
        except Exception as e:
            return "dtFAIL({})".format(e)

    def _track(self, tag, order):
        if order is None:
            self.results["order_" + tag] = "FAIL returned None"
            return
        self.pending[order.ref] = tag
        self.results["order_" + tag] = "SUBMITTED ref={}".format(order.ref)

    def _try(self, tag, kind, **kw):
        try:
            if kind == "buy":
                return self.buy(**kw)
            if kind == "sell":
                return self.sell(**kw)
            if kind == "close":
                return self.close()
            if kind == "buy_bracket":
                return self.buy_bracket(**kw)
            raise ValueError("unknown order kind " + kind)
        except Exception as e:
            self.results["order_" + tag] = "FAIL {}: {}".format(type(e).__name__, e)
            return None

    def _cancel_all(self):
        for o in list(getattr(self, "_open_orders", [])):
            try:
                if o is not None and o.alive():
                    self.cancel(o)
            except Exception:
                pass
        self._open_orders = []

    # ------------------------------------------------------- per bar
    def prenext(self):
        self._step()

    def next(self):
        if not self.indicator_report_done:
            self._indicator_values("first_next_call")
            self.indicator_report_done = True
        self._step()

    def _indicator_values(self, where):
        for name, ind in self.ind.items():
            try:
                if name == "MACDHisto":
                    val = "macd={:.4f} signal={:.4f} histo={:.4f}".format(
                        ind.macd[0], ind.signal[0], ind.histo[0])
                elif name == "MACD":
                    val = "macd={:.4f} signal={:.4f}".format(ind.macd[0], ind.signal[0])
                else:
                    val = "{:.4f}".format(ind[0])
                self.results["val_" + name] = "OK {} @ {} {}".format(val, self._dt_str(), where)
            except Exception as e:
                self.results["val_" + name] = "FAIL {}".format(e)

    def _step(self):
        self.bar += 1
        d = self.data
        # ---- time checks
        try:
            dt = d.datetime.datetime(0)
            if self.bar == 1:
                self.results["datetime_access"] = "OK first={} tzinfo={} date()={} time()={}".format(
                    dt.isoformat(), dt.tzinfo, d.datetime.date(0), d.datetime.time(0))
            self.hour_hist[dt.hour] = self.hour_hist.get(dt.hour, 0) + 1
            if self.prev_dt is not None:
                gap = int((dt - self.prev_dt).total_seconds() // 60)
                self.gaps[gap] = self.gaps.get(gap, 0) + 1
            self.prev_dt = dt
            if len(self.first_bars) < 3:
                self.first_bars.append("{} O={} H={} L={} C={} V={}".format(
                    dt.isoformat(), d.open[0], d.high[0], d.low[0], d.close[0], d.volume[0]))
            self.last_dt = dt
        except Exception as e:
            self.results["datetime_access"] = "FAIL {}".format(e)

        b = self.bar - PROBE_START_BAR
        if b < 0:
            return
        c = d.close[0]
        if not hasattr(self, "_open_orders"):
            self._open_orders = []

        # A: market buy
        if b == 0:
            o = self._try("A_market_buy", "buy", size=PROBE_SIZE)
            self._track("A_market_buy", o)
        # B: protective sell stop below price
        if b == 2:
            pos = self.getposition(d)
            self.results["position_after_buy"] = "OK size={} price={}".format(pos.size, pos.price)
            self.vpp_v0, self.vpp_c0 = self.broker.getvalue(), c
            o = self._try("B_sell_stop_protect", "sell", size=PROBE_SIZE, exectype=bt.Order.Stop, price=c * 0.97)
            self._track("B_sell_stop_protect", o)
            if o is not None:
                self._open_orders.append(o)
        # C: measure money per point per 1.0 size, then close
        if b == 10:
            try:
                v1 = self.broker.getvalue()
                dc = c - self.vpp_c0
                if abs(dc) > 1e-9:
                    self.results["value_per_point_per_1_size"] = "OK {:.6f} (value change {:.4f} / price change {:.4f} / size {})".format(
                        (v1 - self.vpp_v0) / dc / PROBE_SIZE, v1 - self.vpp_v0, dc, PROBE_SIZE)
                else:
                    self.results["value_per_point_per_1_size"] = "INCONCLUSIVE price unchanged"
            except Exception as e:
                self.results["value_per_point_per_1_size"] = "FAIL {}".format(e)
            self._cancel_all()
            o = self._try("C_close", "close")
            self._track("C_close", o)
        # D: native bracket order
        if b == 20:
            orders = self._try("D_buy_bracket", "buy_bracket", size=PROBE_SIZE, exectype=bt.Order.Market,
                               stopprice=c * 0.97, limitprice=c * 1.03)
            if orders:
                try:
                    names = ["D_bracket_main", "D_bracket_stop", "D_bracket_limit"]
                    for nm, o in zip(names, orders):
                        self._track(nm, o)
                        self._open_orders.append(o)
                    self.results["order_D_buy_bracket"] = "OK returned {} orders".format(len(orders))
                except Exception as e:
                    self.results["order_D_buy_bracket"] = "FAIL {}".format(e)
        # E: cancel bracket legs, close
        if b == 35:
            self.results["position_before_E"] = "OK size={}".format(self.getposition(d).size)
            self._cancel_all()
            o = self._try("E_close", "close")
            self._track("E_close", o)
        # F: stop-entry orders above / below (breakout style) with OCO
        if b == 45:
            hi, lo = d.high[0], d.low[0]
            o1 = self._try("F_buy_stop_entry", "buy", size=PROBE_SIZE, exectype=bt.Order.Stop, price=hi + (hi - lo) * 0.1)
            self._track("F_buy_stop_entry", o1)
            if o1 is not None:
                self._open_orders.append(o1)
                o2 = self._try("F_sell_stop_entry_oco", "sell", size=PROBE_SIZE, exectype=bt.Order.Stop, price=lo - (hi - lo) * 0.1, oco=o1)
                self._track("F_sell_stop_entry_oco", o2)
                if o2 is not None:
                    self._open_orders.append(o2)
        # G: cleanup
        if b == 80:
            self.results["position_before_G"] = "OK size={}".format(self.getposition(d).size)
            self._cancel_all()
            if self.getposition(d).size != 0:
                o = self._try("G_close", "close")
                self._track("G_close", o)
        # H: market short
        if b == 90:
            o = self._try("H_market_sell_short", "sell", size=PROBE_SIZE)
            self._track("H_market_sell_short", o)
        if b == 92:
            self.results["position_after_short"] = "OK size={}".format(self.getposition(d).size)
        # I: limit order far away (should stay pending, then be cancelled)
        if b == 95:
            o = self._try("I_buy_limit_far", "buy", size=PROBE_SIZE, exectype=bt.Order.Limit, price=c * 0.5)
            self._track("I_buy_limit_far", o)
            if o is not None:
                self._open_orders.append(o)
        if b == 100:
            self._cancel_all()
            o = self._try("H_close_short", "close")
            self._track("H_close_short", o)

    def _gap_sort_key(self, kv):
        return -kv[1]

    # ------------------------------------------------------- report
    def stop(self):
        if not self.indicator_report_done:
            self._indicator_values("at_stop (next() never ran: not enough bars for EMA800?)")
        try:
            self.results["final_value"] = "OK {}".format(self.broker.getvalue())
            self.results["bars_processed"] = "OK {} last={}".format(self.bar, getattr(self, "last_dt", None))
        except Exception as e:
            self.results["final_value"] = "FAIL {}".format(e)
        _p("==== FIRST BARS (compare with the chart to see if time is bar OPEN or CLOSE, and the time zone) ====")
        for line in self.first_bars:
            _p("bar", line)
        _p("==== BARS PER HOUR OF DAY (hour as stamped in data) ====")
        _p("hours", " ".join("{}:{}".format(h, self.hour_hist[h]) for h in sorted(self.hour_hist)))
        _p("==== GAPS BETWEEN BARS (minutes:count, top 8) ====")
        top = sorted(self.gaps.items(), key=self._gap_sort_key)[:8]
        _p("gaps", " ".join("{}:{}".format(k, v) for k, v in top))
        _p("==== ORDER EVENTS ====")
        for line in self.order_log:
            _p("order", line)
        _p("==== TRADES ====")
        for line in self.trade_log:
            _p("trade", line)
        _p("==== SUMMARY ====")
        for k in sorted(self.results):
            _p("SUMMARY", k, "=>", self.results[k])
        _p("==== END OF PROBE ====")
