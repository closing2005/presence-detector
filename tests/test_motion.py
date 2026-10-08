"""Unit tests for the motion fallback detector (synthetic frames only)."""
import sys
import os

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from motion import MotionDetector


def black(h=120, w=160):
    return np.zeros((h, w, 3), dtype=np.uint8)


def settle(md, frame, n=10):
    for _ in range(n):
        md.motion_detected(frame)


def test_static_frames_no_motion():
    md = MotionDetector()
    f = black()
    settle(md, f)
    assert not md.motion_detected(f)


def test_moving_object_detected():
    md = MotionDetector()
    f = black()
    settle(md, f)
    f2 = f.copy()
    f2[40:80, 60:100] = 255  # ~8% of pixels change, well above min_ratio
    assert md.motion_detected(f2)


def test_tiny_change_ignored():
    md = MotionDetector(min_ratio=0.05)
    f = black()
    settle(md, f)
    f2 = f.copy()
    f2[0:5, 0:5] = 255  # 25 px / 19200 = 0.13% < 5%
    assert not md.motion_detected(f2)


def test_background_adapts_after_object_leaves():
    md = MotionDetector(learning_rate=0.5)  # fast for the test
    f = black()
    settle(md, f)
    f2 = f.copy()
    f2[40:80, 60:100] = 255
    assert md.motion_detected(f2)
    # object leaves; background re-adapts to the empty frame
    for _ in range(30):
        md.motion_detected(f)
    assert not md.motion_detected(f)
