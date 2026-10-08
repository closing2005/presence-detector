"""Human-presence detection from webcam frames.

Uses OpenCV's bundled Haar cascade — no model download required.
Swap in a DNN detector later without touching the callers: the contract
is simply ``present(frame) -> bool``.
"""
import cv2


class FaceDetector:
    def __init__(self, scale_factor=1.1, min_neighbors=5, min_size=(60, 60)):
        cascade_path = (cv2.data.haarcascades
                        + "haarcascade_frontalface_default.xml")
        self._clf = cv2.CascadeClassifier(cascade_path)
        if self._clf.empty():
            raise RuntimeError(
                "failed to load Haar cascade from %s" % cascade_path)
        self._scale_factor = scale_factor
        self._min_neighbors = min_neighbors
        self._min_size = min_size

    def present(self, frame) -> bool:
        """Return True if at least one face is visible in the BGR frame."""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self._clf.detectMultiScale(
            gray,
            scaleFactor=self._scale_factor,
            minNeighbors=self._min_neighbors,
            minSize=self._min_size,
        )
        return len(faces) > 0
