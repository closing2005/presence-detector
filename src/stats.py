"""Session statistics: log desk sessions and breaks to CSV.

Every PRESENT->AWAY transition closes a "session" (focused desk time);
every AWAY->PRESENT closes a "break". `daily_summary()` aggregates one
day into desk hours, break count, and longest focus streak.
"""
import csv
import os
from datetime import date, datetime


class StatsTracker:
    HEADER = ["date", "start", "end", "kind", "duration_sec"]

    def __init__(self, path="sessions.csv"):
        self.path = path
        if not os.path.exists(path):
            with open(path, "w", newline="", encoding="utf-8") as f:
                csv.writer(f).writerow(self.HEADER)

    def log(self, kind, start_ts, end_ts):
        """kind: "session" or "break". Timestamps are epoch seconds."""
        if end_ts <= start_ts:
            return
        with open(self.path, "a", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow([
                datetime.fromtimestamp(start_ts).date().isoformat(),
                datetime.fromtimestamp(start_ts).isoformat(timespec="seconds"),
                datetime.fromtimestamp(end_ts).isoformat(timespec="seconds"),
                kind,
                round(end_ts - start_ts, 1),
            ])

    def daily_summary(self, day=None):
        day = day or date.today().isoformat()
        sessions = breaks = 0
        desk_sec = break_sec = longest = 0.0
        with open(self.path, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                if row["date"] != day:
                    continue
                d = float(row["duration_sec"])
                if row["kind"] == "session":
                    sessions += 1
                    desk_sec += d
                    longest = max(longest, d)
                elif row["kind"] == "break":
                    breaks += 1
                    break_sec += d
        return {
            "date": day,
            "sessions": sessions,
            "breaks": breaks,
            "desk_hours": round(desk_sec / 3600, 2),
            "break_minutes": round(break_sec / 60, 1),
            "longest_focus_minutes": round(longest / 60, 1),
        }


def format_summary(s):
    return (
        "Presence report for %(date)s\n"
        "  desk time:     %(desk_hours).2f h across %(sessions)d sessions\n"
        "  breaks:        %(breaks)d (%(break_minutes).1f min total)\n"
        "  longest focus: %(longest_focus_minutes).1f min" % s
    )
