import sys
import os
import shutil
import random
from datetime import datetime

all_commands = ("help", "todo", "organize", "dummy", "log", "find", "status")
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TODO_FILE = os.path.join(SCRIPT_DIR, "todo.txt")
LOG_FILE = os.path.join(SCRIPT_DIR, "organizer_log.txt")

username = os.getlogin()
DEFAULT_DOWNLOADS = os.path.expanduser("~/Downloads")
DEFAULT_TARGET = os.path.expanduser("~/OrganizedFiles")

SIZE_THRESHOLD_MB = 500

GAME_KEYWORDS = [
    "game", "steam", "epic", "gog", "ubisoft", "ea", "blizzard",
    "riot", "minecraft", "roblox", "patch", "mod", "repack", "setup", "launcher"
]

EXTENSIONS = {
    "images": [".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".bmp", ".ico"],
    "documents": [".pdf", ".docx", ".txt", ".xlsx", ".pptx", ".csv", ".md"],
    "spreadsheets": [".xlsx", ".xls", ".csv", ".ods"],
    "presentations": [".pptx", ".ppt", ".odp"],
    "videos": [".mp4", ".mkv", ".mov", ".avi", ".wmv", ".flv"],
    "music": [".mp3", ".wav", ".flac", ".m4a", ".aac"],
    "archives": [".zip", ".rar", ".7z", ".tar", ".gz"],
    "apps": [".msi", ".dmg", ".pkg", ".deb", ".rpm", ".exe"],
    "games": [
        ".rom", ".nes", ".sfc", ".smc", ".gb", ".gbc", ".gba", ".n64", ".z64",
        ".nds", ".3ds", ".cia", ".iso", ".rvz", ".wbfs", ".bin", ".cue", ".v64"
    ],
    "code": [".py", ".js", ".html", ".css", ".cpp", ".java", ".ts", ".json", ".sh"],
    "fonts": [".ttf", ".otf", ".woff", ".woff2"],
    "ebooks": [".epub", ".mobi", ".azw3"],
    "design": [".psd", ".ai", ".fig", ".sketch"]
}


def log_action(message):
    """Writes an action summary to the global log file."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] {message}\n")


def border():
    print("=" * 100)


def clear_terminal():
    os.system("cls" if os.name == "nt" else "clear")


def command_help():
    print("\n")
    print(f"Welcome back, {username}!")
    print("Usage: utils <command> [args] [flags]")
    print("\nChoices")
    border()

    for command in all_commands:
        print(f"- {command}")

    print("\nFile Organization Pattern:")
    print("  utils organize                  -> Organize Downloads")
    print("  utils organize .                -> Organize current folder in-place")
    print("  utils organize <src>            -> Organize specific folder to default target")
    print("  utils organize <src> <target>   -> Organize to specific target")
    print("  Flags: --safe, --dry-run")

    print("\nTodo Pattern:")
    print("  utils todo                      -> Show all")
    print("  utils todo <task>               -> Add new task")
    print("  utils todo delete <num>         -> Remove task")
    print("  utils todo complete <num>       -> Mark finished")

    print("\nTesting Tools:")
    print("  utils dummy                     -> Create 10 test files here")
    print("  utils dummy <count>             -> Create X test files here")

    print("\nUtility Helpers:")
    print("  utils log                      -> Show last 20 log entries")
    print("  utils log <count>              -> Show last N log entries")
    print("  utils find <keyword> [path]    -> Search files by name")
    print("  utils status [path]            -> Show file category counts")
    print("  Flags for organize: --safe, --dry-run, --report")


def load_tasks():
    if not os.path.exists(TODO_FILE): return []
    with open(TODO_FILE, "r") as f:
        return [line.strip() for line in f.readlines()]


def save_tasks(tasks):
    with open(TODO_FILE, "w") as f:
        for task in tasks: f.write(task + "\n")


def command_todo():
    tasks = load_tasks()
    if len(sys.argv) == 2:
        if not tasks: print("List is empty."); return
        print("\n--- To-Do ---\n")
        for i, t in enumerate(tasks, 1): print(f"{i}. {t}")
    elif len(sys.argv) >= 4 and sys.argv[2].lower() == "delete":
        try:
            removed = tasks.pop(int(sys.argv[3]) - 1)
            save_tasks(tasks)
            print(f"Deleted: {removed}")
        except:
            print("Invalid task number.")
    elif len(sys.argv) >= 4 and sys.argv[2].lower() == "complete":
        try:
            idx = int(sys.argv[3]) - 1
            tasks[idx] = tasks[idx].replace("[ ]", "[x]", 1)
            save_tasks(tasks)
            print(f"Completed: {tasks[idx]}")
        except:
            print("Invalid task number.")
    else:
        task = " ".join(sys.argv[2:])
        if task:
            tasks.append(f"[ ] {task}")
            save_tasks(tasks)
            print(f"Added: {task}")


def command_dummy():
    count = 10
    path = "."

    if len(sys.argv) >= 3:
        try:
            count = int(sys.argv[2])
        except ValueError:
            pass

    if not os.path.exists(path): os.makedirs(path)

    print(f"Generating {count} dummy files...")
    sample_names = ["report", "photo", "vibe", "project", "data", "script", "backup", "notes"]

    for i in range(count):
        category = random.choice(list(EXTENSIONS.keys()))
        ext = random.choice(EXTENSIONS[category])
        name = f"{random.choice(sample_names)}_{random.randint(100, 999)}{ext}"
        with open(os.path.join(path, name), "w") as f:
            f.write("Dummy test file.")
        print(f"Created: {name}")
    border()


def load_log_entries(count=20):
    if not os.path.exists(LOG_FILE):
        return []
    with open(LOG_FILE, "r") as f:
        lines = [line.rstrip("\n") for line in f.readlines()]
    return lines[-count:]


def command_log():
    count = 20
    if len(sys.argv) >= 3:
        try:
            count = int(sys.argv[2])
        except ValueError:
            pass

    entries = load_log_entries(count)
    if not entries:
        print("No log entries found.")
        return

    print(f"\n--- Last {len(entries)} log entries ---\n")
    for item in entries:
        print(item)


def command_find():
    if len(sys.argv) < 3:
        print("Usage: utils find <keyword> [path]")
        return

    keyword = sys.argv[2]
    path = sys.argv[3] if len(sys.argv) >= 4 else "."

    if not os.path.exists(path):
        print(f"Path not found: {path}")
        return

    print(f"Searching for '{keyword}' in {path}...")
    matches = []
    for root, _, files in os.walk(path):
        for filename in files:
            if keyword.lower() in filename.lower():
                matches.append(os.path.join(root, filename))

    if not matches:
        print(f"No files found matching '{keyword}'.")
        return

    print(f"Found {len(matches)} files:")
    for match in matches:
        print(match)


def summarize_folder(path):
    summary = {}
    for root, _, files in os.walk(path):
        for filename in files:
            ext = os.path.splitext(filename)[1].lower()
            category = "others"
            for cat, extensions in EXTENSIONS.items():
                if ext in extensions:
                    category = cat
                    break
            summary[category] = summary.get(category, 0) + 1
    return summary


def command_status():
    path = sys.argv[2] if len(sys.argv) >= 3 else DEFAULT_DOWNLOADS
    if not os.path.exists(path):
        print(f"Path not found: {path}")
        return

    summary = summarize_folder(path)
    total = sum(summary.values())

    print(f"\nStatus for: {path}")
    border()
    for category, count in sorted(summary.items(), key=lambda item: (-item[1], item[0])):
        print(f"{category.title():<15}: {count}")
    border()
    print(f"Total files: {total}")


def organize_files(source_dir, target_dir, safe_mode=False, dry_run=False, report=False):
    if dry_run: print("!!! DRY RUN MODE ENABLED !!!")

    # Critical: Normalize paths to handle relative '.' input
    source_dir = os.path.abspath(os.path.expanduser(source_dir))
    target_dir = os.path.abspath(os.path.expanduser(target_dir))

    print(f"Scanning: {source_dir}")
    print(f"Target:   {target_dir}")

    if not os.path.exists(source_dir):
        print(f"Error: Source '{source_dir}' not found.")
        return

    # List of folder names that we should NOT move into themselves
    protected_folders = set(EXTENSIONS.keys())
    protected_folders.update(["others", "folders", "review_large_files", "bin"])

    files_moved = 0
    category_counts = {}

    for filename in os.listdir(source_dir):
        file_path = os.path.join(source_dir, filename)

        # 1. Skip logic: Don't move the log, the script folder, or existing category folders
        if filename == "organizer_log.txt" or filename == "utils.bat": continue
        if os.path.abspath(file_path) == target_dir: continue
        if filename in protected_folders and os.path.abspath(os.path.join(source_dir, filename)) == os.path.abspath(
                os.path.join(target_dir, filename)):
            continue

        category = "others"

        if os.path.isdir(file_path):
            category = "folders"
        else:
            file_ext = os.path.splitext(filename)[1].lower()
            file_size_mb = os.path.getsize(file_path) / (1024 * 1024)

            if safe_mode and file_size_mb > SIZE_THRESHOLD_MB:
                category = "review_large_files"
            elif file_ext == ".exe":
                category = "games" if any(k in filename.lower() for k in GAME_KEYWORDS) else "apps"
            else:
                for cat, extensions in EXTENSIONS.items():
                    if file_ext in extensions:
                        category = cat
                        break

        category_path = os.path.join(target_dir, category)
        if not dry_run and not os.path.exists(category_path):
            os.makedirs(category_path)

        destination = os.path.join(category_path, filename)

        # Collision handling
        base, ext = os.path.splitext(filename)
        counter = 1
        while os.path.exists(destination):
            destination = os.path.join(category_path, f"{base}_{counter}{ext}")
            counter += 1

        try:
            if dry_run:
                print(f"[PREVIEW] {filename} -> {category.upper()}")
            else:
                shutil.move(file_path, destination)
                print(f"Moved [{category.upper()}]: {filename}")
                log_action(f"Moved {filename} to {category}")
                files_moved += 1

            category_counts[category] = category_counts.get(category, 0) + 1
        except Exception as e:
            print(f"Error moving {filename}: {e}")

    border()
    print(f"Complete! Items processed: {files_moved}")

    if report:
        print("\nOrganize Summary")
        border()
        for category, count in sorted(category_counts.items(), key=lambda item: (-item[1], item[0])):
            print(f"{category.title():<20}: {count}")
        border()


def command_organize():
    safe = "--safe" in sys.argv
    dry = "--dry-run" in sys.argv
    report = "--report" in sys.argv
    clean_args = [arg for arg in sys.argv[2:] if not arg.startswith("--")]

    source = clean_args[0] if len(clean_args) > 0 else DEFAULT_DOWNLOADS
    # If source is '.', we default target to '.' as well for in-place sorting
    if source == ".":
        target = clean_args[1] if len(clean_args) > 1 else "."
    else:
        target = clean_args[1] if len(clean_args) > 1 else DEFAULT_TARGET

    clear_terminal()
    organize_files(source, target, safe_mode=safe, dry_run=dry, report=report)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("No command given. Use 'help'.")
        sys.exit()

    user_choice = sys.argv[1].lower()

    if user_choice == "help":
        clear_terminal()
        command_help()
    elif user_choice == "todo":
        command_todo()
    elif user_choice == "organize":
        command_organize()
    elif user_choice == "dummy":
        command_dummy()
    elif user_choice == "log":
        command_log()
    elif user_choice == "find":
        command_find()
    elif user_choice == "status":
        command_status()
    else:
        print(f"Choose a right choice you fucking idiot {username}!")