"""Sensor fusion: face detection OR motion detection => present.

Face detection is high-confidence but fails when the user turns away from
the camera. Motion detection (frame differencing) catches those cases.
Either signal means "someone is at the desk".

The returned source ("face"/"motion"/"none") is for logging and tuning;
callers should only branch on the boolean.
"""
from detector import FaceDetector
from motion import MotionDetector


class HybridDetector:
    def __init__(self, face=None, motion=None, motion_kwargs=None):
        self.face = face or FaceDetector()
        self.motion = motion or MotionDetector(**(motion_kwargs or {}))

    def present(self, frame):
        """Return (is_present: bool, source: str)."""
        if self.face.present(frame):
            return True, "face"
        if self.motion.motion_detected(frame):
            return True, "motion"
        return False, "none"
