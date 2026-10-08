# presence-detector

Webcam presence detection: pause your media when you walk away, resume when
you're back. Pure OpenCV, no cloud, no model download.

## How it works

```
webcam ──► capture thread ──► face detection (5 fps) ──► state machine ──► actions
                                                                    ├── on AWAY:   media_pause / lock
                                                                    └── on PRESENT: media_play
```

- **Face detection** uses OpenCV's bundled Haar cascade — zero setup.
- **State machine** has time-based hysteresis: a transition only fires after
  the new observation persists (`away_after_sec` / `present_after_sec`), so
  brief look-aways don't flicker the state. Unit-tested, camera not required.
- **Detection is throttled** to 5 fps on purpose — presence doesn't need
  30 fps, and this keeps CPU usage negligible on laptops.

## Install

```bash
pip install -r requirements.txt
```

## Usage

```bash
# Dry run first (detects and logs, touches nothing)
python src/main.py --dry-run

# For real
python src/main.py
```

Edit `config.yaml` to tune thresholds and actions:

```yaml
away_after_sec: 5.0
present_after_sec: 1.0
on_away: [media_pause]   # or [lock], or both
on_return: [media_play]
```

## Platform support

| Action | Linux | macOS | Windows |
|--------|-------|-------|---------|
| `media_pause` / `media_play` | playerctl | media key | media key |
| `lock` | loginctl / gnome-screensaver | displaysleep | LockWorkStation |

Actions are best-effort: if a command is missing on your system, it's logged
as unavailable instead of crashing.

## Tests

```bash
pytest -q
```

## License

MIT
