import os
import signal
import subprocess
import sys
from pathlib import Path

ORGANIZER_DIR = Path(__file__).resolve().parent.parent / "Python Projects" / "Auto Organizer"
SCRIPT_PATH = ORGANIZER_DIR / "main.py"
PID_FILE = ORGANIZER_DIR / "organizer.pid"
DEFAULT_DOWNLOADS = Path.home() / "Downloads"


def _get_pythonw() -> str:
    python_exe = Path(sys.executable)
    pythonw = python_exe.with_name("pythonw.exe")
    return str(pythonw if pythonw.exists() else python_exe)


def _is_process_running(pid: int) -> bool:
    if sys.platform == "win32":
        res = subprocess.run(
            ["tasklist", "/FI", f"PID eq {pid}", "/NH"],
            capture_output=True,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
        return str(pid) in res.stdout
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def _read_pid_info() -> tuple[int | None, str]:
    if not PID_FILE.exists():
        return None, str(DEFAULT_DOWNLOADS)
    try:
        raw = PID_FILE.read_text(encoding="utf-8").strip()
        if "|" in raw:
            pid_str, folder = raw.split("|", 1)
            return int(pid_str), folder
        return int(raw), str(DEFAULT_DOWNLOADS)
    except ValueError:
        return None, str(DEFAULT_DOWNLOADS)


def _resolve_target_dir(raw_path: str = "") -> Path | None:
    if not raw_path:
        return DEFAULT_DOWNLOADS
    cleaned = raw_path.strip().strip('"').strip("'")
    target = Path(cleaned).expanduser().resolve()
    if target.exists() and target.is_dir():
        return target
    return None


def manage_organizer(action: str = "") -> str:
    if not action:
        action = input(
            "Janet: Enter auto sort action (start [path] / stop / status / once [path] / or a directory path): "
        ).strip()

    action = action.strip()
    if not action:
        action = "once"

    parts = action.split(maxsplit=1)
    first_word = parts[0].lower()
    rest = parts[1].strip() if len(parts) > 1 else ""

    if first_word == "start":
        pid, current_folder = _read_pid_info()
        if pid and _is_process_running(pid):
            return f"Auto Sort is already running in the background (PID {pid}, watching: {current_folder})."

        target_dir = _resolve_target_dir(rest)
        if target_dir is None:
            return f"Error! Directory not found: '{rest}'"

        flags = subprocess.CREATE_NO_WINDOW | subprocess.DETACHED_PROCESS if sys.platform == "win32" else 0
        proc = subprocess.Popen(
            [_get_pythonw(), str(SCRIPT_PATH), str(target_dir)],
            creationflags=flags,
            close_fds=True,
        )
        PID_FILE.write_text(f"{proc.pid}|{target_dir}", encoding="utf-8")
        return f"Auto Sort watcher started in background (PID {proc.pid}, watching: {target_dir})."

    if first_word == "stop":
        pid, current_folder = _read_pid_info()
        if not pid:
            return "Auto Sort is not currently running."
        try:
            if _is_process_running(pid):
                if sys.platform == "win32":
                    subprocess.run(
                        ["taskkill", "/F", "/PID", str(pid)],
                        capture_output=True,
                        creationflags=subprocess.CREATE_NO_WINDOW,
                    )
                else:
                    os.kill(pid, signal.SIGTERM)
            PID_FILE.unlink(missing_ok=True)
            return f"Auto Sort stopped (PID {pid}, was watching: {current_folder})."
        except Exception as e:
            PID_FILE.unlink(missing_ok=True)
            return f"Stopped Auto Sort (cleaned up PID file: {e})."

    if first_word == "status":
        pid, current_folder = _read_pid_info()
        running = bool(pid and _is_process_running(pid))
        if running:
            return f"Auto Sort Status: Running (PID {pid}) | Watching: {current_folder}"
        return f"Auto Sort Status: Stopped | Default Directory: {DEFAULT_DOWNLOADS}"

    if first_word in ("once", "now", "run"):
        target_dir = _resolve_target_dir(rest)
        if target_dir is None:
            return f"Error! Directory not found: '{rest}'"

        flags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
        subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "--once", str(target_dir)],
            creationflags=flags,
        )
        return f"Sorted existing files in: {target_dir}"

    target_dir = _resolve_target_dir(action)
    if target_dir is not None:
        flags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
        subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "--once", str(target_dir)],
            creationflags=flags,
        )
        return f"Sorted existing files in: {target_dir}"

    return (
        f"Error! Directory or action '{action}' not found. "
        "Use: 'auto sort start [path]', 'auto sort stop', 'auto sort status', 'auto sort once [path]', or 'auto sort <path>'."
    )
