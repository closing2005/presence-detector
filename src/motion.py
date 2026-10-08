"""Motion-based presence fallback via frame differencing.

Catches the case face detection misses: user at the desk with their back
to the camera, typing. Compares each frame against a running background
model; a large enough pixel change means "someone is moving here".

Design notes:
- Background adapts FAST (default alpha=0.1): when the user leaves, the
  model becomes "empty desk" within ~2s, so the walk-away transient is
  shorter than the state machine's away_after and doesn't block AWAY.
- Known limitation: sitting perfectly still, back to the camera, for a
  minute will read as away. Face detection remains the primary signal.
"""
import cv2


class MotionDetector:
    def __init__(self, threshold=25, min_ratio=0.005, learning_rate=0.1):
        self._threshold = threshold
        self._min_ratio = min_ratio
        self._learning_rate = learning_rate
        self._bg = None  # running background model, float32 grayscale

    def _prepare(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        return cv2.GaussianBlur(gray, (21, 21), 0)

    def motion_detected(self, frame) -> bool:
        gray = self._prepare(frame)
        if self._bg is None:
            self._bg = gray.astype("float32")
            return False
        cv2.accumulateWeighted(gray, self._bg, self._learning_rate)
        diff = cv2.absdiff(gray, cv2.convertScaleAbs(self._bg))
        _, thresh = cv2.threshold(diff, self._threshold, 255,
                                  cv2.THRESH_BINARY)
        ratio = cv2.countNonZero(thresh) / thresh.size
        return ratio > self._min_ratio
