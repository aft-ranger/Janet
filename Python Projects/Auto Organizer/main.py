from pathlib import Path
import os
import shutil
import sys
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

DEFAULT_DOWNLOADS = Path.home() / "Downloads"
TARGET_DIR = DEFAULT_DOWNLOADS
PID_FILE = Path(__file__).parent / "organizer.pid"


class Handler(FileSystemEventHandler):
    def on_created(self, event):
        print(f"CREATED: {event.src_path}")

        if not event.is_directory:
            time.sleep(1)
            organize_downloads(event.src_path)

    def on_moved(self, event):
        print(f"MOVED: {event.dest_path}")

        if not event.is_directory:
            time.sleep(1)
            organize_downloads(event.dest_path)


RULES = {
    "PDFs": [".pdf"],
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff"],
    "Documents": [".doc", ".docx", ".txt"],
    "Spreadsheets": [".xls", ".xlsx", ".csv"],
    "Presentations": [".ppt", ".pptx"],
    "Archives": [".zip", ".tar", ".gz", ".rar"],
    "Setups": [".exe", ".msi", ".msix"],
    "Videos": [".mp4", ".mkv", ".avi", ".mov", ".flv"],
    "Audio": [".mp3", ".wav", ".aac", ".flac"],
}


def organize_existing_files(directory: Path = None):
    target = directory or TARGET_DIR
    if not target.exists():
        return
    for file in target.iterdir():
        if file.is_file():
            organize_downloads(file, target)


def organize_downloads(file_path: str | Path, base_dir: Path = None):
    file = Path(file_path)
    target = base_dir or file.parent
    if file.is_file():
        for category, extensions in RULES.items():
            if file.suffix.lower() in extensions:
                sort_files(file, category, target)
                break


def sort_files(file: Path, category: str, base_dir: Path = None):
    target = base_dir or TARGET_DIR
    category_path = target / category
    category_path.mkdir(exist_ok=True)
    try:
        base_destination = category_path / file.name
        destination = get_unique_path(base_destination)
        shutil.move(str(file), str(destination))
    except PermissionError as e:
        print(f"Error moving {file.name}: {e}")
    except FileNotFoundError:
        pass
    except OSError as e:
        print(f"Error moving {file.name}: {e}")


def get_unique_path(destination: Path) -> Path:
    counter = 1
    original_destination = destination
    while destination.exists():
        destination = original_destination.with_name(
            f"{original_destination.stem} ({counter}){original_destination.suffix}"
        )
        counter += 1
    return destination


if __name__ == "__main__":
    args = sys.argv[1:]
    once_mode = False

    if "--once" in args:
        once_mode = True
        args.remove("--once")

    if args:
        TARGET_DIR = Path(" ".join(args)).expanduser().resolve()
    else:
        TARGET_DIR = DEFAULT_DOWNLOADS

    if not TARGET_DIR.exists() or not TARGET_DIR.is_dir():
        print(f"Janet: Error! Directory not found: {TARGET_DIR}")
        sys.exit(1)

    if once_mode:
        organize_existing_files(TARGET_DIR)
        sys.exit(0)

    print(f"Watching: {TARGET_DIR}")
    try:
        PID_FILE.write_text(f"{os.getpid()}|{TARGET_DIR}", encoding="utf-8")
    except OSError:
        pass

    organize_existing_files(TARGET_DIR)

    observer = Observer()
    observer.schedule(Handler(), str(TARGET_DIR), recursive=False)
    observer.start()
    print("Watcher started...")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    finally:
        if PID_FILE.exists():
            try:
                PID_FILE.unlink()
            except OSError:
                pass

    observer.join()
