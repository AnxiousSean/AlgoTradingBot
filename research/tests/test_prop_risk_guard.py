"""Unit tests for PropRiskGuard. Run from the research/ folder:  python -m pytest -q"""
import datetime as dt

import pytest

from tl_prop_bot import PropRiskGuard, ny_offset_hours, to_utc, trading_day_of, utc_to_ny

D = dt.datetime


# Most tests use simple round numbers ($1 per point, 1:20) so the arithmetic is
# easy to check by hand; TestRealInstrument uses the measured NAS100.X values.
TEST_BASE = {"VALUE_PER_POINT_PER_LOT": 1.0, "LEVERAGE": 20.0, "MAX_LOT": 5.0}


def guard(**kw):
    s = dict(TEST_BASE)
    s.update(kw)
    return PropRiskGuard(settings=s)


# A Wednesday in summer (EDT, UTC-4) and one in winter (EST, UTC-5)
WED_SUMMER_UTC = D(2026, 7, 15, 15, 0)   # 11:00 NY
WED_WINTER_UTC = D(2026, 1, 14, 16, 0)   # 11:00 NY


# ---------------------------------------------------------------- time
class TestTime:
    def test_dst_offsets(self):
        assert ny_offset_hours(D(2026, 7, 1, 12)) == -4
        assert ny_offset_hours(D(2026, 1, 15, 12)) == -5

    def test_dst_boundaries_2026(self):
        # DST starts Sun 8 Mar 2026 07:00 UTC, ends Sun 1 Nov 2026 06:00 UTC
        assert ny_offset_hours(D(2026, 3, 8, 6, 59)) == -5
        assert ny_offset_hours(D(2026, 3, 8, 7, 0)) == -4
        assert ny_offset_hours(D(2026, 11, 1, 5, 59)) == -4
        assert ny_offset_hours(D(2026, 11, 1, 6, 0)) == -5

    def test_5pm_ny_reset(self):
        assert utc_to_ny(D(2026, 7, 15, 21, 0)) == D(2026, 7, 15, 17, 0)
        assert utc_to_ny(D(2026, 1, 14, 22, 0)) == D(2026, 1, 14, 17, 0)
        assert trading_day_of(D(2026, 7, 15, 16, 59)) == dt.date(2026, 7, 15)
        assert trading_day_of(D(2026, 7, 15, 17, 0)) == dt.date(2026, 7, 16)

    def test_data_timezones(self):
        assert to_utc(D(2026, 7, 15, 18, 0), 3) == D(2026, 7, 15, 15, 0)
        assert to_utc(D(2026, 7, 15, 11, 0), "NY") == D(2026, 7, 15, 15, 0)
        assert to_utc(D(2026, 1, 14, 11, 0), "NY") == D(2026, 1, 14, 16, 0)
        aware = D(2026, 7, 15, 18, 0, tzinfo=dt.timezone(dt.timedelta(hours=3)))
        assert to_utc(aware, "UTC") == D(2026, 7, 15, 15, 0)


# ---------------------------------------------------------------- floors
class TestFloors:
    def test_static_floors(self):
        g = guard()
        assert g.firm_floor == pytest.approx(4500.0)
        assert g.total_floor == pytest.approx(4650.0)
        assert g.target_level == pytest.approx(5425.0)

    def test_daily_stop_at_2_5pct(self):
        g = guard()
        assert g.update(WED_SUMMER_UTC, 4876.0, 5000.0, has_position=True) is None
        assert g.can_open(WED_SUMMER_UTC)[0]
        assert g.update(WED_SUMMER_UTC, 4875.0, 5000.0, has_position=True) == "DAILY_STOP"
        assert g.can_open(WED_SUMMER_UTC) == (False, "DAILY_STOP")

    def test_daily_stop_resets_next_day_at_5pm(self):
        g = guard()
        g.update(D(2026, 7, 15, 20, 0), 5000.0, 5000.0)          # 16:00 NY
        g.update(D(2026, 7, 15, 20, 30), 4870.0, 4870.0)          # daily stop
        assert g.day_halted
        g.update(D(2026, 7, 15, 20, 59), 4870.0, 4870.0)          # 16:59 NY, same day
        assert g.day_halted
        g.update(D(2026, 7, 15, 21, 0), 4870.0, 4870.0)           # 17:00 NY -> new day
        assert not g.day_halted
        assert g.day_start_ref == 4870.0
        assert g.daily_floor == pytest.approx(4870.0 - 0.025 * 4870.0)

    def test_day_reference_is_max_of_balance_and_equity(self):
        g = guard()
        g.update(WED_SUMMER_UTC, 5100.0, 5000.0, has_position=True)
        assert g.day_start_ref == 5100.0
        # allowed loss uses the smaller of initial and day ref -> 125, floor 4975
        assert g.daily_floor == pytest.approx(5100.0 - 125.0)

    def test_total_stop_is_permanent(self):
        g = guard()
        g.update(WED_SUMMER_UTC, 4700.0, 4700.0)
        assert g.update(WED_SUMMER_UTC + dt.timedelta(minutes=15), 4650.0, 4700.0, True) == "TOTAL_STOP"
        g.update(WED_SUMMER_UTC + dt.timedelta(days=1), 4650.0, 4650.0)
        assert g.can_open(WED_SUMMER_UTC + dt.timedelta(days=1)) == (False, "TOTAL_STOP")

    def test_target_lock(self):
        g = guard()
        assert g.update(WED_SUMMER_UTC, 5424.0, 5424.0, True) is None
        assert g.update(WED_SUMMER_UTC, 5425.0, 5425.0, True) == "TARGET_LOCK"
        assert g.can_open(WED_SUMMER_UTC) == (False, "TARGET_LOCK")

    def test_target_lock_step2_and_disabled(self):
        g = guard(STEP_TARGET_PCT=6.0)
        assert g.target_level == pytest.approx(5325.0)
        g2 = guard(USE_TARGET_LOCK=False)
        assert g2.update(WED_SUMMER_UTC, 6000.0, 6000.0, True) is None

    def test_firm_breach_flag(self):
        g = guard()
        g.update(WED_SUMMER_UTC, 5000.0, 5000.0)
        assert g.firm_breach is None
        g.update(WED_SUMMER_UTC, 4799.0, 5000.0)      # 4% daily = 200
        assert "FIRM DAILY" in g.firm_breach

    def test_worst_day_tracked(self):
        g = guard()
        g.update(WED_SUMMER_UTC, 5000.0, 5000.0)
        g.update(WED_SUMMER_UTC, 4950.0, 5000.0)
        assert g.worst_day_pct == pytest.approx(-1.0)


# ---------------------------------------------------------------- sizing
class TestSizing:
    def setup_method(self):
        self.g = guard(LEVERAGE=1000.0)  # margin not binding unless a test says so
        self.g.update(WED_SUMMER_UTC, 5000.0, 5000.0)

    def test_basic_risk_sizing(self):
        lots, _ = self.g.size_position(20000.0, 19980.0, 5000.0)   # $25 / 20pt
        assert lots == pytest.approx(1.25)

    def test_rounds_down_to_step(self):
        lots, _ = self.g.size_position(20000.0, 19963.0, 5000.0)   # 25/37 = 0.6756
        assert lots == pytest.approx(0.67)

    def test_float_edge_rounding(self):
        assert self.g.round_lots(0.29) == pytest.approx(0.29)
        assert self.g.round_lots(0.299999) == pytest.approx(0.29)
        g = guard(LOT_STEP=0.1)
        assert g.round_lots(0.7) == pytest.approx(0.7)
        assert g.round_lots(1.0) == pytest.approx(1.0)

    def test_value_per_point(self):
        g = guard(VALUE_PER_POINT_PER_LOT=10.0, LEVERAGE=1000.0)
        g.update(WED_SUMMER_UTC, 5000.0, 5000.0)
        lots, _ = g.size_position(20000.0, 19980.0, 5000.0)        # 25/(20*10)
        assert lots == pytest.approx(0.12)

    def test_below_min_lot_skips(self):
        g = guard(MIN_LOT=0.1, LOT_STEP=0.1, LEVERAGE=1000.0)
        g.update(WED_SUMMER_UTC, 5000.0, 5000.0)
        lots, why = g.size_position(20000.0, 19700.0, 5000.0)      # 25/300 = 0.083
        assert lots == 0.0 and "below min lot" in why

    def test_risk_is_based_on_initial_not_equity(self):
        g = guard(LEVERAGE=1000.0)
        g.update(WED_SUMMER_UTC, 5300.0, 5300.0)
        lots, _ = g.size_position(20000.0, 19980.0, 5300.0)
        assert lots == pytest.approx(1.25)

    def test_room_before_daily_stop_limits_size(self):
        self.g.update(WED_SUMMER_UTC, 4900.0, 4900.0)   # room to 4875 = 25 -> /1.5 = 16.67
        lots, why = self.g.size_position(20000.0, 19980.0, 4900.0)
        assert lots == pytest.approx(0.83)
        assert "risk" in why

    def test_margin_cap(self):
        g = guard(LEVERAGE=20.0)                       # 1 lot @20000 = 1000 margin
        g.update(WED_SUMMER_UTC, 5000.0, 5000.0)
        lots, why = g.size_position(20000.0, 19990.0, 5000.0)   # risk says 2.5 lots
        assert lots == pytest.approx(1.5)              # 30% of 5000 / 1000
        assert "margin" in why
        assert g.margin_used(lots, 20000.0) / 5000.0 <= 0.30 + 1e-9

    def test_max_lot(self):
        g = guard(MAX_LOT=0.5, LEVERAGE=1000.0)
        g.update(WED_SUMMER_UTC, 5000.0, 5000.0)
        assert g.size_position(20000.0, 19990.0, 5000.0)[0] == pytest.approx(0.5)

    def test_no_lot_increase_after_loss(self):
        g = self.g
        lots, _ = g.size_position(20000.0, 19950.0, 5000.0)       # 0.5
        g.register_entry(WED_SUMMER_UTC, 1, lots, 20000.0, 19950.0)
        g.register_exit(WED_SUMMER_UTC + dt.timedelta(minutes=30), -25.0)
        lots2, why = g.size_position(20000.0, 19990.0, 4975.0)    # risk alone -> 2.5
        assert lots2 == pytest.approx(0.5)
        assert "no_increase_after_loss" in why
        g.register_entry(WED_SUMMER_UTC, 1, lots2, 20000.0, 19990.0)
        g.register_exit(WED_SUMMER_UTC + dt.timedelta(minutes=60), +10.0)
        assert g.size_position(20000.0, 19990.0, 4985.0)[0] > 0.5

    def test_invalid_stop(self):
        assert self.g.size_position(20000.0, 20000.0, 5000.0)[0] == 0.0


# ---------------------------------------------------------------- limits & exits
class TestEntriesAndExits:
    def test_max_open_positions(self):
        g = guard()
        g.update(WED_SUMMER_UTC, 5000.0)
        assert g.can_open(WED_SUMMER_UTC, open_positions=1) == (False, "MAX_OPEN_POSITIONS")

    def test_max_entries_per_day_and_reset(self):
        g = guard()
        g.update(WED_SUMMER_UTC, 5000.0)
        for i in range(3):
            assert g.can_open(WED_SUMMER_UTC)[0]
            g.register_entry(WED_SUMMER_UTC, 1, 0.1, 20000.0, 19980.0)
            g.register_exit(WED_SUMMER_UTC, 1.0)
        assert g.can_open(WED_SUMMER_UTC) == (False, "MAX_ENTRIES_PER_DAY")
        nxt = WED_SUMMER_UTC + dt.timedelta(days=1)
        g.update(nxt, 5000.0)
        assert g.can_open(nxt)[0]
        assert len(g.trading_days) == 1

    def test_min_hold_time(self):
        g = guard()
        g.update(WED_SUMMER_UTC, 5000.0)
        g.register_entry(WED_SUMMER_UTC, 1, 0.1, 20000.0, 19980.0)
        assert g.exit_allowed(WED_SUMMER_UTC + dt.timedelta(seconds=119))[0] is False
        assert g.exit_allowed(WED_SUMMER_UTC + dt.timedelta(seconds=120))[0] is True
        assert g.exit_allowed(WED_SUMMER_UTC + dt.timedelta(seconds=10), forced=True)[0] is True

    def test_r_multiple(self):
        g = guard()
        g.update(WED_SUMMER_UTC, 5000.0)
        g.register_entry(WED_SUMMER_UTC, 1, 0.5, 20000.0, 19950.0)  # risk $25
        assert g.register_exit(WED_SUMMER_UTC, 50.0) == pytest.approx(2.0)
        g.register_entry(WED_SUMMER_UTC, -1, 0.5, 20000.0, 20050.0)
        assert g.register_exit(WED_SUMMER_UTC, -25.0) == pytest.approx(-1.0)

    def test_state_str(self):
        g = guard()
        g.update(WED_SUMMER_UTC, 4990.0, 5000.0)
        s = g.state_str()
        assert "dayStart=5000.00" in s and "entries=0/3" in s


# ---------------------------------------------------------------- news
class TestNews:
    EV = "2026-07-15 10:00"           # NY; = 14:00 UTC

    def g(self, **kw):
        g = guard(NEWS_EVENTS_NY=[self.EV], **kw)
        g.update(D(2026, 7, 15, 13, 0), 5000.0)
        return g

    def test_entry_blackout(self):
        g = self.g()
        assert g.can_open(D(2026, 7, 15, 13, 39))[0]                       # 21 min before
        assert g.can_open(D(2026, 7, 15, 13, 40))[1].startswith("NEWS")    # 20 min before
        assert g.can_open(D(2026, 7, 15, 14, 10))[1].startswith("NEWS")    # 10 min after
        assert g.can_open(D(2026, 7, 15, 14, 11))[0]

    def test_no_voluntary_close_near_news(self):
        g = self.g(NEWS_FLATTEN_BEFORE_MIN=0)
        g.register_entry(D(2026, 7, 15, 13, 0), 1, 0.1, 20000.0, 19980.0)
        assert g.exit_allowed(D(2026, 7, 15, 13, 53))[0]
        assert g.exit_allowed(D(2026, 7, 15, 13, 54))[1].startswith("NEWS_NO_CLOSE")
        assert g.exit_allowed(D(2026, 7, 15, 14, 6))[1].startswith("NEWS_NO_CLOSE")
        assert g.exit_allowed(D(2026, 7, 15, 14, 7))[0]
        assert g.exit_allowed(D(2026, 7, 15, 14, 0), forced=True)[0]

    def test_flatten_before_news(self):
        g = self.g()
        assert g.update(D(2026, 7, 15, 13, 49), 5000.0, has_position=True) is None
        assert g.update(D(2026, 7, 15, 13, 50), 5000.0, has_position=True) == "NEWS_FLATTEN"
        assert g.exit_allowed(D(2026, 7, 15, 13, 50))[0]      # 10 min before: outside +-6

    def test_news_in_data_timezone(self):
        g = guard(NEWS_EVENTS_NY=[self.EV], DATA_TIMEZONE=3)  # data at UTC+3
        g.update(D(2026, 7, 15, 16, 0), 5000.0)
        assert g.can_open(D(2026, 7, 15, 17, 0))[1].startswith("NEWS")  # 17:00 = 14:00 UTC


# ---------------------------------------------------------------- weekend
class TestWeekend:
    # 2026-07-17 is a Friday, 07-19 Sunday, 07-20 Monday (EDT: NY = UTC-4)
    def test_friday_last_3_hours(self):
        g = guard()
        g.update(D(2026, 7, 17, 15, 0), 5000.0)
        assert g.can_open(D(2026, 7, 17, 17, 59))[0]                          # 13:59 NY
        assert g.can_open(D(2026, 7, 17, 18, 0)) == (False, "FRIDAY_LAST_HOURS")

    def test_weekend_flatten(self):
        g = guard()
        assert g.update(D(2026, 7, 17, 20, 44), 5000.0, has_position=True) is None   # 16:44 NY
        assert g.update(D(2026, 7, 17, 20, 45), 5000.0, has_position=True) == "WEEKEND"

    def test_weekend_flatten_can_be_disabled(self):
        g = guard(FLATTEN_BEFORE_WEEKEND=False)
        assert g.update(D(2026, 7, 17, 20, 45), 5000.0, has_position=True) is None

    def test_week_open_and_monday_blocks(self):
        g = guard()
        g.update(D(2026, 7, 19, 22, 0), 5000.0)
        assert g.can_open(D(2026, 7, 19, 22, 0)) == (False, "WEEK_OPEN_FIRST_HOURS")   # Sun 18:00 NY
        assert g.can_open(D(2026, 7, 19, 22, 0) + dt.timedelta(hours=3))[0]           # Sun 21:00 NY
        assert g.can_open(D(2026, 7, 20, 6, 59)) == (False, "MONDAY_FIRST_HOURS")      # Mon 02:59 NY
        assert g.can_open(D(2026, 7, 20, 7, 0))[0]                                     # Mon 03:00 NY
        assert g.can_open(D(2026, 7, 20, 13, 45))[0]                                   # Mon 09:45 NY

    def test_saturday_blocked(self):
        g = guard()
        assert g.can_open(D(2026, 7, 18, 15, 0)) == (False, "WEEKEND")


# ---------------------------------------------------------------- measured NAS100.X values
class TestRealInstrument:
    def test_nas100_defaults(self):
        g = PropRiskGuard()                      # bot defaults: $10/pt/lot, 1:50, max 0.30
        g.update(WED_SUMMER_UTC, 5000.0)
        lots, _ = g.size_position(30000.0, 29948.0, 5000.0)  # 1.5 x ATR(14) ~ 52 pts
        assert lots == pytest.approx(0.04)                    # $25 / (52 * $10) = 0.048
        assert lots * 52 * 10 <= 25.0
        assert g.margin_used(lots, 30000.0) / 5000.0 < 0.30   # $240 margin = 4.8%

    def test_nas100_tight_stop_hits_margin_cap(self):
        # 1 lot @30000 = $300k notional = $6000 margin at 1:50.
        # 30% of $5000 = $1500 -> 0.25 lots max, before MAX_LOT (0.30) applies.
        g = PropRiskGuard()
        g.update(WED_SUMMER_UTC, 5000.0)
        lots, why = g.size_position(30000.0, 29992.0, 5000.0)  # 8 pts -> risk says 0.31
        assert lots == pytest.approx(0.25) and "margin" in why
