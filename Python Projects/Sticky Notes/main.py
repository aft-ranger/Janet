import json
from pathlib import Path
import tkinter as tk

SAVE_FILE = Path.home() / ".config" / "janet_sticky" / "notes.json"


def save_notes(text_widget):
  SAVE_FILE.parent.mkdir(parents=True, exist_ok=True)
  data = {"content": text_widget.get("1.0", tk.END).strip()}
  SAVE_FILE.write_text(json.dumps(data))


def load_notes(text_widget):
  if SAVE_FILE.exists():
    try:
      data = json.loads(SAVE_FILE.read_text())
      text_widget.insert("1.0", data.get("content", ""))
    except json.JSONDecodeError:
      pass


def create_sticky():
  root = tk.Tk()
  root.title("Janet Sticky")
  root.overrideredirect(True)  # Frameless
  root.attributes("-topmost", True)  # Always on top
  root.geometry("250x250+100+100")
  root.configure(bg="#282828")

  # Simple title bar to drag/close the window since borders are removed
  title_bar = tk.Frame(root, bg="#3c3836", height=20)
  title_bar.pack(fill="x", side="top")

  def close_app():
    save_notes(text_area)
    root.destroy()

  close_btn = tk.Button(
      title_bar,
      text="×",
      command=close_app,
      bg="#3c3836",
      fg="#ebdbb2",
      bd=0,
      activebackground="#cc241d",
  )
  close_btn.pack(side="right", padx=5)

  # Text area for editing
  text_area = tk.Text(
      root,
      wrap="word",
      bg="#282828",
      fg="#ebdbb2",
      insertbackground="#ebdbb2",
      bd=0,
      highlightthickness=0,
      font=("monospace", 10),
  )
  text_area.pack(fill="both", expand=True, padx=5, pady=5)

  load_notes(text_area)

  # Auto-save on every keystroke
  text_area.bind("<KeyRelease>", lambda e: save_notes(text_area))

  # Make window draggable
  def start_move(event):
    root.x = event.x
    root.y = event.y

  def do_move(event):
    x = root.winfo_pointerx() - root.x
    y = root.winfo_pointery() - root.y
    root.geometry(f"+{x}+{y}")

  title_bar.bind("<Button-1>", start_move)
  title_bar.bind("<B1-Motion>", do_move)

  root.mainloop()


if __name__ == "__main__":
  create_sticky()