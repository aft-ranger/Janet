import json
import os
import signal
import subprocess
import sys
from pathlib import Path

NOTIFIER_DIR = Path(__file__).resolve().parent.parent / "Python Projects" / "Auto Notifier"
SCRIPT_PATH = NOTIFIER_DIR / "main.py"
CONFIG_FILE = NOTIFIER_DIR / "config.json"
PID_FILE = NOTIFIER_DIR / "notifier.pid"


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


def _load_config() -> dict:
    if CONFIG_FILE.exists():
        try:
            return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return {
        "interval_hours": 2.0,
        "auto_close_seconds": 15,
        "mode": "sequential",
        "last_index": 0,
        "messages": [],
    }


def _save_config(config: dict) -> None:
    CONFIG_FILE.write_text(json.dumps(config, indent=4), encoding="utf-8")


def manage_notifier(action: str = "") -> str:
    if not action:
        action = input(
            "Janet: Enter notifier action (start / stop / status / test / list / add <msg> / delete <num|msg> / interval <hours>): "
        ).strip()

    action = action.strip()
    cmd = action.lower()

    if cmd == "start":
        if PID_FILE.exists():
            try:
                pid = int(PID_FILE.read_text(encoding="utf-8").strip())
                if _is_process_running(pid):
                    return f"Auto Notifier is already running in the background (PID {pid})."
            except ValueError:
                pass

        flags = subprocess.CREATE_NO_WINDOW | subprocess.DETACHED_PROCESS if sys.platform == "win32" else 0
        proc = subprocess.Popen(
            [_get_pythonw(), str(SCRIPT_PATH)],
            creationflags=flags,
            close_fds=True,
        )
        PID_FILE.write_text(str(proc.pid), encoding="utf-8")
        cfg = _load_config()
        return f"Auto Notifier started in background (PID {proc.pid}, interval: {cfg.get('interval_hours', 2.0)}h)."

    if cmd == "stop":
        if not PID_FILE.exists():
            return "Auto Notifier is not currently running."
        try:
            pid = int(PID_FILE.read_text(encoding="utf-8").strip())
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
            return f"Auto Notifier stopped (PID {pid})."
        except Exception as e:
            PID_FILE.unlink(missing_ok=True)
            return f"Stopped notifier (cleaned up PID file: {e})."

    if cmd == "status":
        cfg = _load_config()
        running = False
        pid = None
        if PID_FILE.exists():
            try:
                pid = int(PID_FILE.read_text(encoding="utf-8").strip())
                running = _is_process_running(pid)
            except ValueError:
                pass
        state = f"Running (PID {pid})" if running else "Stopped"
        return (
            f"Status: {state} | Interval: {cfg.get('interval_hours', 2.0)}h | "
            f"Messages: {len(cfg.get('messages', []))} configured."
        )

    if cmd == "test":
        flags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
        subprocess.Popen(
            [_get_pythonw(), str(SCRIPT_PATH), "--test"],
            creationflags=flags,
        )
        return "Displaying test notification popup."

    if cmd.startswith("interval "):
        val_str = action.split(maxsplit=1)[1].strip()
        try:
            hours = float(val_str)
            if hours <= 0:
                return "Interval must be greater than 0 hours."
            cfg = _load_config()
            cfg["interval_hours"] = hours
            _save_config(cfg)
            return f"Auto Notifier interval updated to {hours} hours."
        except ValueError:
            return "Invalid number. Usage: notifier interval <hours> (e.g., notifier interval 1.5)"

    if cmd.startswith("add "):
        msg = action.split(maxsplit=1)[1].strip()
        if not msg:
            return "Please provide a message to add."
        cfg = _load_config()
        cfg.setdefault("messages", []).append(msg)
        _save_config(cfg)
        return f"Added message to Auto Notifier: '{msg}'"

    if cmd.startswith("delete ") or cmd.startswith("remove "):
        target = action.split(maxsplit=1)[1].strip()
        if not target:
            return "Please specify the message number or text to delete."
        cfg = _load_config()
        msgs = cfg.get("messages", [])
        if not msgs:
            return "No messages configured to delete."

        if target.isdigit():
            idx = int(target) - 1
            if 0 <= idx < len(msgs):
                removed = msgs.pop(idx)
                cfg["last_index"] = 0
                _save_config(cfg)
                return f"Deleted message #{idx + 1}: '{removed}'"
            return f"Invalid message number. Choose between 1 and {len(msgs)}."

        for i, m in enumerate(msgs):
            if m.lower() == target.lower():
                removed = msgs.pop(i)
                cfg["last_index"] = 0
                _save_config(cfg)
                return f"Deleted message: '{removed}'"

        return f"Message '{target}' not found. Use 'notifier list' to see message numbers."

    if cmd == "clear":
        cfg = _load_config()
        cfg["messages"] = []
        cfg["last_index"] = 0
        _save_config(cfg)
        return "Cleared all messages from Auto Notifier."

    if cmd == "list":
        cfg = _load_config()
        msgs = cfg.get("messages", [])
        if not msgs:
            return "No messages configured."
        formatted = "\n".join(f"  {i + 1}. {m}" for i, m in enumerate(msgs))
        return f"Configured Messages:\n{formatted}"

    return (
        "Unknown notifier command. Available actions: "
        "'start', 'stop', 'status', 'test', 'list', 'add <message>', 'delete <number|message>', 'clear', 'interval <hours>'."
    )
