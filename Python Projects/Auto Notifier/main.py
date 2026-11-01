import json
import os
import random
import subprocess
import sys
import time
from pathlib import Path

CONFIG_FILE = Path(__file__).parent / "config.json"
PID_FILE = Path(__file__).parent / "notifier.pid"

DEFAULT_CONFIG = {
    "interval_hours": 2.0,
    "auto_close_seconds": 15,
    "mode": "sequential",
    "last_index": 0,
    "messages": []
}


def load_config() -> dict:
    if not CONFIG_FILE.exists():
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()
    try:
        return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return DEFAULT_CONFIG.copy()


def save_config(config: dict) -> None:
    try:
        CONFIG_FILE.write_text(json.dumps(config, indent=4), encoding="utf-8")
    except OSError:
        pass


def get_next_message(config: dict) -> str:
    messages = config.get("messages", [])
    if not messages:
        return "Hello, Sir. This is your scheduled reminder from Janet."

    mode = config.get("mode", "sequential")
    if mode == "random":
        return random.choice(messages)

    idx = config.get("last_index", 0) % len(messages)
    message = messages[idx]
    config["last_index"] = (idx + 1) % len(messages)
    save_config(config)
    return message


def show_popup(message: str, auto_close_seconds: int = 15) -> None:
    from PySide6.QtCore import Qt, QTimer, QPoint
    from PySide6.QtGui import QFont, QGuiApplication
    from PySide6.QtWidgets import (
        QApplication,
        QFrame,
        QHBoxLayout,
        QLabel,
        QPushButton,
        QVBoxLayout,
        QWidget,
    )

    app = QApplication.instance() or QApplication(sys.argv)

    window = QWidget()
    window.setWindowTitle("Janet Notifier")
    window.setWindowFlags(
        Qt.WindowType.FramelessWindowHint
        | Qt.WindowType.WindowStaysOnTopHint
        | Qt.WindowType.Tool
    )
    window.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
    window.setFixedSize(360, 140)

    container = QFrame(window)
    container.setGeometry(0, 0, 360, 140)
    container.setStyleSheet(
        """
        QFrame#MainContainer {
            background-color: #282828;
            border: 1px solid #504945;
            border-radius: 10px;
        }
        QFrame#TitleBar {
            background-color: #3c3836;
            border-top-left-radius: 9px;
            border-top-right-radius: 9px;
        }
        QLabel#TitleLabel {
            color: #fabd2f;
            font-family: Consolas, monospace;
            font-size: 11px;
            font-weight: bold;
        }
        QLabel#MessageLabel {
            color: #ebdbb2;
            font-family: Segoe UI, sans-serif;
            font-size: 13px;
        }
        QPushButton#CloseBtn {
            background-color: transparent;
            color: #ebdbb2;
            border: none;
            font-size: 16px;
            font-weight: bold;
            border-radius: 4px;
        }
        QPushButton#CloseBtn:hover {
            background-color: #cc241d;
            color: #ffffff;
        }
        """
    )
    container.setObjectName("MainContainer")

    layout = QVBoxLayout(container)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(0)

    # Title Bar
    title_bar = QFrame()
    title_bar.setObjectName("TitleBar")
    title_bar.setFixedHeight(30)
    title_layout = QHBoxLayout(title_bar)
    title_layout.setContentsMargins(12, 0, 8, 0)

    title_label = QLabel("● JANET // AUTOMATED DISPATCH")
    title_label.setObjectName("TitleLabel")

    close_btn = QPushButton("×")
    close_btn.setObjectName("CloseBtn")
    close_btn.setFixedSize(24, 24)
    close_btn.clicked.connect(app.quit)

    title_layout.addWidget(title_label)
    title_layout.addStretch()
    title_layout.addWidget(close_btn)

    # Message Area
    body_widget = QWidget()
    body_layout = QVBoxLayout(body_widget)
    body_layout.setContentsMargins(16, 12, 16, 12)

    msg_label = QLabel(message)
    msg_label.setObjectName("MessageLabel")
    msg_label.setWordWrap(True)
    msg_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
    body_layout.addWidget(msg_label)

    layout.addWidget(title_bar)
    layout.addWidget(body_widget)

    # Position at bottom-right of primary screen
    screen = QGuiApplication.primaryScreen()
    if screen:
        avail = screen.availableGeometry()
        x = avail.right() - window.width() - 20
        y = avail.bottom() - window.height() - 20
        window.move(QPoint(x, y))

    # Enable dragging via title bar
    drag_pos = {"offset": None}

    def mouse_press(event):
        if event.button() == Qt.MouseButton.LeftButton:
            drag_pos["offset"] = event.globalPosition().toPoint() - window.frameGeometry().topLeft()

    def mouse_move(event):
        if drag_pos["offset"] is not None and event.buttons() & Qt.MouseButton.LeftButton:
            window.move(event.globalPosition().toPoint() - drag_pos["offset"])

    title_bar.mousePressEvent = mouse_press
    title_bar.mouseMoveEvent = mouse_move

    if auto_close_seconds > 0:
        QTimer.singleShot(int(auto_close_seconds * 1000), app.quit)

    window.show()
    app.exec()


def run_daemon() -> None:
    """
    Ultra-lightweight background loop.
    Does NOT import PySide6 in the parent process, keeping RAM usage minimal (~8-10 MB)
    and 0% CPU during sleep. Spawns the popup subprocess only when the timer fires,
    and reclaims 100% of GUI memory immediately after the popup closes.
    """
    load_config()  # Ensure config file is created on first run
    try:
        PID_FILE.write_text(str(os.getpid()), encoding="utf-8")
    except OSError:
        pass

    try:
        while True:
            config = load_config()
            interval_hours = float(config.get("interval_hours", 2.0))
            sleep_seconds = max(5.0, interval_hours * 3600.0)

            time.sleep(sleep_seconds)

            # Reload config after waking in case messages or settings were updated
            config = load_config()
            msg = get_next_message(config)
            auto_close = int(config.get("auto_close_seconds", 15))

            creation_flags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            subprocess.run(
                [sys.executable, str(Path(__file__).resolve()), "--popup", msg, str(auto_close)],
                creationflags=creation_flags,
            )
    finally:
        if PID_FILE.exists():
            try:
                PID_FILE.unlink()
            except OSError:
                pass


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "--popup":
        popup_msg = sys.argv[2] if len(sys.argv) >= 3 else "Hello, Sir."
        popup_timeout = int(sys.argv[3]) if len(sys.argv) >= 4 else 15
        show_popup(popup_msg, popup_timeout)
    elif len(sys.argv) >= 2 and sys.argv[1] == "--test":
        cfg = load_config()
        msg = get_next_message(cfg)
        show_popup(msg, int(cfg.get("auto_close_seconds", 15)))
    else:
        run_daemon()
