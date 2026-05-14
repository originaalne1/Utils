import os
import sys
import winreg


def install():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    main_py = os.path.join(script_dir, "main.py")
    bin_dir = os.path.join(script_dir, "bin")

    # Ensure the bin directory exists
    if not os.path.exists(bin_dir):
        os.makedirs(bin_dir)

    bat_path = os.path.join(bin_dir, "utils.bat")

    # We overwrite this every time to ensure that if you moved the project,
    # the global command points to the new location.
    print(f"Updating global command wrapper at: {bat_path}")
    with open(bat_path, "w") as f:
        f.write(f'@echo off\npython "{main_py}" %*')

    print("Refreshing System PATH for current user...")
    try:
        # Open the User Environment key
        reg_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Environment', 0, winreg.KEY_ALL_ACCESS)

        try:
            path_value, _ = winreg.QueryValueEx(reg_key, 'Path')
        except FileNotFoundError:
            path_value = ""

        # Check if our bin_dir is already there. If not, add it.
        # We normalize paths to prevent "C:/path" vs "C:\path" duplicates.
        norm_bin = os.path.normpath(bin_dir)
        current_paths = [os.path.normpath(p) for p in path_value.split(';') if p.strip()]

        if norm_bin not in current_paths:
            new_path = f"{path_value};{norm_bin}".replace(";;", ";")
            winreg.SetValueEx(reg_key, 'Path', 0, winreg.REG_EXPAND_SZ, new_path)
            print("\nSUCCESS: 'utils' has been added to your PATH!")
        else:
            print("\nUPDATE: 'utils' is already in your PATH. Wrapper has been refreshed.")

        print("\n" + "=" * 50)
        print("INSTALLATION COMPLETE")
        print("=" * 50)
        print("1. Restart any open Terminal or VS Code windows.")
        print("2. Type 'utils help' to verify.")
        print("=" * 50)

    except Exception as e:
        print(f"Error updating PATH: {e}")
        print("Try running the terminal as Administrator if this fails.")


if __name__ == "__main__":
    install()