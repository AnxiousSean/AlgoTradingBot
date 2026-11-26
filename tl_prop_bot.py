# -*- coding: utf-8 -*-
"""
TL PROP BOT - TradeLocker Studio bot for a Goat Funded Trader 2-Step evaluation
==============================================================================

STATUS: Stage 1. This file currently contains the SETTINGS block and the
PropRiskGuard (the safety layer). The trading strategies (RSI2 and ORB) are
added in Stage 2, once the Stage 0 probe has shown what Studio supports.

HOW THE FILE IS ORGANISED
    1. SETTINGS       - the only part you normally edit
    2. Time helpers   - converts the data's clock to New York time
    3. PropRiskGuard  - enforces every prop-firm rule BEFORE and DURING trades
    4. (Stage 2) Strategy classes

Everything is plain Python plus backtrader, so you can show the source to the
firm. It has no martingale, grid, recovery, averaging down, hedging or HFT,
and it never raises lot size after a loss.
"""
import math
import datetime as _dt

import backtrader as bt  # noqa: F401  (used by the strategy section in Stage 2)


# =============================================================================
# 1. SETTINGS - edit these values. Percentages are written as percent (2.5 = 2.5%).
# =============================================================================
SETTINGS = dict(
    # ---- account -----------------------------------------------------------
    INITIAL_BALANCE=5000.0,          # starting balance of the evaluation
    STEP_TARGET_PCT=8.0,             # 8.0 for Step 1, 6.0 for Step 2
    USE_TARGET_LOCK=True,            # stop trading once the target + buffer is reached
    TARGET_BUFFER_PCT=0.5,           # extra cushion above the target before locking

    # ---- firm limits (only used for warnings, never loosen these) ---------
    FIRM_DAILY_DD_PCT=4.0,           # firm daily drawdown (resets 5 PM New York)
    FIRM_MAX_LOSS_PCT=10.0,          # firm static max loss: equity must stay above 4,500

    # ---- the bot's own, tighter limits -------------------------------------
    INTERNAL_DAILY_STOP_PCT=2.5,     # flatten and stop for the day at -2.5%
    INTERNAL_TOTAL_STOP_PCT=7.0,     # flatten and stop for good at -7% from start
    RISK_PER_TRADE_PCT=0.5,          # risk per trade, % of INITIAL balance (fixed $)
    MAX_OPEN_POSITIONS=1,
    MAX_ENTRIES_PER_DAY=3,
    STOP_SLIPPAGE_BUFFER=1.5,        # assume a stop may lose 1.5x its planned amount
                                     # when checking room left before the daily/total stop
    NO_LOT_INCREASE_AFTER_LOSS=True, # after a losing trade the next lot size can't be larger

    # ---- instrument (read these from TradeLocker's instrument specs) ------
    SYMBOL="NAS100",                 # instrument name exactly as in TradeLocker
    VALUE_PER_POINT_PER_LOT=1.0,     # account currency gained per 1.0 price move per 1 lot
    MIN_LOT=0.01,
    LOT_STEP=0.01,
    MAX_LOT=5.0,                     # hard ceiling on any single order
    LEVERAGE=20.0,                   # instrument leverage (margin = notional / leverage)
    MARGIN_CAP_PCT=30.0,             # margin used must stay under this % of equity (firm: 80%)

    # ---- time --------------------------------------------------------------
    DATA_TIMEZONE="UTC",             # clock of the bar timestamps: "UTC", "NY", or a fixed
                                     # number of hours from UTC such as 2 or 3
    MIN_HOLD_SECONDS=120,            # never close a trade voluntarily before 2 minutes

    # ---- weekend rules (New York time) ------------------------------------
    FRIDAY_CLOSE_NY="17:00",         # when the market closes on Friday
    FRIDAY_NO_OPEN_HOURS=3,          # no new trades this many hours before Friday close
    FLATTEN_BEFORE_WEEKEND=True,
    WEEKEND_FLATTEN_NY="16:45",      # Friday time at which open trades are closed
    WEEK_OPEN_NY="18:00",            # Sunday time the market re-opens
    MONDAY_NO_OPEN_HOURS=3,          # no new trades in the first hours of the week
                                     # (blocks both Sun 18:00+3h and Mon 00:00+3h NY)

    # ---- news blackout (New York time, "YYYY-MM-DD HH:MM") ----------------
    NEWS_EVENTS_NY=[
        # "2026-12-04 08:30",        # example: Non-Farm Payrolls
    ],
    NEWS_BLOCK_BEFORE_MIN=20,        # no new trades from 20 min before ...
    NEWS_BLOCK_AFTER_MIN=10,         # ... until 10 min after each event
    NEWS_NO_CLOSE_WINDOW_MIN=6,      # no voluntary closes within +-6 min (firm rule: 5)
    NEWS_FLATTEN_BEFORE_MIN=10,      # close open trades 10 min before an event (0 = off)
)


# =============================================================================
# 2. TIME HELPERS - New York time without needing extra libraries
# =============================================================================
def _nth_sunday(year, month, n):
    d = _dt.date(year, month, 1)
    first = d + _dt.timedelta(days=(6 - d.weekday()) % 7)
    return first + _dt.timedelta(days=7 * (n - 1))


def ny_offset_hours(utc_dt):
    """New York's offset from UTC (-4 summer, -5 winter), US rules since 2007."""
    y = utc_dt.year
    dst_start = _dt.datetime.combine(_nth_sunday(y, 3, 2), _dt.time(7, 0))   # 2:00 EST
    dst_end = _dt.datetime.combine(_nth_sunday(y, 11, 1), _dt.time(6, 0))    # 2:00 EDT
    return -4 if dst_start <= utc_dt < dst_end else -5


def utc_to_ny(utc_dt):
    return utc_dt + _dt.timedelta(hours=ny_offset_hours(utc_dt))


def to_utc(dt, data_tz):
    """Convert a bar timestamp in the data's clock to naive UTC."""
    if dt.tzinfo is not None:
        off = dt.utcoffset() or _dt.timedelta(0)
        return (dt - off).replace(tzinfo=None)
    if data_tz in ("UTC", "utc", 0, None):
        return dt
    if data_tz in ("NY", "ny", "America/New_York"):
        guess = dt + _dt.timedelta(hours=5)
        return dt - _dt.timedelta(hours=ny_offset_hours(guess))
    return dt - _dt.timedelta(hours=float(data_tz))


def parse_hhmm(s):
    h, m = s.split(":")
    return _dt.time(int(h), int(m))


def trading_day_of(ny_dt):
    """The firm's trading day: it starts at 17:00 New York, so 17:00 Monday
    already belongs to Tuesday."""
    return (ny_dt + _dt.timedelta(hours=7)).date()


# =============================================================================
# 3. PROP RISK GUARD
# =============================================================================
class PropRiskGuard(object):
    """Keeps the account inside the prop-firm rules.

    The strategy calls it like this:
        guard.update(now, equity, balance, has_position)  -> flatten reason or None
        guard.can_open(now, open_positions)               -> (True/False, reason)
        guard.size_position(entry, stop, equity)          -> (lots, explanation)
        guard.register_entry(now, direction, lots, entry, stop)
        guard.exit_allowed(now, forced)                   -> (True/False, reason)
        guard.register_exit(now, pnl)                     -> R multiple
    `now` is the bar timestamp in the data's own clock (see DATA_TIMEZONE).
    """

    FORCED_REASONS = ("TOTAL_STOP", "DAILY_STOP")   # may close before min hold time

    def __init__(self, settings=None, log=None, **overrides):
        s = dict(SETTINGS)
        if settings:
            s.update(settings)
        s.update(overrides)
        self.s = s
        self.log = log or (lambda msg: None)

        self.initial = float(s["INITIAL_BALANCE"])
        self.firm_floor = self.initial * (1 - s["FIRM_MAX_LOSS_PCT"] / 100.0)          # 4,500
        self.total_floor = self.initial * (1 - s["INTERNAL_TOTAL_STOP_PCT"] / 100.0)   # 4,650
        self.target_level = self.initial * (1 + (s["STEP_TARGET_PCT"] + s["TARGET_BUFFER_PCT"]) / 100.0)

        self.news_ny = sorted(_dt.datetime.strptime(x, "%Y-%m-%d %H:%M") for x in s["NEWS_EVENTS_NY"])
        self.friday_close = parse_hhmm(s["FRIDAY_CLOSE_NY"])
        self.weekend_flatten = parse_hhmm(s["WEEKEND_FLATTEN_NY"])
        self.week_open = parse_hhmm(s["WEEK_OPEN_NY"])

        self.day = None
        self.day_start_ref = self.initial
        self.entries_today = 0
        self.day_halted = False
        self.total_halted = False
        self.target_locked = False
        self.firm_breach = None          # text if a FIRM limit was ever crossed
        self.trading_days = set()
        self.open_trade = None           # dict with entry info
        self.last_lots = None
        self.last_was_loss = False
        self.worst_day_pct = 0.0
        self.last_equity = self.initial

    # ---------------------------------------------------------------- helpers
    def ny(self, now):
        return utc_to_ny(to_utc(now, self.s["DATA_TIMEZONE"]))

    def _day_loss_allowed(self, pct):
        """Money the day may lose. Uses the SMALLER of initial balance and
        start-of-day reference, so it is never looser than either rule."""
        return pct / 100.0 * min(self.initial, self.day_start_ref)

    @property
    def daily_floor(self):
        return self.day_start_ref - self._day_loss_allowed(self.s["INTERNAL_DAILY_STOP_PCT"])

    @property
    def firm_daily_floor(self):
        return self.day_start_ref - self._day_loss_allowed(self.s["FIRM_DAILY_DD_PCT"])

    def day_pnl(self, equity):
        return equity - self.day_start_ref

    # ------------------------------------------------------- per-bar update
    def update(self, now, equity, balance=None, has_position=False):
        """Call on every bar. Returns a reason string if open trades must be
        closed now, otherwise None."""
        balance = equity if balance is None else balance
        self.last_equity = equity
        ny = self.ny(now)
        day = trading_day_of(ny)
        if day != self.day:
            self._new_day(day, equity, balance)

        dd_pct = (equity - self.day_start_ref) / self.initial * 100.0
        self.worst_day_pct = min(self.worst_day_pct, dd_pct)

        # Firm limits (should never trigger: internal limits are tighter)
        if self.firm_breach is None:
            if equity <= self.firm_floor:
                self.firm_breach = "FIRM MAX LOSS crossed: equity {:.2f} <= {:.2f}".format(equity, self.firm_floor)
            elif equity <= self.firm_daily_floor:
                self.firm_breach = "FIRM DAILY DD crossed: equity {:.2f} <= {:.2f}".format(equity, self.firm_daily_floor)
            if self.firm_breach:
                self.log("!!! " + self.firm_breach)

        if not self.total_halted and equity <= self.total_floor:
            self.total_halted = True
            self.log("GUARD TOTAL_STOP: equity {:.2f} <= {:.2f}. Trading stopped for good.".format(equity, self.total_floor))
        if not self.day_halted and equity <= self.daily_floor:
            self.day_halted = True
            self.log("GUARD DAILY_STOP: equity {:.2f} <= {:.2f}. No more trades today.".format(equity, self.daily_floor))
        if self.s["USE_TARGET_LOCK"] and not self.target_locked and equity >= self.target_level:
            self.target_locked = True
            self.log("GUARD TARGET_LOCK: equity {:.2f} >= {:.2f}. Trading stopped. Trading days so far: {} (need 3).".format(
                equity, self.target_level, len(self.trading_days)))

        if not has_position:
            return None
        if self.total_halted:
            return "TOTAL_STOP"
        if self.day_halted:
            return "DAILY_STOP"
        if self.target_locked:
            return "TARGET_LOCK"
        if self.s["FLATTEN_BEFORE_WEEKEND"] and self._weekend_flatten_time(ny):
            return "WEEKEND"
        if self._news_flatten_time(ny):
            return "NEWS_FLATTEN"
        return None

    def _new_day(self, day, equity, balance):
        if self.day is not None:
            self.log("GUARD NEW_DAY {}: previous day P&L {:.2f}".format(day, equity - self.day_start_ref))
        self.day = day
        # higher of balance and equity at 5 PM NY = stricter floor
        self.day_start_ref = max(balance, equity)
        self.entries_today = 0
        self.day_halted = False

    # ---------------------------------------------------------- time rules
    def _weekend_flatten_time(self, ny):
        wd = ny.weekday()   # Mon=0 ... Fri=4, Sat=5, Sun=6
        if wd == 4 and ny.time() >= self.weekend_flatten:
            return True
        if wd == 5:
            return True
        if wd == 6 and ny.time() < self.week_open:
            return True
        return False

    def _weekend_no_open(self, ny):
        wd, t = ny.weekday(), ny.time()
        fri_cutoff = (_dt.datetime.combine(ny.date(), self.friday_close)
                      - _dt.timedelta(hours=self.s["FRIDAY_NO_OPEN_HOURS"])).time()
        if wd == 4 and t >= fri_cutoff:
            return "FRIDAY_LAST_HOURS"
        if wd == 5:
            return "WEEKEND"
        if wd == 6:
            open_end = (_dt.datetime.combine(ny.date(), self.week_open)
                        + _dt.timedelta(hours=self.s["MONDAY_NO_OPEN_HOURS"]))
            if ny < open_end:
                return "WEEK_OPEN_FIRST_HOURS"
        if wd == 0 and t < _dt.time(min(23, int(self.s["MONDAY_NO_OPEN_HOURS"])), 0):
            return "MONDAY_FIRST_HOURS"
        return None

    def _news_near(self, ny, before_min, after_min):
        for ev in self.news_ny:
            if ev - _dt.timedelta(minutes=before_min) <= ny <= ev + _dt.timedelta(minutes=after_min):
                return ev
        return None

    def _news_flatten_time(self, ny):
        m = self.s["NEWS_FLATTEN_BEFORE_MIN"]
        if m <= 0:
            return False
        for ev in self.news_ny:
            if ev - _dt.timedelta(minutes=m) <= ny < ev:
                return True
        return False

    # ------------------------------------------------------------ entries
    def can_open(self, now, open_positions=0):
        """(True, "OK") or (False, reason)."""
        if self.total_halted:
            return False, "TOTAL_STOP"
        if self.target_locked:
            return False, "TARGET_LOCK"
        if self.day_halted:
            return False, "DAILY_STOP"
        if open_positions >= self.s["MAX_OPEN_POSITIONS"]:
            return False, "MAX_OPEN_POSITIONS"
        if self.entries_today >= self.s["MAX_ENTRIES_PER_DAY"]:
            return False, "MAX_ENTRIES_PER_DAY"
        ny = self.ny(now)
        wk = self._weekend_no_open(ny)
        if wk:
            return False, wk
        if self.s["FLATTEN_BEFORE_WEEKEND"] and self._weekend_flatten_time(ny):
            return False, "WEEKEND"
        before = max(self.s["NEWS_BLOCK_BEFORE_MIN"],
                     self.s["NEWS_FLATTEN_BEFORE_MIN"] + self.s["MIN_HOLD_SECONDS"] / 60.0)
        ev = self._news_near(ny, before, self.s["NEWS_BLOCK_AFTER_MIN"])
        if ev is not None:
            return False, "NEWS_BLACKOUT {}".format(ev.strftime("%Y-%m-%d %H:%M"))
        return True, "OK"

    def round_lots(self, lots):
        step = self.s["LOT_STEP"]
        n = math.floor(round(lots / step, 9))
        decimals = max(0, -int(math.floor(math.log10(step)))) if step < 1 else 0
        return round(n * step, decimals + 2)

    def size_position(self, entry, stop, equity):
        """Lots for a trade, or 0 with the reason. Never more than:
        - fixed risk (RISK_PER_TRADE_PCT of INITIAL balance),
        - what fits before the daily and total internal stops,
        - the margin cap, MAX_LOT, and (after a loss) the previous lot size."""
        s = self.s
        dist = abs(float(entry) - float(stop))
        vpp = float(s["VALUE_PER_POINT_PER_LOT"])
        if dist <= 0 or vpp <= 0:
            return 0.0, "invalid stop distance"
        risk_amt = s["RISK_PER_TRADE_PCT"] / 100.0 * self.initial
        room = min(equity - self.daily_floor, equity - self.total_floor)
        if room <= 0:
            return 0.0, "no room left before internal stop"
        allowed_loss = min(risk_amt, room / s["STOP_SLIPPAGE_BUFFER"])
        by_risk = allowed_loss / (dist * vpp)
        margin_per_lot = float(entry) * vpp / float(s["LEVERAGE"])
        by_margin = (s["MARGIN_CAP_PCT"] / 100.0 * equity) / margin_per_lot if margin_per_lot > 0 else by_risk
        caps = [("risk", by_risk), ("margin", by_margin), ("max_lot", float(s["MAX_LOT"]))]
        if s["NO_LOT_INCREASE_AFTER_LOSS"] and self.last_was_loss and self.last_lots:
            caps.append(("no_increase_after_loss", self.last_lots))
        limit_name, raw = min(caps, key=lambda kv: kv[1])
        lots = self.round_lots(raw)
        why = "risk${:.2f} dist={:.2f} raw={:.4f} limited_by={} -> {} lots".format(
            allowed_loss, dist, raw, limit_name, lots)
        if lots < s["MIN_LOT"] - 1e-12:
            return 0.0, "below min lot ({})".format(why)
        return lots, why

    def margin_used(self, lots, price):
        return lots * price * self.s["VALUE_PER_POINT_PER_LOT"] / self.s["LEVERAGE"]

    def register_entry(self, now, direction, lots, entry, stop):
        risk = abs(entry - stop) * lots * self.s["VALUE_PER_POINT_PER_LOT"]
        self.open_trade = dict(time=to_utc(now, self.s["DATA_TIMEZONE"]), direction=direction,
                               lots=lots, entry=entry, stop=stop, risk=risk)
        self.entries_today += 1
        self.trading_days.add(self.day if self.day is not None else trading_day_of(self.ny(now)))
        self.last_lots = lots

    # -------------------------------------------------------------- exits
    def held_seconds(self, now):
        if not self.open_trade:
            return None
        return (to_utc(now, self.s["DATA_TIMEZONE"]) - self.open_trade["time"]).total_seconds()

    def exit_allowed(self, now, forced=False):
        """Voluntary exits wait for the minimum hold time and avoid the news
        window. Forced exits (daily/total stop) are always allowed: a losing
        trade closed early does not lose any profit."""
        if forced:
            return True, "FORCED"
        held = self.held_seconds(now)
        if held is not None and held < self.s["MIN_HOLD_SECONDS"]:
            return False, "MIN_HOLD ({:.0f}s < {}s)".format(held, self.s["MIN_HOLD_SECONDS"])
        w = self.s["NEWS_NO_CLOSE_WINDOW_MIN"]
        ev = self._news_near(self.ny(now), w, w)
        if ev is not None:
            return False, "NEWS_NO_CLOSE {}".format(ev.strftime("%H:%M"))
        return True, "OK"

    def register_exit(self, now, pnl):
        """Returns the R multiple of the closed trade."""
        r = None
        if self.open_trade and self.open_trade["risk"] > 0:
            r = pnl / self.open_trade["risk"]
        self.last_was_loss = pnl < 0
        self.open_trade = None
        return r

    # ------------------------------------------------------------ logging
    def state_str(self, equity=None):
        eq = self.last_equity if equity is None else equity
        flags = [n for n, on in (("DAY_HALT", self.day_halted), ("TOTAL_HALT", self.total_halted),
                                 ("TARGET_LOCK", self.target_locked)) if on]
        return ("day={} dayStart={:.2f} dayPnL={:+.2f} dailyRoom={:.2f} totalRoom={:.2f} "
                "entries={}/{} tradingDays={} flags={}").format(
            self.day, self.day_start_ref, eq - self.day_start_ref, eq - self.daily_floor,
            eq - self.total_floor, self.entries_today, self.s["MAX_ENTRIES_PER_DAY"],
            len(self.trading_days), ",".join(flags) or "none")


# =============================================================================
# 4. STRATEGIES - added in Stage 2 (after the Studio probe results are in)
# =============================================================================
