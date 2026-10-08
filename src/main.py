"""presence-detector — pause the world when you walk away.

Threads:
  capture thread  -> grabs frames from the webcam into a shared slot
  main loop       -> runs face detection at detection_fps, feeds the
                     presence state machine, fires configured actions
                     on PRESENT<->AWAY transitions.

Face detection is deliberately throttled (default 5 fps): presence does
not need 30 fps, and this keeps CPU usage negligible on laptops.
"""
import argparse
import signal
import threading
import time

import cv2
import yaml

from actions import run_action
from detector import FaceDetector
from state_machine import PresenceConfig, PresenceStateMachine


class Camera:
    """Latest-frame slot fed by a background capture thread."""

    def __init__(self, index=0):
        self._cap = cv2.VideoCapture(index)
        if not self._cap.isOpened():
            raise RuntimeError("cannot open camera index %d" % index)
        self._lock = threading.Lock()
        self._frame = None
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._loop, daemon=True)

    def start(self):
        self._thread.start()

    def stop(self):
        self._stop.set()
        self._thread.join(timeout=2)
        self._cap.release()

    def _loop(self):
        while not self._stop.is_set():
            ok, frame = self._cap.read()
            if ok:
                with self._lock:
                    self._frame = frame

    def latest(self):
        with self._lock:
            return None if self._frame is None else self._frame.copy()


def load_config(path):
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def main():
    ap = argparse.ArgumentParser(description="Webcam presence detector")
    ap.add_argument("-c", "--config", default="config.yaml")
    ap.add_argument("--dry-run", action="store_true",
                    help="detect and log, but don't run OS actions")
    args = ap.parse_args()

    cfg = load_config(args.config)
    dry_run = args.dry_run or cfg.get("dry_run", False)

    detector = FaceDetector()
    sm = PresenceStateMachine(PresenceConfig(
        away_after=float(cfg.get("away_after_sec", 5.0)),
        present_after=float(cfg.get("present_after_sec", 1.0)),
    ))
    on_away = cfg.get("on_away", ["media_pause"])
    on_return = cfg.get("on_return", ["media_play"])
    fps = float(cfg.get("detection_fps", 5.0))

    cam = Camera(index=int(cfg.get("camera_index", 0)))
    cam.start()
    print("[presence-detector] running (Ctrl+C to stop)%s"
          % (" [dry-run]" if dry_run else ""))

    stop = threading.Event()

    def _sig(*_):
        stop.set()
    signal.signal(signal.SIGINT, _sig)
    signal.signal(signal.SIGTERM, _sig)

    try:
        while not stop.is_set():
            frame = cam.latest()
            if frame is not None:
                transition = sm.update(detector.present(frame), time.monotonic())
                if transition == PresenceStateMachine.AWAY:
                    print("[state] -> AWAY")
                    for a in on_away:
                        run_action(a, dry_run=dry_run)
                elif transition == PresenceStateMachine.PRESENT:
                    print("[state] <- PRESENT")
                    for a in on_return:
                        run_action(a, dry_run=dry_run)
            time.sleep(1.0 / fps)
    finally:
        cam.stop()
        print("[presence-detector] stopped")


if __name__ == "__main__":
    main()
