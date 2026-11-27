# -*- coding: utf-8 -*-
"""
TL PROP BOT - TradeLocker Studio bot for a Goat Funded Trader 2-Step evaluation
==============================================================================

STATUS: Stage 2. Settings, PropRiskGuard and both strategies (RSI2, ORB).
Not yet validated: see research/ reports before trading it anywhere.

HOW TO USE IN STUDIO
    Copy this whole file from a plain-text editor (Notepad/TextEdit) into an
    EMPTY Studio editor. The last line must be the "END OF FILE" comment.
    Choose the strategy with STRATEGY below (or in Studio's parameter inputs).

HOW THE FILE IS ORGANISED
    1. SETTINGS       - the only part you normally edit
    2. Time helpers   - converts the data's clock to New York time
    3. PropRiskGuard  - enforces every prop-firm rule BEFORE and DURING trades
    4. Small helpers (tick rounding, percentile, daily ATR, seeded coin)
    5. TLPropBot      - the Backtrader strategy Studio runs

Everything is plain Python plus backtrader, so you can show the source to the
firm. It has no martingale, grid, recovery, averaging down, hedging or HFT,
and it never raises lot size after a loss.
"""
import math
import datetime as dtm

import backtrader as bt


# =============================================================================
# 1. SETTINGS - edit these values. Percentages are written as percent (2.5 = 2.5%).
# =============================================================================
SETTINGS = dict(
    # ---- which strategy -----------------------------------------------------
    STRATEGY="RSI2",                 # "RSI2" (15m or 1H bars) or "ORB" (5m bars)

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
    # Defaults below were MEASURED in Studio on NAS100.X (probe, 2026-11-26).
    SYMBOL="NAS100.X",               # instrument name exactly as in TradeLocker
    VALUE_PER_POINT_PER_LOT=10.0,    # $ per 1.0 index point per 1 lot (0.01 lot = $0.10/pt)
    MIN_LOT=0.01,
    LOT_STEP=0.01,
    TICK_SIZE=0.01,                  # Studio rounds order prices to this
    MAX_LOT=0.30,                    # hard ceiling on any single order (~$3/pt)
    LEVERAGE=20.0,                   # GFT indices leverage 1:20 (Studio backtest reports 1:50).
                                     # Use the LOWER of this and your GFT account leverage.
    MARGIN_CAP_PCT=30.0,             # margin used must stay under this % of equity (firm: 80%)

    # ---- US cash session (New York time) -----------------------------------
    SESSION_START_NY="09:30",
    SESSION_END_NY="16:00",          # open trades are closed on the last bar before this
    NO_ENTRY_FIRST_MIN=15,           # RSI2: no entries in the first 15 minutes
    LAST_ENTRY_NY="15:00",           # no new entries (or pending ORB orders) after this

    # ---- Strategy A: RSI2 trend pullback -----------------------------------
    RSI_PERIOD=2,
    RSI_LONG_ENTRY=10.0,             # buy when RSI(2) < 10 in an uptrend
    RSI_SHORT_ENTRY=90.0,            # sell when RSI(2) > 90 in a downtrend
    RSI_LONG_EXIT=70.0,              # exit a long when RSI(2) > 70
    RSI_SHORT_EXIT=30.0,             # exit a short when RSI(2) < 30
    TREND_EMA=200,                   # price above = longs only, below = shorts only
    USE_SLOW_TREND=False,            # also require price on the same side of SLOW_TREND_EMA
    SLOW_TREND_EMA=800,
    EXIT_EMA=5,                      # exit when the close crosses this EMA in our favour
    ATR_PERIOD=14,
    STOP_ATR_MULT=1.5,               # hard stop = 1.5 x ATR(14) from entry
    TIME_STOP_BARS=12,               # exit after this many bars in the trade

    # ---- Strategy B: Opening Range Breakout --------------------------------
    ORB_MINUTES=5,                   # opening range = first 5 minutes after the open
    ORB_STOP_MODE="range",           # "range" = other side of the range, "atr" = see below
    ORB_STOP_ATR_FRAC=0.10,          # with "atr": stop 0.10 x daily ATR(14) from entry
    ORB_DAILY_ATR_DAYS=14,
    ORB_TARGET_R=0.0,                # profit target in R (0 = none, exit at session end)
    ORB_DOJI_BODY_PCT=10.0,          # skip if candle body < 10% of its range
    ORB_RANGE_LOOKBACK=20,           # compare today's range with the last 20 days ...
    ORB_RANGE_MIN_PCTL=20.0,         # ... skip if below the 20th percentile
    ORB_RANGE_MAX_PCTL=90.0,         # ... or above the 90th percentile
    ORB_ENTRY_OFFSET_TICKS=1,        # entry stop order this many ticks beyond the range
    RANDOM_DIRECTION=False,          # True = random direction (same days, same brackets)
    RANDOM_SEED=42,

    # ---- time --------------------------------------------------------------
    BAR_TIMESTAMP="close",           # Studio stamps each bar at its CLOSE (measured)
    BAR_MINUTES=0,                   # 0 = read from the data feed
    VERBOSE=True,                    # print every entry/exit/guard event
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
def nth_sunday(year, month, n):
    d = dtm.date(year, month, 1)
    first = d + dtm.timedelta(days=(6 - d.weekday()) % 7)
    return first + dtm.timedelta(days=7 * (n - 1))


def ny_offset_hours(utc_dt):
    """New York's offset from UTC (-4 summer, -5 winter), US rules since 2007."""
    y = utc_dt.year
    dst_start = dtm.datetime.combine(nth_sunday(y, 3, 2), dtm.time(7, 0))   # 2:00 EST
    dst_end = dtm.datetime.combine(nth_sunday(y, 11, 1), dtm.time(6, 0))    # 2:00 EDT
    return -4 if dst_start <= utc_dt < dst_end else -5


def utc_to_ny(utc_dt):
    return utc_dt + dtm.timedelta(hours=ny_offset_hours(utc_dt))


def to_utc(dt, data_tz):
    """Convert a bar timestamp in the data's clock to naive UTC."""
    if dt.tzinfo is not None:
        off = dt.utcoffset() or dtm.timedelta(0)
        return (dt - off).replace(tzinfo=None)
    if data_tz in ("UTC", "utc", 0, None):
        return dt
    if data_tz in ("NY", "ny", "America/New_York"):
        guess = dt + dtm.timedelta(hours=5)
        return dt - dtm.timedelta(hours=ny_offset_hours(guess))
    return dt - dtm.timedelta(hours=float(data_tz))


def parse_hhmm(s):
    h, m = s.split(":")
    return dtm.time(int(h), int(m))


def trading_day_of(ny_dt):
    """The firm's trading day: it starts at 17:00 New York, so 17:00 Monday
    already belongs to Tuesday."""
    return (ny_dt + dtm.timedelta(hours=7)).date()


def quiet_log(msg):
    pass


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

    def __init__(self, settings=None, log=None):
        s = dict(SETTINGS)
        if settings:
            s.update(settings)
        self.s = s
        self.log = log if log is not None else quiet_log

        self.initial = float(s["INITIAL_BALANCE"])
        self.firm_floor = self.initial * (1 - s["FIRM_MAX_LOSS_PCT"] / 100.0)          # 4,500
        self.total_floor = self.initial * (1 - s["INTERNAL_TOTAL_STOP_PCT"] / 100.0)   # 4,650
        self.target_level = self.initial * (1 + (s["STEP_TARGET_PCT"] + s["TARGET_BUFFER_PCT"]) / 100.0)

        self.news_ny = sorted(dtm.datetime.strptime(x, "%Y-%m-%d %H:%M") for x in s["NEWS_EVENTS_NY"])
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

    def day_loss_allowed(self, pct):
        """Money the day may lose. Uses the SMALLER of initial balance and
        start-of-day reference, so it is never looser than either rule."""
        return pct / 100.0 * min(self.initial, self.day_start_ref)

    @property
    def daily_floor(self):
        return self.day_start_ref - self.day_loss_allowed(self.s["INTERNAL_DAILY_STOP_PCT"])

    @property
    def firm_daily_floor(self):
        return self.day_start_ref - self.day_loss_allowed(self.s["FIRM_DAILY_DD_PCT"])

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
            self.start_new_day(day, equity, balance)

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
        if self.s["FLATTEN_BEFORE_WEEKEND"] and self.weekend_flatten_time(ny):
            return "WEEKEND"
        if self.news_flatten_time(ny):
            return "NEWS_FLATTEN"
        return None

    def start_new_day(self, day, equity, balance):
        if self.day is not None:
            self.log("DAY {} starts. Previous day P&L {:+.2f}".format(day, equity - self.day_start_ref))
        self.day = day
        # higher of balance and equity at 5 PM NY = stricter floor
        self.day_start_ref = max(balance, equity)
        self.entries_today = 0
        self.day_halted = False

    # ---------------------------------------------------------- time rules
    def weekend_flatten_time(self, ny):
        wd = ny.weekday()   # Mon=0 ... Fri=4, Sat=5, Sun=6
        if wd == 4 and ny.time() >= self.weekend_flatten:
            return True
        if wd == 5:
            return True
        if wd == 6 and ny.time() < self.week_open:
            return True
        return False

    def weekend_no_open(self, ny):
        wd, t = ny.weekday(), ny.time()
        fri_cutoff = (dtm.datetime.combine(ny.date(), self.friday_close)
                      - dtm.timedelta(hours=self.s["FRIDAY_NO_OPEN_HOURS"])).time()
        if wd == 4 and t >= fri_cutoff:
            return "FRIDAY_LAST_HOURS"
        if wd == 5:
            return "WEEKEND"
        if wd == 6:
            open_end = (dtm.datetime.combine(ny.date(), self.week_open)
                        + dtm.timedelta(hours=self.s["MONDAY_NO_OPEN_HOURS"]))
            if ny < open_end:
                return "WEEK_OPEN_FIRST_HOURS"
        if wd == 0 and t < dtm.time(min(23, int(self.s["MONDAY_NO_OPEN_HOURS"])), 0):
            return "MONDAY_FIRST_HOURS"
        return None

    def news_near(self, ny, before_min, after_min):
        for ev in self.news_ny:
            if ev - dtm.timedelta(minutes=before_min) <= ny <= ev + dtm.timedelta(minutes=after_min):
                return ev
        return None

    def news_flatten_time(self, ny):
        m = self.s["NEWS_FLATTEN_BEFORE_MIN"]
        if m <= 0:
            return False
        for ev in self.news_ny:
            if ev - dtm.timedelta(minutes=m) <= ny < ev:
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
        wk = self.weekend_no_open(ny)
        if wk:
            return False, wk
        if self.s["FLATTEN_BEFORE_WEEKEND"] and self.weekend_flatten_time(ny):
            return False, "WEEKEND"
        before = max(self.s["NEWS_BLOCK_BEFORE_MIN"],
                     self.s["NEWS_FLATTEN_BEFORE_MIN"] + self.s["MIN_HOLD_SECONDS"] / 60.0)
        ev = self.news_near(ny, before, self.s["NEWS_BLOCK_AFTER_MIN"])
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
        limit_name, raw = caps[0]
        for cap_name, cap_value in caps:
            if cap_value < raw:
                limit_name, raw = cap_name, cap_value
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
        ev = self.news_near(self.ny(now), w, w)
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
# 4. SMALL HELPERS
# =============================================================================
def tick_decimals(tick):
    d = 0
    while d < 8 and abs(round(tick, d) - tick) > 1e-12:
        d += 1
    return d


def round_to_tick(price, tick, mode):
    """mode "down", "up" or "nearest". Returns a clean multiple of the tick."""
    n = round(price / tick, 6)
    if mode == "up":
        k = math.ceil(n)
    elif mode == "down":
        k = math.floor(n)
    else:
        k = math.floor(n + 0.5)
    return round(k * tick, tick_decimals(tick))


def percentile(values, pct):
    """Linear-interpolation percentile (same as numpy's default)."""
    v = sorted(values)
    if not v:
        return None
    pos = (len(v) - 1) * pct / 100.0
    lo = int(math.floor(pos))
    hi = min(lo + 1, len(v) - 1)
    return v[lo] + (v[hi] - v[lo]) * (pos - lo)


def minutes_of(t):
    return t.hour * 60 + t.minute


class SeededCoin(object):
    """Tiny deterministic random generator (linear congruential), so the
    RANDOM_DIRECTION test is repeatable and needs no extra imports."""

    def __init__(self, seed):
        self.state = int(seed) % 2147483648

    def flip(self):
        self.state = (1103515245 * self.state + 12345) % 2147483648
        return 1 if (self.state >> 16) & 1 else -1


class DailyATR(object):
    """ATR over completed firm trading days (17:00 NY to 17:00 NY), built from
    the intraday bars. Simple average of the last N true ranges."""

    def __init__(self, period):
        self.period = int(period)
        self.trs = []
        self.day = None
        self.high = None
        self.low = None
        self.close = None
        self.prev_close = None

    def update(self, day, high, low, close):
        if day != self.day:
            if self.day is not None:
                self.finish_day()
            self.day = day
            self.high = high
            self.low = low
        else:
            self.high = max(self.high, high)
            self.low = min(self.low, low)
        self.close = close

    def finish_day(self):
        tr = self.high - self.low
        if self.prev_close is not None:
            tr = max(tr, abs(self.high - self.prev_close), abs(self.low - self.prev_close))
        self.trs.append(tr)
        if len(self.trs) > self.period:
            self.trs.pop(0)
        self.prev_close = self.close

    def value(self):
        if len(self.trs) < self.period:
            return None
        return sum(self.trs) / len(self.trs)


# =============================================================================
# 5. THE STRATEGY STUDIO RUNS
# =============================================================================
class TLPropBot(bt.Strategy):
    # Every non-list setting becomes a Studio parameter input.
    params = tuple([(k, SETTINGS[k]) for k in SETTINGS if not isinstance(SETTINGS[k], list)])

    # ------------------------------------------------------------ setup
    def __init__(self):
        cfg = dict(SETTINGS)
        for k in SETTINGS:
            if not isinstance(SETTINGS[k], list):
                cfg[k] = getattr(self.p, k)
        self.cfg = cfg
        self.guard = PropRiskGuard(cfg, log=self.log)
        self.tick = float(cfg["TICK_SIZE"])
        self.mode = str(cfg["STRATEGY"]).upper()

        if cfg["BAR_MINUTES"]:
            self.bar_minutes = int(cfg["BAR_MINUTES"])
        elif self.data.p.timeframe == bt.TimeFrame.Minutes:
            self.bar_minutes = int(self.data.p.compression)
        else:
            self.bar_minutes = 60 * int(self.data.p.compression)
        self.session_start = minutes_of(parse_hhmm(cfg["SESSION_START_NY"]))
        self.session_end = minutes_of(parse_hhmm(cfg["SESSION_END_NY"]))
        self.last_entry = minutes_of(parse_hhmm(cfg["LAST_ENTRY_NY"]))

        if self.mode == "RSI2":
            c = self.data.close
            self.rsi = bt.indicators.RSI(c, period=int(cfg["RSI_PERIOD"]), safediv=True)
            self.ema_trend = bt.indicators.EMA(c, period=int(cfg["TREND_EMA"]))
            self.ema_exit = bt.indicators.EMA(c, period=int(cfg["EXIT_EMA"]))
            self.atr = bt.indicators.ATR(self.data, period=int(cfg["ATR_PERIOD"]))
            self.ema_slow = None
            if cfg["USE_SLOW_TREND"]:
                self.ema_slow = bt.indicators.EMA(c, period=int(cfg["SLOW_TREND_EMA"]))
        elif self.mode == "ORB":
            self.daily_atr = DailyATR(cfg["ORB_DAILY_ATR_DAYS"])
            self.orb_ranges = []          # past opening-range sizes (points)
            self.orb_today = None         # today's opening range info
            self.orb_done_day = None      # firm day on which ORB already traded/decided
            self.coin = SeededCoin(cfg["RANDOM_SEED"])
            if self.bar_minutes > int(cfg["ORB_MINUTES"]) or int(cfg["ORB_MINUTES"]) % self.bar_minutes:
                self.log("CONFIG ERROR: ORB needs bars of " + str(cfg["ORB_MINUTES"])
                         + " minutes or a divisor of it; data has " + str(self.bar_minutes))
        else:
            self.log("CONFIG ERROR: STRATEGY must be RSI2 or ORB, got " + self.mode)

        # order / trade state
        self.entry_order = None
        self.stop_order = None
        self.target_order = None
        self.close_order = None
        self.trade_info = None            # dict for the trade in progress
        self.balance = float(cfg["INITIAL_BALANCE"])
        self.trade_records = []           # read by the research harness
        self.day_stats = {}
        self.deferred_logged = None
        self.now = None
        self.ny_now = None

    # ------------------------------------------------------------ logging
    def log(self, msg):
        if not self.cfg["VERBOSE"] and not msg.startswith(("ENTRY", "EXIT", "GUARD", "!!!", "CONFIG", "SUMMARY")):
            return
        stamp = self.ny_now.strftime("%Y-%m-%d %H:%M NY") if self.ny_now is not None else "----"
        print("[BOT] " + stamp + " | " + msg)

    # ------------------------------------------------------------ time
    def bar_end(self):
        """Bar END time in the data's clock, rounded to the minute."""
        dt = self.data.datetime.datetime(0)
        dt = (dt + dtm.timedelta(seconds=30)).replace(second=0, microsecond=0)
        if self.cfg["BAR_TIMESTAMP"] == "open":
            dt = dt + dtm.timedelta(minutes=self.bar_minutes)
        return dt

    # ------------------------------------------------------------ main loop
    def next(self):
        self.now = self.bar_end()
        self.ny_now = self.guard.ny(self.now)
        equity = self.broker.getvalue()
        pos = self.getposition(self.data).size
        reason = self.guard.update(self.now, equity, self.balance, has_position=(pos != 0))
        self.track_day(equity)

        if self.mode == "ORB":
            self.orb_update_bar()

        if self.close_order is not None:
            return                                  # waiting for an exit to fill
        if pos != 0 and self.trade_info is not None:
            self.manage_position(reason)
        elif pos != 0:
            # a position we do not know about: close it (should never happen)
            self.log("!!! untracked position size " + str(pos) + ": closing it")
            self.close_order = self.close()
        elif self.entry_order is not None:
            self.manage_pending_entry()
        else:
            if self.mode == "RSI2":
                self.rsi2_entry()
            elif self.mode == "ORB":
                self.orb_entry()

    def track_day(self, equity):
        d = self.guard.day
        st = self.day_stats.get(d)
        if st is None:
            st = {"start": self.guard.day_start_ref, "low": equity, "end": equity}
            self.day_stats[d] = st
        st["low"] = min(st["low"], equity)
        st["end"] = equity

    def minutes_now(self):
        return minutes_of(self.ny_now.time())

    def in_entry_window(self):
        # RSI2: never in the first NO_ENTRY_FIRST_MIN minutes.
        # ORB: as soon as the opening-range candle has closed.
        m = self.minutes_now()
        if self.mode == "ORB":
            first = self.session_start + int(self.cfg["ORB_MINUTES"])
        else:
            first = self.session_start + int(self.cfg["NO_ENTRY_FIRST_MIN"])
        return (self.ny_now.weekday() < 5
                and m >= first
                and m <= self.last_entry
                and m + self.bar_minutes < self.session_end)

    def session_exit_due(self):
        m = self.minutes_now()
        return m + self.bar_minutes >= self.session_end or m < self.session_start

    # ------------------------------------------------------------ entries
    def rsi2_entry(self):
        if not self.in_entry_window():
            return
        ok, why = self.guard.can_open(self.now, 0)
        if not ok:
            return
        c = self.data.close[0]
        up = c > self.ema_trend[0]
        down = c < self.ema_trend[0]
        if self.ema_slow is not None:
            up = up and c > self.ema_slow[0]
            down = down and c < self.ema_slow[0]
        direction = 0
        if up and self.rsi[0] < self.cfg["RSI_LONG_ENTRY"]:
            direction = 1
        elif down and self.rsi[0] > self.cfg["RSI_SHORT_ENTRY"]:
            direction = -1
        if direction == 0:
            return
        dist = self.cfg["STOP_ATR_MULT"] * self.atr[0]
        if direction > 0:
            stop = round_to_tick(c - dist, self.tick, "down")
        else:
            stop = round_to_tick(c + dist, self.tick, "up")
        self.submit_entry(direction, None, stop, c, "RSI2 rsi=" + str(round(self.rsi[0], 1)))

    def orb_update_bar(self):
        d = self.data
        self.daily_atr.update(self.guard.day, d.high[0], d.low[0], d.close[0])
        n_bars = int(self.cfg["ORB_MINUTES"]) // self.bar_minutes
        if n_bars < 1 or self.ny_now.weekday() >= 5:
            return
        if self.minutes_now() != self.session_start + int(self.cfg["ORB_MINUTES"]):
            return
        hi = max([d.high[-i] for i in range(n_bars)])
        lo = min([d.low[-i] for i in range(n_bars)])
        op = d.open[-(n_bars - 1)]
        cl = d.close[0]
        rng = hi - lo
        info = {"high": hi, "low": lo, "open": op, "close": cl, "range": rng,
                "day": self.guard.day, "valid": True, "why": "ok"}
        history = self.orb_ranges[-int(self.cfg["ORB_RANGE_LOOKBACK"]):]
        if rng <= 0 or abs(cl - op) < self.cfg["ORB_DOJI_BODY_PCT"] / 100.0 * rng:
            info["valid"], info["why"] = False, "doji"
        elif len(history) < int(self.cfg["ORB_RANGE_LOOKBACK"]):
            info["valid"], info["why"] = False, "not enough range history"
        else:
            lo_p = percentile(history, self.cfg["ORB_RANGE_MIN_PCTL"])
            hi_p = percentile(history, self.cfg["ORB_RANGE_MAX_PCTL"])
            if rng < lo_p or rng > hi_p:
                info["valid"], info["why"] = False, "range {:.1f} outside [{:.1f}, {:.1f}]".format(rng, lo_p, hi_p)
        if info["valid"]:
            info["direction"] = 1 if cl > op else -1
            if self.cfg["RANDOM_DIRECTION"]:
                info["direction"] = self.coin.flip()
        self.orb_ranges.append(rng)
        self.orb_today = info
        self.log("ORB range H={:.2f} L={:.2f} size={:.2f} -> {}".format(hi, lo, rng, info["why"]))

    def orb_entry(self):
        info = self.orb_today
        if info is None or not info["valid"] or info["day"] != self.guard.day:
            return
        if self.orb_done_day == self.guard.day or not self.in_entry_window():
            return
        ok, why = self.guard.can_open(self.now, 0)
        if not ok:
            return
        self.orb_done_day = self.guard.day          # one attempt per day
        off = int(self.cfg["ORB_ENTRY_OFFSET_TICKS"]) * self.tick
        direction = info["direction"]
        if direction > 0:
            entry = round_to_tick(info["high"] + off, self.tick, "up")
        else:
            entry = round_to_tick(info["low"] - off, self.tick, "down")
        if self.cfg["ORB_STOP_MODE"] == "atr":
            atr = self.daily_atr.value()
            if atr is None:
                self.log("ORB skip: daily ATR not ready")
                return
            dist = self.cfg["ORB_STOP_ATR_FRAC"] * atr
            stop = entry - dist if direction > 0 else entry + dist
        else:
            stop = info["low"] if direction > 0 else info["high"]
        stop = round_to_tick(stop, self.tick, "down" if direction > 0 else "up")
        c = self.data.close[0]
        # the breakout level must still be on the right side of the price
        if (direction > 0 and entry <= c) or (direction < 0 and entry >= c):
            self.log("ORB skip: price already beyond the entry level")
            return
        self.submit_entry(direction, entry, stop, entry, "ORB" + (" RANDOM" if self.cfg["RANDOM_DIRECTION"] else ""))

    def submit_entry(self, direction, entry_price, stop, planned_entry, label):
        """Entry + hard stop as one bracket. entry_price None = market order."""
        equity = self.broker.getvalue()
        lots, why = self.guard.size_position(planned_entry, stop, equity)
        if lots <= 0:
            self.log("SKIP " + label + ": " + why)
            return
        kw = {"size": lots, "stopprice": stop, "limitexec": None}
        if entry_price is None:
            kw["exectype"] = bt.Order.Market
        else:
            kw["exectype"] = bt.Order.Stop
            kw["price"] = entry_price
        if direction > 0:
            orders = self.buy_bracket(**kw)
        else:
            orders = self.sell_bracket(**kw)
        self.entry_order = orders[0]
        self.stop_order = orders[1]
        self.trade_info = {"direction": direction, "lots": lots, "stop": stop, "planned": planned_entry,
                           "label": label, "filled": False, "bars": 0, "exit_reason": None,
                           "fill_price": None, "fill_time": None, "target_placed": False,
                           "margin_pct": self.guard.margin_used(lots, planned_entry) / equity * 100.0}
        self.log("ORDER {} {} {} lots, entry {}, stop {} ({})".format(
            label, "BUY" if direction > 0 else "SELL", lots,
            "market" if entry_price is None else entry_price, stop, why))

    def manage_pending_entry(self):
        """ORB stop-entry orders: cancel when the window closes or the guard says no."""
        ok, why = self.guard.can_open(self.now, 0)
        m = self.minutes_now()
        if not ok or m > self.last_entry or self.session_exit_due():
            self.log("CANCEL pending entry: " + (why if not ok else "entry window over"))
            self.cancel(self.entry_order)

    # ------------------------------------------------------------ exits
    def manage_position(self, guard_reason):
        t = self.trade_info
        t["bars"] += 1
        reason = guard_reason
        if reason is None:
            reason = self.exit_signal(t)
        if reason is None:
            self.maybe_place_target(t)
            return
        forced = reason in PropRiskGuard.FORCED_REASONS
        ok, why = self.guard.exit_allowed(self.now, forced)
        if not ok:
            if self.deferred_logged != why:
                self.log("EXIT " + reason + " deferred: " + why)
                self.deferred_logged = why
            return
        self.exit_position(reason)

    def exit_signal(self, t):
        if self.session_exit_due():
            return "SESSION_END"
        if self.mode != "RSI2":
            return None
        c = self.data.close[0]
        if t["direction"] > 0:
            if c > self.ema_exit[0]:
                return "EMA_EXIT"
            if self.rsi[0] > self.cfg["RSI_LONG_EXIT"]:
                return "RSI_EXIT"
        else:
            if c < self.ema_exit[0]:
                return "EMA_EXIT"
            if self.rsi[0] < self.cfg["RSI_SHORT_EXIT"]:
                return "RSI_EXIT"
        if t["bars"] >= int(self.cfg["TIME_STOP_BARS"]):
            return "TIME_STOP"
        return None

    def maybe_place_target(self, t):
        """ORB R target: placed only after the minimum hold time, so a fast
        profit can never be closed inside 2 minutes."""
        r = self.cfg["ORB_TARGET_R"]
        if self.mode != "ORB" or r <= 0 or t["target_placed"] or not t["filled"]:
            return
        ok, why = self.guard.exit_allowed(self.now, False)
        if not ok:
            return
        risk_pts = abs(t["fill_price"] - t["stop"])
        if t["direction"] > 0:
            price = round_to_tick(t["fill_price"] + r * risk_pts, self.tick, "down")
            if price <= self.data.close[0]:
                self.exit_position("TARGET_PASSED")
                return
            self.target_order = self.sell(size=t["lots"], exectype=bt.Order.Limit, price=price, oco=self.stop_order)
        else:
            price = round_to_tick(t["fill_price"] - r * risk_pts, self.tick, "up")
            if price >= self.data.close[0]:
                self.exit_position("TARGET_PASSED")
                return
            self.target_order = self.buy(size=t["lots"], exectype=bt.Order.Limit, price=price, oco=self.stop_order)
        t["target_placed"] = True
        self.log("TARGET placed at " + str(price))

    def exit_position(self, reason):
        t = self.trade_info
        t["exit_reason"] = reason
        for o in (self.target_order, self.stop_order):
            if o is not None and o.alive():
                self.cancel(o)
        self.close_order = self.close()

    # ------------------------------------------------------------ broker events
    def same_order(self, a, b):
        # Backtrader passes a COPY of the order to notify_order, so compare refs.
        return a is not None and b is not None and a.ref == b.ref

    def notify_order(self, order):
        if order.status in (order.Submitted, order.Accepted):
            return
        self.ny_now = self.guard.ny(self.bar_end())
        t = self.trade_info
        if self.same_order(order, self.entry_order):
            if order.status == order.Completed:
                fill_time = self.bar_end() - dtm.timedelta(minutes=self.bar_minutes)
                t["filled"] = True
                t["fill_price"] = order.executed.price
                t["fill_time"] = fill_time
                self.guard.register_entry(fill_time, t["direction"], t["lots"], order.executed.price, t["stop"])
                self.log("ENTRY {} {} {} lots @ {:.2f} stop {:.2f} risk ${:.2f} margin {:.1f}% | {}".format(
                    t["label"], "LONG" if t["direction"] > 0 else "SHORT", t["lots"], order.executed.price,
                    t["stop"], self.guard.open_trade["risk"], t["margin_pct"], self.guard.state_str()))
            else:
                self.log("Entry order " + order.getstatusname() + " (no trade)")
                self.entry_order = None
                self.stop_order = None
                self.trade_info = None
            return
        if self.same_order(order, self.stop_order) and order.status == order.Completed:
            if t is not None and t["exit_reason"] is None:
                t["exit_reason"] = "STOP"
        elif self.same_order(order, self.target_order) and order.status == order.Completed:
            if t is not None and t["exit_reason"] is None:
                t["exit_reason"] = "TARGET"
        elif self.same_order(order, self.close_order) and order.status != order.Completed:
            self.log("!!! close order " + order.getstatusname() + ", will retry")
            self.close_order = None
        if order.status in (order.Margin, order.Rejected):
            self.log("!!! order " + order.getstatusname())

    def notify_trade(self, trade):
        if not trade.isclosed:
            return
        self.now = self.bar_end()
        self.ny_now = self.guard.ny(self.now)
        pnl = trade.pnlcomm
        self.balance += pnl
        t = self.trade_info or {}
        r = self.guard.register_exit(self.now, pnl)
        exit_time = self.bar_end()
        held_min = None
        if t.get("fill_time") is not None:
            held_min = (exit_time - t["fill_time"]).total_seconds() / 60.0
        rec = {
            "entry_time_ny": self.guard.ny(t["fill_time"]) if t.get("fill_time") else None,
            "exit_time_ny": self.guard.ny(exit_time),
            "day": self.guard.day,
            "direction": t.get("direction"),
            "lots": t.get("lots"),
            "entry": t.get("fill_price"),
            "stop": t.get("stop"),
            "pnl": pnl,
            "r": r,
            "reason": t.get("exit_reason") or "UNKNOWN",
            "held_min": held_min,
            "label": t.get("label"),
        }
        self.trade_records.append(rec)
        self.log("EXIT {} {} pnl ${:+.2f} R={} held {} min | dayPnL ${:+.2f} | {}".format(
            rec["reason"], t.get("label"), pnl, "n/a" if r is None else "{:+.2f}".format(r),
            "?" if held_min is None else "{:.0f}".format(held_min),
            self.guard.day_pnl(self.broker.getvalue()), self.guard.state_str(self.broker.getvalue())))
        # clean up any order left over from this trade
        for o in (self.target_order, self.stop_order):
            if o is not None and o.alive():
                self.cancel(o)
        self.entry_order = None
        self.stop_order = None
        self.target_order = None
        self.close_order = None
        self.trade_info = None
        self.deferred_logged = None

    # ------------------------------------------------------------ end of test
    def stop(self):
        n = len(self.trade_records)
        wins = len([x for x in self.trade_records if x["pnl"] > 0])
        rs = [x["r"] for x in self.trade_records if x["r"] is not None]
        self.log("SUMMARY strategy={} trades={} wins={} totalR={:+.2f} final equity {:.2f} | {}".format(
            self.mode, n, wins, sum(rs), self.broker.getvalue(), self.guard.state_str()))
        self.log("SUMMARY worst day {:.2f}% | firm breach: {}".format(
            self.guard.worst_day_pct, self.guard.firm_breach or "none"))


# ===== END OF FILE: if this line is missing in Studio, the copy was cut off =====
