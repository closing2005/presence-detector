"""Presence state machine with time-based hysteresis.

States: PRESENT <-> AWAY. A transition only fires after the new observation
persists for a configurable duration, which filters out detection flicker
(e.g. briefly looking away from the camera).

This module has no OpenCV dependency so it can be unit-tested in CI.
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class PresenceConfig:
    away_after: float = 5.0     # seconds of continuous absence before AWAY
    present_after: float = 1.0  # seconds of continuous presence before PRESENT


class PresenceStateMachine:
    PRESENT = "present"
    AWAY = "away"

    def __init__(self, config: Optional[PresenceConfig] = None):
        self.config = config or PresenceConfig()
        self.state = self.PRESENT
        self._candidate: Optional[str] = None
        self._candidate_since: float = 0.0

    def update(self, detected: bool, now: float) -> Optional[str]:
        """Feed one observation.

        Returns the new state ("present"/"away") exactly once per transition,
        otherwise None.
        """
        observed = self.PRESENT if detected else self.AWAY

        if observed == self.state:
            self._candidate = None
            return None

        # Observation disagrees with the current state: (re)start candidacy.
        if self._candidate != observed:
            self._candidate = observed
            self._candidate_since = now
            return None

        threshold = (self.config.away_after if observed == self.AWAY
                     else self.config.present_after)
        if now - self._candidate_since >= threshold:
            self.state = observed
            self._candidate = None
            return self.state
        return None
