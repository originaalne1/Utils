import os
import winreg


def normalize_path(path):
    return os.path.normcase(os.path.normpath(path))


def write_wrapper(main_py, bat_path):
    print(f"Updating global command wrapper at: {bat_path}")
    with open(bat_path, "w") as f:
        f.write(f'@echo off\npython "{main_py}" %*')


def refresh_user_path(bin_dir):
    print("Refreshing System PATH for current user...")
    try:
        reg_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Environment', 0, winreg.KEY_ALL_ACCESS)

        try:
            path_value, _ = winreg.QueryValueEx(reg_key, 'Path')
        except FileNotFoundError:
            path_value = ""

        current_paths = [p.strip() for p in path_value.split(';') if p.strip()]
        norm_bin = normalize_path(bin_dir)
        new_paths = []
        removed_old = False

        for path in current_paths:
            norm_path = normalize_path(path)
            if norm_path == norm_bin:
                if path not in new_paths:
                    new_paths.append(path)
                continue

            if os.path.basename(norm_path) == 'bin' and os.path.basename(os.path.dirname(norm_path)).lower() == 'organizer':
                removed_old = True
                continue

            if path not in new_paths:
                new_paths.append(path)

        if norm_bin not in [normalize_path(p) for p in new_paths]:
            new_paths.append(bin_dir)

        new_path_value = ";".join(new_paths)
        winreg.SetValueEx(reg_key, 'Path', 0, winreg.REG_EXPAND_SZ, new_path_value)

        if removed_old:
            print("\nRemoved stale Organizer PATH entries and refreshed the current install.")
        else:
            print("\nPATH refreshed for the current install.")

        print("\n" + "=" * 50)
        print("INSTALLATION COMPLETE")
        print("=" * 50)
        print("1. Restart any open Terminal or VS Code windows.")
        print("2. Type 'utils help' to verify.")
        print("=" * 50)

    except Exception as e:
        print(f"Error updating PATH: {e}")
        print("Try running the terminal as Administrator if this fails.")


def install():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    main_py = os.path.join(script_dir, "main.py")
    bin_dir = os.path.join(script_dir, "bin")

    if not os.path.exists(bin_dir):
        os.makedirs(bin_dir)

    bat_path = os.path.join(bin_dir, "utils.bat")
    write_wrapper(main_py, bat_path)
    refresh_user_path(bin_dir)


if __name__ == "__main__":
    install()