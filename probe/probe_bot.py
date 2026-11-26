# =============================================================================
# probe_bot.py  --  TradeLocker Studio platform capability probe (Phase 0)
#
# PURPOSE: discover what Studio's Backtrader build actually supports, before we
# design anything on top of it. It is NOT a trading strategy.
#
# SAFETY:
#   * Run it in the Studio BACKTESTER first. If you also launch it live, use a
#     TradeLocker DEMO account only -- NEVER the GFT challenge account.
#   * It places ~8 tiny test trades (size = probe_size param), one at a time, and is
#     always flat between tests. It never holds a buy and a sell at once: if a
#     one-cancels-other leg fills, the other leg is cancelled immediately.
#   * After the last test it does nothing (just keeps logging timestamp gaps).
#
# OUTPUT: every line starts with "PROBE|". The most important block is the
# "PROBE|SUMMARY" section printed when the backtest ends. Paste the whole log
# back if you can; if it's too long, paste everything from the first
# "PROBE|ENV" line to the first 60 "PROBE|BAR" lines, plus the full SUMMARY.
#
# Original code written for this project. Only `backtrader` is required; every
# other import is optional and tested.
# =============================================================================

import backtrader as bt

# ---- optional imports: each one is tested and reported --------------------
IMPORTS = {}
try:
    import sys
    IMPORTS['sys'] = 'OK'
except Exception as e:  # noqa
    sys = None
    IMPORTS['sys'] = 'FAIL %r' % (e,)
try:
    import math
    IMPORTS['math'] = 'OK'
except Exception as e:
    math = None
    IMPORTS['math'] = 'FAIL %r' % (e,)
try:
    import datetime
    IMPORTS['datetime'] = 'OK'
except Exception as e:
    datetime = None
    IMPORTS['datetime'] = 'FAIL %r' % (e,)
try:
    import collections
    IMPORTS['collections'] = 'OK'
except Exception as e:
    collections = None
    IMPORTS['collections'] = 'FAIL %r' % (e,)
try:
    import statistics
    IMPORTS['statistics'] = 'OK'
except Exception as e:
    statistics = None
    IMPORTS['statistics'] = 'FAIL %r' % (e,)
try:
    import numpy
    IMPORTS['numpy'] = 'OK %s' % getattr(numpy, '__version__', '?')
except Exception as e:
    numpy = None
    IMPORTS['numpy'] = 'FAIL %r' % (e,)
try:
    import pandas
    IMPORTS['pandas'] = 'OK %s' % getattr(pandas, '__version__', '?')
except Exception as e:
    pandas = None
    IMPORTS['pandas'] = 'FAIL %r' % (e,)
try:
    import zoneinfo
    zoneinfo.ZoneInfo('America/New_York')
    IMPORTS['zoneinfo(America/New_York)'] = 'OK'
except Exception as e:
    zoneinfo = None
    IMPORTS['zoneinfo(America/New_York)'] = 'FAIL %r' % (e,)
try:
    import time as _time
    IMPORTS['time'] = 'OK'
except Exception as e:
    _time = None
    IMPORTS['time'] = 'FAIL %r' % (e,)


def _r(x, nd=5):
    try:
        return round(float(x), nd)
    except Exception:
        return x


def _ny_is_dst(d):
    """US daylight saving: 2nd Sunday of March 02:00 -> 1st Sunday of Nov 02:00.
    Computed by hand so it works even if zoneinfo is missing. Date precision
    is enough here: the market is closed when the switch happens."""
    y = d.year
    mar1 = datetime.date(y, 3, 1)
    first_sun_mar = 1 + (6 - mar1.weekday()) % 7
    start = datetime.date(y, 3, first_sun_mar + 7)
    nov1 = datetime.date(y, 11, 1)
    end = datetime.date(y, 11, 1 + (6 - nov1.weekday()) % 7)
    dd = d.date() if hasattr(d, 'date') else d
    return start <= dd < end


class ProbeStrategy(bt.Strategy):

    # ------------------------------------------------------------- CONFIG
    # All settings live here (Backtrader "params"); read as self.p.<name>.
    params = (
        ('probe_size', 0.01),     # order size for every test trade. If every order
                                  # shows Rejected/Margin, try 1 or 0.1 and tell me.
        ('move_pct', 0.0015),     # distance of test stop/limit entries from price (0.15%)
        ('bracket_pct', 0.003),   # stop/target distance in the bracket tests (0.3%)
        ('hold_bars', 12),        # bars to hold the market-order test position
        ('max_bar_lines', 60),    # how many initial bars to print
        ('max_gap_lines', 80),    # how many timestamp gaps (session breaks) to print
        ('gap_min_minutes', 30),  # a jump between bars bigger than this counts as a gap
    )

    # ------------------------------------------------------------------ util
    def plog(self, msg):
        line = 'PROBE|' + msg
        try:
            print(line)
        except Exception:
            pass
        self._lines_logged += 1

    def _dt(self, ago=0):
        try:
            return self.data.datetime.datetime(ago)
        except Exception:
            return None

    def _bar(self):
        return 'O=%s H=%s L=%s C=%s' % (_r(self.data.open[0]), _r(self.data.high[0]),
                                        _r(self.data.low[0]), _r(self.data.close[0]))

    def _attr(self, obj, name):
        try:
            return 'yes' if hasattr(obj, name) else 'NO'
        except Exception as e:
            return 'ERR %r' % (e,)

    # ------------------------------------------------------------------ init
    def __init__(self):
        self._lines_logged = 0
        self.results = {}          # test name -> result string
        self.notes = []            # free-form findings
        self.order_tag = {}        # order.ref -> test tag
        self.bar_n = 0
        self.prev_dt = None
        self.deltas = []
        self.gaps = []
        self.offset_votes = {}
        self.bar_minutes = None

        self.plog('ENV|python=%s' % (sys.version.replace('\n', ' ') if sys else '?'))
        self.plog('ENV|backtrader=%s' % getattr(bt, '__version__', 'MISSING'))
        for k in sorted(IMPORTS):
            self.plog('ENV|import %s -> %s' % (k, IMPORTS[k]))
        self.plog('ENV|strategy has builtin .log(): %s' % self._attr(bt.Strategy, 'log'))

        # ---- data feeds
        try:
            self.plog('DATA|len(self.datas)=%d' % len(self.datas))
            for i, d in enumerate(self.datas):
                tf = getattr(getattr(d, 'p', None), 'timeframe', '?')
                comp = getattr(getattr(d, 'p', None), 'compression', '?')
                try:
                    tfname = bt.TimeFrame.getname(tf, comp)
                except Exception:
                    tfname = '?'
                tz = getattr(getattr(d, 'p', None), 'tz', '?')
                self.plog('DATA|feed %d name=%r class=%s timeframe=%s(%s) compression=%s tz=%r'
                          % (i, getattr(d, '_name', '?'), type(d).__name__, tf, tfname, comp, tz))
                try:
                    self.plog('DATA|feed %d lines=%s' % (i, list(d.lines.getlinealiases())))
                except Exception as e:
                    self.plog('DATA|feed %d lines=ERR %r' % (i, e))
        except Exception as e:
            self.plog('DATA|ERR %r' % (e,))

        # ---- broker / commission settings (do they model costs?)
        try:
            self.plog('BROKER|class=%s' % type(self.broker).__name__)
            bp = getattr(self.broker, 'p', None)
            if bp is not None:
                for k in ('cash', 'checksubmit', 'slip_perc', 'slip_fixed', 'slip_open',
                          'slip_match', 'slip_limit', 'slip_out', 'coc', 'coo', 'int2pnl',
                          'shortcash', 'fundmode'):
                    if hasattr(bp, k):
                        self.plog('BROKER|param %s=%r' % (k, getattr(bp, k)))
        except Exception as e:
            self.plog('BROKER|ERR %r' % (e,))
        try:
            ci = self.broker.getcommissioninfo(self.data)
            self.plog('COMMINFO|class=%s' % type(ci).__name__)
            for k in ('commission', 'mult', 'margin', 'commtype', 'stocklike', 'percabs',
                      'leverage', 'interest', 'automargin'):
                if hasattr(ci.p, k):
                    self.plog('COMMINFO|%s=%r' % (k, getattr(ci.p, k)))
        except Exception as e:
            self.plog('COMMINFO|ERR %r' % (e,))

        # ---- order types / API surface
        for name in ('Market', 'Close', 'Limit', 'Stop', 'StopLimit', 'StopTrail',
                     'StopTrailLimit'):
            self.plog('API|bt.Order.%s: %s' % (name, self._attr(bt.Order, name)))
        for name in ('buy', 'sell', 'close', 'cancel', 'buy_bracket', 'sell_bracket',
                     'order_target_size', 'notify_order', 'notify_trade',
                     'notify_cashvalue', 'getposition'):
            self.plog('API|Strategy.%s: %s' % (name, self._attr(self, name)))
        for name in ('getvalue', 'getcash', 'get_orders_open', 'getposition', 'cancel'):
            self.plog('API|broker.%s: %s' % (name, self._attr(self.broker, name)))

        # ---- indicators (constructed here, values printed at bar 60)
        self.inds = {}
        builders = [
            ('ATR14', lambda: bt.ind.ATR(self.data, period=14)),
            ('EMA20', lambda: bt.ind.EMA(self.data.close, period=20)),
            ('SMA20', lambda: bt.ind.SMA(self.data.close, period=20)),
            ('Highest20', lambda: bt.ind.Highest(self.data.high, period=20)),
            ('Lowest20', lambda: bt.ind.Lowest(self.data.low, period=20)),
            ('RSI14', lambda: bt.ind.RSI(self.data.close, period=14)),
            ('TrueRange', lambda: bt.ind.TrueRange(self.data)),
            ('MACD', lambda: bt.ind.MACD(self.data.close)),
            ('MACDHisto', lambda: bt.ind.MACDHisto(self.data.close)),
        ]
        for name, fn in builders:
            try:
                self.inds[name] = fn()
                self.plog('IND|%s: constructed OK' % name)
            except Exception as e:
                self.plog('IND|%s: FAIL %r' % (name, e))
        if 'MACD' in self.inds:
            m = self.inds['MACD']
            for ln in ('macd', 'signal', 'histo'):
                self.plog('IND|MACD.%s exposed: %s' % (ln, self._attr(m.lines, ln)))

        # ---- test plan state machine
        self.tests = ['T1_MARKET', 'T2_STOP_ENTRY', 'T3_LIMIT_ENTRY', 'T4_CANCEL',
                      'T5_VALID_EXPIRY', 'T6_OCO', 'T7_BRACKET_LONG', 'T8_BRACKET_SHORT']
        self.ti = -1            # index of current test
        self.tstate = None      # dict for the current test
        self.cooldown = 3       # bars to wait before first / between tests
        self.first_value = None
        self.first_cash = None
        self.per_point = []     # value-per-point-per-unit estimates

    # ------------------------------------------------------------------ start
    def start(self):
        try:
            self.first_value = self.broker.getvalue()
            self.first_cash = self.broker.getcash()
            self.plog('BROKER|start getvalue=%s getcash=%s' % (_r(self.first_value, 2),
                                                              _r(self.first_cash, 2)))
        except Exception as e:
            self.plog('BROKER|start ERR %r' % (e,))
        if datetime is not None:
            try:
                now_utc = datetime.datetime.utcnow()
                now_loc = datetime.datetime.now()
                self.plog('CLOCK|machine now: utc=%s local=%s (only meaningful when running live)'
                          % (now_utc.strftime('%Y-%m-%d %H:%M:%S'),
                             now_loc.strftime('%Y-%m-%d %H:%M:%S')))
            except Exception as e:
                self.plog('CLOCK|ERR %r' % (e,))

    # ------------------------------------------------------------------ time
    def _track_time(self):
        dt = self._dt()
        if dt is None:
            return
        if self.bar_n <= self.p.max_bar_lines:
            try:
                raw = self.data.datetime[0]
            except Exception:
                raw = '?'
            self.plog('BAR|%d %s %s raw=%s tz=%r %s vol=%s'
                      % (self.bar_n, dt.strftime('%Y-%m-%d %H:%M:%S'), dt.strftime('%a'),
                         _r(raw, 6), getattr(dt, 'tzinfo', None), self._bar(),
                         _r(self.data.volume[0], 2)))
        if self.prev_dt is not None and datetime is not None:
            mins = (dt - self.prev_dt).total_seconds() / 60.0
            if len(self.deltas) < 200:
                self.deltas.append(mins)
                if len(self.deltas) == 50:
                    self.bar_minutes = max(set(self.deltas), key=self.deltas.count)
                    self.plog('TIME|typical bar spacing = %s min' % self.bar_minutes)
            if mins > self.p.gap_min_minutes and mins < 4 * 24 * 60:
                self._record_gap(self.prev_dt, dt, mins)
        self.prev_dt = dt

    def _record_gap(self, last_dt, next_dt, mins):
        # Assume bar stamps are bar OPEN times -> market closed at last_dt + 1 bar.
        bm = self.bar_minutes or (self.deltas and min(self.deltas)) or 0
        close_srv = last_dt + datetime.timedelta(minutes=bm)
        # Hypothesis: the break starts at 17:00 New York (gold & index CFDs).
        dst = _ny_is_dst(close_srv)
        ny_to_utc = 4 if dst else 5
        srv_hours = close_srv.hour + close_srv.minute / 60.0
        offset = srv_hours - (17 + ny_to_utc)     # server - UTC, mod 24
        while offset > 12:
            offset -= 24
        while offset <= -12:
            offset += 24
        offset = round(offset * 2) / 2.0
        key = '%+.1f(%s)' % (offset, 'NY-DST' if dst else 'NY-STD')
        self.offset_votes[key] = self.offset_votes.get(key, 0) + 1
        if len(self.gaps) < self.p.max_gap_lines:
            self.gaps.append(1)
            self.plog('GAP|last=%s %s next=%s %s gap=%.0fmin implied_close=%s '
                      'implied_server_minus_UTC=%+.1fh (if break starts 17:00 NY; NY DST=%s)'
                      % (last_dt.strftime('%Y-%m-%d %H:%M'), last_dt.strftime('%a'),
                         next_dt.strftime('%Y-%m-%d %H:%M'), next_dt.strftime('%a'), mins,
                         close_srv.strftime('%H:%M'), offset, dst))

    # ------------------------------------------------------------------ orders
    def _tag(self, order, tag):
        if order is not None:
            self.order_tag[order.ref] = tag
        return order

    def notify_order(self, order):
        tag = self.order_tag.get(order.ref, '?')
        try:
            st = order.getstatusname()
        except Exception:
            st = str(order.status)
        try:
            et = bt.Order.ExecTypes[order.exectype]
        except Exception:
            et = str(order.exectype)
        side = 'BUY' if order.isbuy() else 'SELL'
        ex = order.executed
        self.plog('ORDER|%s ref=%s %s %s status=%s created_price=%s size=%s '
                  'exec_price=%s exec_size=%s comm=%s margin=%s | bar %s %s'
                  % (tag, order.ref, side, et, st, _r(order.created.price),
                     _r(order.created.size), _r(ex.price), _r(ex.size), _r(ex.comm),
                     _r(getattr(ex, 'margin', None)),
                     self._dt().strftime('%Y-%m-%d %H:%M') if self._dt() else '?',
                     self._bar()))
        if self.tstate is not None:
            self.tstate.setdefault('events', []).append((order.ref, st))
            if order.status == order.Completed:
                self._on_fill(order, tag)

    def notify_trade(self, trade):
        try:
            self.plog('TRADE|isclosed=%s size=%s price=%s value=%s pnl=%s pnlcomm=%s '
                      'commission=%s barlen=%s'
                      % (trade.isclosed, _r(trade.size), _r(trade.price), _r(trade.value),
                         _r(trade.pnl, 4), _r(trade.pnlcomm, 4), _r(trade.commission, 4),
                         getattr(trade, 'barlen', '?')))
            if trade.isclosed and self.tstate is not None:
                s = self.tstate
                if s.get('entry_px') is not None and s.get('exit_px') is not None:
                    move = (s['exit_px'] - s['entry_px']) * s['dir']
                    if move != 0:
                        vpp = trade.pnl / (move * abs(s['size']))
                        self.per_point.append(vpp)
                        self.plog('MEASURE|%s value per 1.0 price move per 1 size unit = %s '
                                  '(pnl %s / (move %s x size %s))'
                                  % (self.tests[self.ti], _r(vpp, 6), _r(trade.pnl, 4),
                                     _r(move), s['size']))
        except Exception as e:
            self.plog('TRADE|ERR %r' % (e,))

    def notify_cashvalue(self, cash, value):
        # Only log a handful, to keep the log short.
        self._cv_calls = getattr(self, '_cv_calls', 0) + 1
        if self._cv_calls <= 3:
            self.plog('CASHVALUE|bar %d cash=%s value=%s' % (self.bar_n, _r(cash, 2), _r(value, 2)))

    # Classify how an order was filled relative to its trigger and the bar.
    def _classify_fill(self, order):
        px = order.executed.price
        trig = order.created.price
        o, h, l, c = (self.data.open[0], self.data.high[0], self.data.low[0],
                      self.data.close[0])
        tol = abs(px) * 1e-7 + 1e-9
        parts = []
        if trig is not None and abs(px - trig) <= tol:
            parts.append('AT_TRIGGER_PRICE')
        if abs(px - o) <= tol:
            parts.append('AT_BAR_OPEN')
        if abs(px - c) <= tol:
            parts.append('AT_BAR_CLOSE')
        if not (l - tol <= px <= h + tol):
            parts.append('OUTSIDE_BAR_RANGE(!)')
        return '+'.join(parts) or 'OTHER(px=%s trig=%s)' % (_r(px), _r(trig))

    def _on_fill(self, order, tag):
        s = self.tstate
        role = s.get('roles', {}).get(order.ref, 'entry')
        how = self._classify_fill(order)
        self.plog('FILL|%s role=%s how=%s' % (tag, role, how))
        if role == 'entry':
            s['entry_px'] = order.executed.price
            s['size'] = order.executed.size
            s['dir'] = 1 if order.isbuy() else -1
            # notifications arrive before next() increments bar_n
            s['fill_bar'] = self.bar_n + 1
            s['entry_how'] = how
            # Hedging protection: if this was one leg of an OCO pair, check the
            # other leg and cancel it ourselves if the platform did not.
            other = s.get('oco_partner', {}).get(order.ref)
            if other is not None:
                if other.status in (other.Canceled,):
                    s['oco_native'] = True
                else:
                    s['oco_native'] = False
                    self.plog('SAFETY|OCO partner ref=%s still %s -> cancelling manually'
                              % (other.ref, other.getstatusname()))
                    self.cancel(other)
        elif role in ('stop', 'target', 'exit'):
            s['exit_px'] = order.executed.price
            s['exit_role'] = role
            s['exit_how'] = how

    def _open_orders_alive(self):
        alive = []
        for o in self.tstate.get('orders', []):
            if o.status in (o.Created, o.Submitted, o.Accepted, o.Partial):
                alive.append(o)
        return alive

    def _cancel_all(self):
        for o in self._open_orders_alive():
            self.cancel(o)

    # ------------------------------------------------------------------ tests
    def _start_test(self):
        name = self.tests[self.ti]
        c = self.data.close[0]
        s = {'name': name, 'start_bar': self.bar_n, 'orders': [], 'roles': {},
             'entry_px': None, 'exit_px': None, 'oco_partner': {}}
        self.tstate = s
        self.plog('TEST|START %s at %s close=%s value=%s cash=%s'
                  % (name, self._dt().strftime('%Y-%m-%d %H:%M'), _r(c),
                     _r(self.broker.getvalue(), 2), _r(self.broker.getcash(), 2)))
        try:
            if name == 'T1_MARKET':
                o = self._tag(self.buy(size=self.p.probe_size), name)
                s['orders'] = [o]
                s['created_close'] = c
            elif name == 'T2_STOP_ENTRY':
                p = c * (1 + self.p.move_pct)
                o = self._tag(self.buy(size=self.p.probe_size, exectype=bt.Order.Stop, price=p), name)
                s['orders'] = [o]
            elif name == 'T3_LIMIT_ENTRY':
                p = c * (1 - self.p.move_pct)
                o = self._tag(self.buy(size=self.p.probe_size, exectype=bt.Order.Limit, price=p), name)
                s['orders'] = [o]
            elif name == 'T4_CANCEL':
                p = c * 0.95
                o = self._tag(self.buy(size=self.p.probe_size, exectype=bt.Order.Limit, price=p), name)
                s['orders'] = [o]
            elif name == 'T5_VALID_EXPIRY':
                p = c * 0.95
                bm = self.bar_minutes or 5
                o = self._tag(self.buy(size=self.p.probe_size, exectype=bt.Order.Limit, price=p,
                                       valid=datetime.timedelta(minutes=3 * bm)), name)
                s['orders'] = [o]
                s['valid_minutes'] = 3 * bm
            elif name == 'T6_OCO':
                o1 = self._tag(self.buy(size=self.p.probe_size, exectype=bt.Order.Stop,
                                        price=c * (1 + self.p.move_pct)), name + '_BUYSTOP')
                o2 = self._tag(self.sell(size=self.p.probe_size, exectype=bt.Order.Stop,
                                         price=c * (1 - self.p.move_pct), oco=o1), name + '_SELLSTOP')
                s['orders'] = [o1, o2]
                s['oco_partner'] = {o1.ref: o2, o2.ref: o1}
            elif name in ('T7_BRACKET_LONG', 'T8_BRACKET_SHORT'):
                if name == 'T7_BRACKET_LONG':
                    os_ = self.buy_bracket(size=self.p.probe_size, exectype=bt.Order.Market,
                                           stopprice=c * (1 - self.p.bracket_pct),
                                           limitprice=c * (1 + self.p.bracket_pct))
                else:
                    os_ = self.sell_bracket(size=self.p.probe_size, exectype=bt.Order.Market,
                                            stopprice=c * (1 + self.p.bracket_pct),
                                            limitprice=c * (1 - self.p.bracket_pct))
                os_ = list(os_)
                self.plog('TEST|%s bracket returned %d orders' % (name, len(os_)))
                for o, role in zip(os_, ('entry', 'stop', 'target')):
                    self._tag(o, '%s_%s' % (name, role.upper()))
                    s['roles'][o.ref] = role
                s['orders'] = os_
        except Exception as e:
            self.results[name] = 'EXCEPTION placing orders: %r' % (e,)
            self.plog('TEST|%s EXCEPTION %r' % (name, e))
            self._end_test()

    def _end_test(self):
        s = self.tstate
        self.plog('TEST|END %s value=%s cash=%s position=%s'
                  % (s['name'], _r(self.broker.getvalue(), 2), _r(self.broker.getcash(), 2),
                     self.position.size))
        self.tstate = None
        self.cooldown = 3

    def _run_test_bar(self):
        s = self.tstate
        name = s['name']
        age = self.bar_n - s['start_bar']
        pos = self.position.size

        if name == 'T1_MARKET':
            if s['entry_px'] is not None:
                k = self.bar_n - s['fill_bar']
                v, cash, c = self.broker.getvalue(), self.broker.getcash(), self.data.close[0]
                if k == 0:
                    s['v0'], s['c0'], s['cash0'] = v, c, cash
                    if 'created_close' in s:
                        how = ('NEXT_BAR_OPEN' if 'AT_BAR_OPEN' in s['entry_how'] else
                               s['entry_how'])
                        self.notes.append('market order: created at close %s, filled %s (%s)'
                                          % (_r(s['created_close']), _r(s['entry_px']), how))
                else:
                    dv = v - s['v0']
                    dc = (c - s['c0']) * s['size']
                    est = (dv / dc) if dc != 0 else None
                    s.setdefault('float_est', [])
                    if est is not None and pos != 0:
                        s['float_est'].append(est)
                    self.plog('FLOAT|bar+%d close=%s value=%s cash=%s pos=%s pos.price=%s '
                              'dValue=%s dClose*size=%s ratio=%s'
                              % (k, _r(c), _r(v, 4), _r(cash, 4), pos,
                                 _r(self.position.price), _r(dv, 4), _r(dc, 6),
                                 _r(est, 4) if est is not None else 'n/a'))
                if k >= self.p.hold_bars and pos != 0 and not s.get('closing'):
                    s['closing'] = True
                    o = self._tag(self.close(), name + '_EXIT')
                    s['roles'][o.ref] = 'exit'
                    s['orders'].append(o)
                if s.get('closing') and pos == 0:
                    est = s.get('float_est') or []
                    if est:
                        avg = sum(est) / len(est)
                        self.results[name] = ('filled; getvalue moves with open P&L: ratio '
                                              'dValue/(dPrice*size) avg=%s over %d bars'
                                              % (_r(avg, 4), len(est)))
                    else:
                        self.results[name] = 'filled; price never moved, no ratio'
                    self._end_test()
            elif age > 10:
                self.results[name] = 'NOT FILLED after 10 bars (rejected? see ORDER lines)'
                self._cancel_all()
                self._end_test()
            return

        if name in ('T2_STOP_ENTRY', 'T3_LIMIT_ENTRY'):
            if s['entry_px'] is not None:
                if pos != 0 and not s.get('closing') and self.bar_n - s['fill_bar'] >= 2:
                    s['closing'] = True
                    o = self._tag(self.close(), name + '_EXIT')
                    s['roles'][o.ref] = 'exit'
                    s['orders'].append(o)
                if s.get('closing') and pos == 0:
                    self.results[name] = 'FILLED, fill=%s' % s['entry_how']
                    self._end_test()
            elif age > 60:
                self._cancel_all()
                self.results[name] = 'not triggered in 60 bars, cancelled (inconclusive)'
                self._end_test()
            return

        if name == 'T4_CANCEL':
            o = s['orders'][0]
            if age == 3:
                self.cancel(o)
            if age >= 6:
                self.results[name] = 'order status after self.cancel(): %s' % o.getstatusname()
                if o.status not in (o.Canceled,):
                    self._cancel_all()
                self._end_test()
            return

        if name == 'T5_VALID_EXPIRY':
            o = s['orders'][0]
            if o.status == o.Expired:
                self.results[name] = 'EXPIRED after %d bars (valid=%d min) -> valid= works' % (
                    age, s['valid_minutes'])
                self._end_test()
            elif age >= 10:
                self.results[name] = ('NOT expired after 10 bars (status %s) -> valid= NOT '
                                      'honoured; cancelled manually' % o.getstatusname())
                self._cancel_all()
                self._end_test()
            return

        if name == 'T6_OCO':
            if s['entry_px'] is not None:
                if pos != 0 and not s.get('closing') and self.bar_n - s['fill_bar'] >= 2:
                    s['closing'] = True
                    o = self._tag(self.close(), name + '_EXIT')
                    s['roles'][o.ref] = 'exit'
                    s['orders'].append(o)
                if s.get('closing') and pos == 0 and not self._open_orders_alive():
                    sts = ', '.join('ref%s=%s' % (o.ref, o.getstatusname())
                                    for o in s['orders'][:2])
                    self.results[name] = ('one leg filled (%s); other leg auto-cancelled by '
                                          'platform: %s; final: %s'
                                          % (s['entry_how'], s.get('oco_native'), sts))
                    self._end_test()
            elif age > 100:
                self._cancel_all()
                self.results[name] = 'neither leg triggered in 100 bars (inconclusive)'
                self._end_test()
            return

        if name in ('T7_BRACKET_LONG', 'T8_BRACKET_SHORT'):
            if s.get('exit_px') is not None and pos == 0:
                if self._open_orders_alive() and age < 400:
                    # give the platform one more bar to cancel the sibling
                    if s.get('sib_wait', 0) >= 1:
                        self.plog('SAFETY|bracket sibling still open -> cancelling manually')
                        s['sib_manual'] = True
                        self._cancel_all()
                    s['sib_wait'] = s.get('sib_wait', 0) + 1
                    return
                sts = ', '.join('%s=%s' % (s['roles'].get(o.ref), o.getstatusname())
                                for o in s['orders'])
                self.results[name] = ('entry %s; exit by %s, fill=%s; sibling auto-cancel=%s; '
                                      'final: %s' % (s.get('entry_how'), s.get('exit_role'),
                                                     s.get('exit_how'),
                                                     not s.get('sib_manual', False), sts))
                self._end_test()
            elif s['entry_px'] is None and age > 10:
                self.results[name] = 'entry NOT filled after 10 bars (see ORDER lines)'
                self._cancel_all()
                self._end_test()
            elif age > 400:
                self.results[name] = 'neither stop nor target hit in 400 bars; closed manually'
                self._cancel_all()
                if pos != 0:
                    self.close()
                self._end_test()
            return

    # ------------------------------------------------------------------ next
    def prenext(self):
        # Called while indicators are still warming up: only track timestamps.
        self.bar_n += 1
        self._track_time()

    def next(self):
        self.bar_n += 1
        self._track_time()

        if not getattr(self, '_first_next_logged', False):
            self._first_next_logged = True
            self.plog('TIME|first next() call at bar %d (earlier bars = indicator warm-up)'
                      % self.bar_n)
        if self.bar_n == 60:
            for name, ind in self.inds.items():
                try:
                    vals = ['%s=%s' % (ln, _r(getattr(ind.lines, ln)[0]))
                            for ln in ind.lines.getlinealiases()]
                    self.plog('IND|%s at bar 60: %s' % (name, ' '.join(vals)))
                except Exception as e:
                    self.plog('IND|%s value ERR %r' % (name, e))

        if self.tstate is not None:
            try:
                self._run_test_bar()
            except Exception as e:
                name = self.tstate['name'] if self.tstate else '?'
                self.results[name] = 'EXCEPTION during test: %r' % (e,)
                self.plog('TEST|%s EXCEPTION %r' % (name, e))
                try:
                    self._cancel_all()
                    if self.position.size != 0:
                        self.close()
                except Exception:
                    pass
                self.tstate = None
                self.cooldown = 3
            return

        if self.cooldown > 0:
            self.cooldown -= 1
            return
        if self.position.size != 0:
            self.plog('SAFETY|unexpected open position %s -> closing' % self.position.size)
            self.close()
            self.cooldown = 3
            return
        if self.ti + 1 < len(self.tests):
            self.ti += 1
            self._start_test()

    # ------------------------------------------------------------------ stop
    def stop(self):
        P = self.plog
        P('SUMMARY|================ PROBE SUMMARY ================')
        P('SUMMARY|backtrader=%s python=%s' % (getattr(bt, '__version__', '?'),
                                               sys.version.split()[0] if sys else '?'))
        P('SUMMARY|imports: %s' % ', '.join('%s=%s' % (k, v.split()[0])
                                             for k, v in sorted(IMPORTS.items())))
        P('SUMMARY|feeds=%d  bars=%d  typical_bar_min=%s' % (len(self.datas), self.bar_n,
                                                            self.bar_minutes))
        P('SUMMARY|start value=%s end value=%s end cash=%s'
          % (_r(self.first_value, 2), _r(self.broker.getvalue(), 2),
             _r(self.broker.getcash(), 2)))
        for t in self.tests:
            P('SUMMARY|%-18s %s' % (t, self.results.get(t, 'NOT RUN')))
        if self.per_point:
            P('SUMMARY|value per 1.0 price move per 1 size unit (from closed trades): %s'
              % ', '.join(str(_r(x, 6)) for x in self.per_point))
        for n in self.notes:
            P('SUMMARY|note: %s' % n)
        if self.offset_votes:
            votes = sorted(self.offset_votes.items(), key=lambda kv: -kv[1])
            P('SUMMARY|implied server-minus-UTC offset votes (assumes daily/weekly break at '
              '17:00 NY): %s' % ', '.join('%s x%d' % kv for kv in votes))
        else:
            P('SUMMARY|no session gaps seen (use a longer date range)')
        P('SUMMARY|log lines printed: %d' % (self._lines_logged + 1))
        P('SUMMARY|================ END SUMMARY ==================')
