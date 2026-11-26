import math
import datetime
import backtrader as bt

# STAGE 0 PROBE - TradeLocker Studio capability test (plain-code version)
# Run it in the BACKTESTER ONLY: it places small test orders.
# Settings: margin 5000, any instrument, 5m or 15m, about 1 month of data.
# Then copy every line that starts with "PROBE|" and send it back.
# If 0.01 lots is rejected, set PROBE_SIZE to your minimum lot.
#
# This version uses only plain Python, because Studio's code checks
# rejected parts of the earlier versions.

PROBE_SIZE = 0.01
PROBE_START_BAR = 30


def plog(text):
    print("PROBE|" + text)


class PlainHelper(object):
    # Tests that a normal class outside the strategy works (the risk guard is one).
    def __init__(self, x):
        self.x = x

    def doubled(self):
        return self.x * 2


def new_state():
    st = {}
    st["results"] = {}
    st["bar"] = 0
    st["orders"] = {}
    st["open_orders"] = []
    st["order_log"] = []
    st["trade_log"] = []
    st["hours"] = {}
    st["gaps"] = {}
    st["prev_dt"] = None
    st["first_bars"] = []
    st["ind_done"] = False
    return st


def res(st, key, text):
    st["results"][key] = text


def make_indicator(strat, name):
    c = strat.data.close
    if name == "EMA200":
        return bt.indicators.EMA(c, period=200)
    if name == "EMA800":
        return bt.indicators.EMA(c, period=800)
    if name == "EMA5":
        return bt.indicators.EMA(c, period=5)
    if name == "RSI2_safediv":
        # plain RSI(period=2) can crash with ZeroDivisionError, so use safediv
        return bt.indicators.RSI(c, period=2, safediv=True)
    if name == "RSI2_Safe":
        return bt.indicators.RSI_Safe(c, period=2)
    if name == "ATR14":
        return bt.indicators.ATR(strat.data, period=14)
    if name == "SMA20":
        return bt.indicators.SMA(c, period=20)
    if name == "Highest20":
        return bt.indicators.Highest(strat.data.high, period=20)
    if name == "Lowest20":
        return bt.indicators.Lowest(strat.data.low, period=20)
    if name == "CrossOver":
        return bt.indicators.CrossOver(c, bt.indicators.EMA(c, period=5))
    if name == "MACD":
        return bt.indicators.MACD(c)
    if name == "MACDHisto":
        return bt.indicators.MACDHisto(c)
    return None


def env_checks(strat, st):
    res(st, "math_module", "OK sqrt2=" + str(round(math.sqrt(2), 4)))
    try:
        d = datetime.datetime(2026, 7, 15, 12, 0) + datetime.timedelta(hours=5)
        res(st, "datetime_module", "OK " + d.isoformat())
    except Exception as e:
        res(st, "datetime_module", "FAIL " + str(e))
    try:
        res(st, "params", "OK int=" + str(strat.p.probe_param_int) + " str=" + str(strat.p.probe_param_str)
            + " float=" + str(strat.p.probe_param_float))
    except Exception as e:
        res(st, "params", "FAIL " + str(e))
    try:
        res(st, "n_datas", "OK " + str(len(strat.datas)))
        res(st, "data_timeframe", "OK timeframe=" + str(strat.data.p.timeframe)
            + " compression=" + str(strat.data.p.compression))
    except Exception as e:
        res(st, "data_info", "FAIL " + str(e))
    try:
        res(st, "broker_getvalue", "OK " + str(strat.broker.getvalue()))
        res(st, "broker_getcash", "OK " + str(strat.broker.getcash()))
    except Exception as e:
        res(st, "broker_basic", "FAIL " + str(e))
    try:
        ci = strat.broker.getcommissioninfo(strat.data)
        res(st, "commission_info", "OK commission=" + str(ci.p.commission) + " mult=" + str(ci.p.mult)
            + " margin=" + str(ci.p.margin) + " leverage=" + str(ci.p.leverage))
    except Exception as e:
        res(st, "commission_info", "FAIL " + str(e))
    try:
        res(st, "module_level_class", "OK " + str(PlainHelper(21).doubled()))
    except Exception as e:
        res(st, "module_level_class", "FAIL " + str(e))
    try:
        strat.custom_method_test()
        res(st, "custom_method_kept", "OK")
    except Exception as e:
        res(st, "custom_method_kept", "FAIL " + str(e))


def dt_str(strat):
    try:
        return strat.data.datetime.datetime(0).isoformat()
    except Exception as e:
        return "dtFAIL(" + str(e) + ")"


def track(st, tag, order):
    if order is None:
        res(st, "order_" + tag, "FAIL returned None")
        return
    st["orders"][order.ref] = tag
    res(st, "order_" + tag, "SUBMITTED ref=" + str(order.ref))


def cancel_all(strat, st):
    for o in st["open_orders"]:
        try:
            if o.alive():
                strat.cancel(o)
        except Exception:
            pass
    st["open_orders"] = []


def indicator_values(strat, st, where):
    for name in st["ind"]:
        ind = st["ind"][name]
        try:
            if name == "MACDHisto":
                val = ("macd=" + str(round(ind.macd[0], 4)) + " signal=" + str(round(ind.signal[0], 4))
                       + " histo=" + str(round(ind.histo[0], 4)))
            elif name == "MACD":
                val = "macd=" + str(round(ind.macd[0], 4)) + " signal=" + str(round(ind.signal[0], 4))
            else:
                val = str(round(ind[0], 4))
            res(st, "val_" + name, "OK " + val + " @ " + dt_str(strat) + " " + where)
        except Exception as e:
            res(st, "val_" + name, "FAIL " + str(e))


def record_time(strat, st):
    try:
        dt = strat.data.datetime.datetime(0)
        if st["bar"] == 1:
            res(st, "datetime_access", "OK first=" + dt.isoformat() + " tzinfo=" + str(dt.tzinfo))
        st["hours"][dt.hour] = st["hours"].get(dt.hour, 0) + 1
        if st["prev_dt"] is not None:
            gap = int((dt - st["prev_dt"]).total_seconds() // 60)
            st["gaps"][gap] = st["gaps"].get(gap, 0) + 1
        st["prev_dt"] = dt
        if len(st["first_bars"]) < 3:
            d = strat.data
            st["first_bars"].append(dt.isoformat() + " O=" + str(d.open[0]) + " H=" + str(d.high[0])
                                    + " L=" + str(d.low[0]) + " C=" + str(d.close[0]))
    except Exception as e:
        res(st, "datetime_access", "FAIL " + str(e))


def probe_step(strat, st):
    st["bar"] += 1
    record_time(strat, st)
    b = st["bar"] - PROBE_START_BAR
    if b < 0:
        return
    d = strat.data
    c = d.close[0]
    try:
        if b == 0:
            track(st, "A_market_buy", strat.buy(size=PROBE_SIZE))
        if b == 2:
            pos = strat.getposition(d)
            res(st, "position_after_buy", "OK size=" + str(pos.size) + " price=" + str(pos.price))
            st["v0"] = strat.broker.getvalue()
            st["c0"] = c
            o = strat.sell(size=PROBE_SIZE, exectype=bt.Order.Stop, price=c * 0.97)
            track(st, "B_sell_stop_protect", o)
            st["open_orders"].append(o)
        if b == 10:
            v1 = strat.broker.getvalue()
            dc = c - st["c0"]
            if abs(dc) > 1e-9:
                res(st, "value_per_point_per_1_size", "OK " + str(round((v1 - st["v0"]) / dc / PROBE_SIZE, 6))
                    + " (value change " + str(round(v1 - st["v0"], 4)) + " / price change " + str(round(dc, 4)) + ")")
            else:
                res(st, "value_per_point_per_1_size", "INCONCLUSIVE price unchanged")
            cancel_all(strat, st)
            track(st, "C_close", strat.close())
        if b == 20:
            orders = strat.buy_bracket(size=PROBE_SIZE, exectype=bt.Order.Market,
                                       stopprice=c * 0.97, limitprice=c * 1.03)
            res(st, "order_D_buy_bracket", "OK returned " + str(len(orders)) + " orders")
            track(st, "D_bracket_main", orders[0])
            track(st, "D_bracket_stop", orders[1])
            track(st, "D_bracket_limit", orders[2])
            st["open_orders"].append(orders[1])
            st["open_orders"].append(orders[2])
        if b == 35:
            res(st, "position_before_E", "OK size=" + str(strat.getposition(d).size))
            cancel_all(strat, st)
            track(st, "E_close", strat.close())
        if b == 45:
            hi = d.high[0]
            lo = d.low[0]
            o1 = strat.buy(size=PROBE_SIZE, exectype=bt.Order.Stop, price=hi + (hi - lo) * 0.1)
            track(st, "F_buy_stop_entry", o1)
            st["open_orders"].append(o1)
            o2 = strat.sell(size=PROBE_SIZE, exectype=bt.Order.Stop, price=lo - (hi - lo) * 0.1, oco=o1)
            track(st, "F_sell_stop_entry_oco", o2)
            st["open_orders"].append(o2)
        if b == 80:
            res(st, "position_before_G", "OK size=" + str(strat.getposition(d).size))
            cancel_all(strat, st)
            if strat.getposition(d).size != 0:
                track(st, "G_close", strat.close())
        if b == 90:
            track(st, "H_market_sell_short", strat.sell(size=PROBE_SIZE))
        if b == 92:
            res(st, "position_after_short", "OK size=" + str(strat.getposition(d).size))
        if b == 95:
            o = strat.buy(size=PROBE_SIZE, exectype=bt.Order.Limit, price=c * 0.5)
            track(st, "I_buy_limit_far", o)
            st["open_orders"].append(o)
        if b == 100:
            cancel_all(strat, st)
            track(st, "H_close_short", strat.close())
    except Exception as e:
        res(st, "order_step_" + str(b), "FAIL " + str(e))


def final_report(strat, st):
    if not st["ind_done"]:
        indicator_values(strat, st, "at_stop (next never ran)")
    res(st, "final_value", "OK " + str(strat.broker.getvalue()))
    res(st, "bars_processed", "OK " + str(st["bar"]))
    plog("==== FIRST BARS ====")
    for line in st["first_bars"]:
        plog("bar " + line)
    plog("==== BARS PER HOUR (hour:count) ====")
    plog("hours " + " ".join([str(h) + ":" + str(st["hours"][h]) for h in sorted(st["hours"])]))
    plog("==== GAPS BETWEEN BARS (minutes:count) ====")
    gap_keys = sorted(st["gaps"])
    plog("gaps " + " ".join([str(g) + ":" + str(st["gaps"][g]) for g in gap_keys[:12]]))
    plog("==== ORDER EVENTS ====")
    for line in st["order_log"]:
        plog("order " + line)
    plog("==== TRADES ====")
    for line in st["trade_log"]:
        plog("trade " + line)
    plog("==== SUMMARY ====")
    for k in sorted(st["results"]):
        plog("SUMMARY " + k + " => " + st["results"][k])
    plog("==== END OF PROBE ====")


class ProbeStrategy(bt.Strategy):
    params = (
        ("probe_param_int", 7),
        ("probe_param_str", "hello"),
        ("probe_param_float", 1.5),
    )

    def __init__(self):
        plog("init start")
        self.st = new_state()
        self.st["ind"] = {}
        env_checks(self, self.st)
        names = ["EMA200", "EMA800", "EMA5", "RSI2_safediv", "RSI2_Safe", "ATR14", "SMA20",
                 "Highest20", "Lowest20", "CrossOver", "MACD", "MACDHisto"]
        for name in names:
            try:
                self.st["ind"][name] = make_indicator(self, name)
                res(self.st, "ind_" + name, "OK created")
            except Exception as e:
                res(self.st, "ind_" + name, "FAIL " + str(e))
        plog("init done")

    def notify_order(self, order):
        st = self.st
        try:
            line = ("ref=" + str(order.ref) + " " + ("BUY" if order.isbuy() else "SELL")
                    + " status=" + order.getstatusname() + " size=" + str(order.created.size)
                    + " exec_price=" + str(order.executed.price) + " at " + dt_str(self))
            st["order_log"].append(line)
            res(st, "notify_order", "OK called")
            if order.ref in st["orders"]:
                tag = st["orders"][order.ref]
                ok = "OK " if order.status == order.Completed else "STATUS "
                res(st, "order_" + tag, ok + order.getstatusname() + " exec_price="
                    + str(order.executed.price) + " at " + dt_str(self))
        except Exception as e:
            res(st, "notify_order", "FAIL " + str(e))

    def notify_trade(self, trade):
        try:
            if trade.isclosed:
                self.st["trade_log"].append("closed pnl=" + str(round(trade.pnl, 4))
                                            + " pnlcomm=" + str(round(trade.pnlcomm, 4)))
                res(self.st, "notify_trade", "OK closed trades seen")
        except Exception as e:
            res(self.st, "notify_trade", "FAIL " + str(e))

    def prenext(self):
        probe_step(self, self.st)

    def next(self):
        if not self.st["ind_done"]:
            indicator_values(self, self.st, "first_next_call")
            self.st["ind_done"] = True
        probe_step(self, self.st)

    def stop(self):
        final_report(self, self.st)

    def custom_method_test(self):
        return True
