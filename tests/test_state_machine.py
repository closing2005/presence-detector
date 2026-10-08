"""Unit tests for the presence state machine (no camera needed)."""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from state_machine import PresenceConfig, PresenceStateMachine


def feed(sm, observations, start=0.0, step=0.5):
    """Feed a list of bools; return list of transitions."""
    out = []
    t = start
    for obs in observations:
        r = sm.update(obs, t)
        if r:
            out.append((round(t, 2), r))
        t += step
    return out


def test_starts_present_no_spurious_transition():
    sm = PresenceStateMachine()
    assert feed(sm, [True] * 10) == []


def test_goes_away_after_threshold():
    sm = PresenceStateMachine(PresenceConfig(away_after=2.0, present_after=1.0))
    # 2.0s of absence at 0.5s steps -> transition at t=2.0
    transitions = feed(sm, [False] * 6)
    assert transitions == [(2.0, "away")]


def test_flicker_does_not_trigger_away():
    sm = PresenceStateMachine(PresenceConfig(away_after=3.0, present_after=1.0))
    # absence never persists 3s: a True resets the candidacy
    obs = [False, False, True, False, False, True, False, False]
    assert feed(sm, obs) == []
    assert sm.state == "present"


def test_returns_present_faster_than_away():
    sm = PresenceStateMachine(PresenceConfig(away_after=5.0, present_after=1.0))
    feed(sm, [False] * 12)          # -> away at t=5.0
    assert sm.state == "away"
    transitions = feed(sm, [True] * 4, start=6.0)
    assert transitions == [(7.0, "present")]


def test_transition_fires_exactly_once():
    sm = PresenceStateMachine(PresenceConfig(away_after=1.0, present_after=1.0))
    transitions = feed(sm, [False] * 10)
    assert transitions == [(1.0, "away")]


def test_observation_matching_state_resets_candidacy():
    sm = PresenceStateMachine(PresenceConfig(away_after=2.0, present_after=1.0))
    sm.update(False, 0.0)   # candidacy starts
    sm.update(True, 0.5)    # back to present -> candidacy reset
    transitions = feed(sm, [False] * 6, start=1.0)
    assert transitions == [(3.0, "away")]
