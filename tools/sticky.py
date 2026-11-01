import json
import subprocess
import sys
from pathlib import Path

STICKY_SCRIPT = Path(__file__).resolve().parent.parent / "Python Projects" / "Sticky Notes" / "main.py"
SAVE_FILE = Path.home() / ".config" / "janet_sticky" / "notes.json"


def _get_pythonw() -> str:
    python_exe = Path(sys.executable)
    pythonw = python_exe.with_name("pythonw.exe")
    return str(pythonw if pythonw.exists() else python_exe)


def manage_sticky(action: str = "") -> str:
    action = (action or "").strip()
    cmd = action.lower()

    if not cmd or cmd == "open":
        flags = subprocess.CREATE_NO_WINDOW | subprocess.DETACHED_PROCESS if sys.platform == "win32" else 0
        subprocess.Popen(
            [_get_pythonw(), str(STICKY_SCRIPT)],
            creationflags=flags,
            close_fds=True,
        )
        return "Opened Sticky Notes."

    if cmd == "read" or cmd == "show":
        if not SAVE_FILE.exists():
            return "Sticky note is currently empty."
        try:
            data = json.loads(SAVE_FILE.read_text(encoding="utf-8"))
            content = data.get("content", "").strip()
            return f"Sticky Note Content:\n{content}" if content else "Sticky note is currently empty."
        except (json.JSONDecodeError, OSError):
            return "Could not read sticky note."

    if cmd.startswith("add "):
        note_text = action.split(maxsplit=1)[1].strip()
        SAVE_FILE.parent.mkdir(parents=True, exist_ok=True)
        existing = ""
        if SAVE_FILE.exists():
            try:
                existing = json.loads(SAVE_FILE.read_text(encoding="utf-8")).get("content", "").strip()
            except (json.JSONDecodeError, OSError):
                pass
        updated = f"{existing}\n{note_text}".strip() if existing else note_text
        SAVE_FILE.write_text(json.dumps({"content": updated}), encoding="utf-8")
        return f"Appended to Sticky Notes: '{note_text}'"

    if cmd == "clear":
        SAVE_FILE.parent.mkdir(parents=True, exist_ok=True)
        SAVE_FILE.write_text(json.dumps({"content": ""}), encoding="utf-8")
        return "Cleared Sticky Notes."

    return "Unknown sticky notes command. Use: 'sticky notes' (or 'sticky notes open'), 'sticky notes read', 'sticky notes add <text>', or 'sticky notes clear'."
