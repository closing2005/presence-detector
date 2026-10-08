"""Unit tests for the session stats tracker."""
import sys
import os
from datetime import date, datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from stats import StatsTracker, format_summary


def _ts(hour, minute=0):
    return datetime.combine(date.today(),
                            datetime.min.time()).timestamp() + hour * 3600 + minute * 60


def test_log_and_daily_summary(tmp_path):
    st = StatsTracker(str(tmp_path / "s.csv"))
    st.log("session", _ts(9), _ts(10, 30))    # 1.5 h desk
    st.log("break", _ts(10, 30), _ts(10, 45))  # 15 min break
    st.log("session", _ts(10, 45), _ts(12))    # 1.25 h desk
    s = st.daily_summary()
    assert s["sessions"] == 2
    assert s["breaks"] == 1
    assert s["desk_hours"] == 2.75
    assert s["break_minutes"] == 15.0
    assert s["longest_focus_minutes"] == 90.0


def test_ignores_other_days(tmp_path):
    st = StatsTracker(str(tmp_path / "s.csv"))
    st.log("session", _ts(9) - 86400, _ts(10) - 86400)  # yesterday
    s = st.daily_summary()
    assert s["sessions"] == 0
    assert s["desk_hours"] == 0.0


def test_zero_or_negative_duration_not_logged(tmp_path):
    st = StatsTracker(str(tmp_path / "s.csv"))
    st.log("session", _ts(9), _ts(9))
    st.log("break", _ts(9), _ts(8))
    assert st.daily_summary()["sessions"] == 0


def test_format_summary_renders(tmp_path):
    st = StatsTracker(str(tmp_path / "s.csv"))
    st.log("session", _ts(9), _ts(11))
    out = format_summary(st.daily_summary())
    assert "2.00 h" in out and "1 sessions" in out
