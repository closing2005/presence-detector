"""OS actions triggered on presence transitions.

Best-effort and cross-platform: every action returns True on success,
False when the platform/command is unavailable. Nothing here raises.
"""
import platform
import shutil
import subprocess


def _run(*cmd):
    if not shutil.which(cmd[0]):
        return False
    try:
        subprocess.run(list(cmd), check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                       timeout=10)
        return True
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired,
            OSError):
        return False


def lock_screen() -> bool:
    """Lock the workstation."""
    system = platform.system()
    if system == "Linux":
        return (_run("loginctl", "lock-session")
                or _run("gnome-screensaver-command", "--lock")
                or _run("xdg-screensaver", "lock"))
    if system == "Darwin":
        return _run("pmset", "displaysleepnow")
    if system == "Windows":
        return _run("rundll32.exe", "user32.dll,LockWorkStation")
    return False


def media_pause() -> bool:
    """Pause currently playing media, if any."""
    system = platform.system()
    if system == "Linux":
        return _run("playerctl", "pause")
    if system == "Darwin":
        return _run("osascript", "-e",
                    'tell application "System Events" to key code 16')
    if system == "Windows":
        # Play/Pause media key via PowerShell
        return _run("powershell", "-c",
                    "(New-Object -ComObject WScript.Shell)"
                    ".SendKeys([char]179)")
    return False


def media_play() -> bool:
    """Resume media playback."""
    system = platform.system()
    if system == "Linux":
        return _run("playerctl", "play")
    if system == "Darwin":
        return _run("osascript", "-e",
                    'tell application "System Events" to key code 16')
    if system == "Windows":
        return _run("powershell", "-c",
                    "(New-Object -ComObject WScript.Shell)"
                    ".SendKeys([char]179)")
    return False


ACTIONS = {
    "lock": lock_screen,
    "media_pause": media_pause,
    "media_play": media_play,
}


def run_action(name: str, dry_run: bool = False) -> bool:
    """Run a named action. In dry-run mode just report what would happen."""
    fn = ACTIONS.get(name)
    if fn is None:
        print("[action] unknown action: %s" % name)
        return False
    if dry_run:
        print("[dry-run] would run action: %s" % name)
        return True
    ok = fn()
    print("[action] %s -> %s" % (name, "ok" if ok else "unavailable"))
    return ok
