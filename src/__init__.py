import os
import sys
import re
import json
import subprocess
import logging
import platform
from ttkbootstrap import *
import ttkbootstrap as ttk

# Constants
ROW_LIMIT = 4
PROCESS = subprocess.Popen
ALWAYS = False


def create_logger() -> logging.Logger:
    """
    Creates a logger for the application.
    The logger will log messages to a file named 'debug.log'.
    """

    logger = logging.getLogger("debug_logger")
    logger.setLevel(logging.DEBUG)
    handler = logging.FileHandler("debug.log")
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        "%(asctime)s - %(lineno)s - %(funcName)s - [%(levelname)s] - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


def launch_app(command_dict: dict, button: ttk.Button) -> None:
    """
    Launches the specified application in a new terminal window.
    """
    try:
        # Check if the command is a dictionary
        if not check_dict(command_dict):
            return

        # Get the script path and arguments
        script_path = command_dict.get("path", None)
        if not script_path:
            logger.error(f'Error: The script "path" is missing in the Config.')
            return
        if not check_path_format(script_path):
            return
        if command_dict.get("args"):
            args = command_dict.get("args")
            if isinstance(args, list):
                args = " ".join(args)
            else:
                args = str(args)
            cmd = f"{script_path} {args}"
        else:
            cmd = script_path

        # Check if the script is a Python script
        if not script_path.endswith(".py"):
            logger.error("Error: The script is not a Python script.")
            return

        # Check if the script exists
        if os.path.exists(script_path):
            logger.debug(f"Launching the application: {script_path}")
            logger.debug(f"Command: {cmd}")

            # Open the script in a new terminal window
            if sys.platform == "win32":
                os.system(f'start cmd /k "timeout /t 1 >nul & python {cmd}"')
            elif sys.platform in ["linux", "darwin"]:
                os.system(
                    f'gnome-terminal -- bash -c "sleep 1; python3 {cmd}; exec bash"'
                )  # Linux/macOS
            else:
                logger.error(f"Unsupported platform: {sys.platform}")
                return
        else:
            logger.error(f"Error: The script '{script_path}' does not exist.")
            return
    except Exception as e:
        logger.exception(f"Error launching the application: {e}")


def check_path_format(path_str: str) -> bool:
    """
    Checks the provided path to see if it's compatible for the current OS.
    Parameters:
        - path_str(str): The path to check.
    Returns:
        - bool: True if everything is correct, False if anything incompatible is found.
    """
    # Check for Windows OS
    if os.name == "nt":
        # Windows paths typically have a \ in them
        if "\\" not in path_str:
            logger.error(
                f"Path format is incorrect for Windows systems. Separator: '\\' is required. \n>> Path: {path_str}"
            )
            return False
        # Ensure the path does not contain illegal Windows characters
        illegal_chars = r'[<>"/|?*]'
        if re.search(illegal_chars, path_str):
            logger.error(
                f"Path contains invalid characters for Windows systems \n>> Path: {path_str}"
            )
            return False
        # Additional check: if the path starts with a drive letter, ensure the first character is a letter
        if path_str[1] == ":" and not path_str[0].isalpha():
            logger.error(f"Invalid drive letter format in path \n>> Path: {path_str}")
            return False

    # Check for POSIX OS (Linux/macOS)
    elif os.name == "posix":
        # POSIX paths should contain "/"
        if "/" not in path_str:
            logger.error(
                f"Path format is incorrect for POSIX systems (Mac OS/Linux). Separator '/' is required. \n>> Path: {path_str}"
            )
            return False
        # Ensure the path does not contain illegal characters
        if re.search(r"\0", path_str):  # null byte is illegal
            logger.error(
                f"Path contains invalid characters for POSIX systems (Mac OS/Linux) \n>> Path: {path_str}"
            )
            return False
        # Optional check: does the path begin with a '/' for absolute paths?
        if path_str.startswith("/") and not os.path.isabs(path_str):
            logger.error(
                f"Absolute path should start with '/' on POSIX systems (Mac OS/Linux) \n>> Path: {path_str}"
            )
            return False

    else:
        logger.error(f"Unsupported OS - {os.name}")
        return False

    return True


def check_dict(command_dict: dict) -> bool:
    """
    Checks if the command dictionary is formatted correctly.
    The command dictionary should contain the following keys:
        - "path": The path to the script to be executed.
        - "args": (Optional) A list of arguments to be passed to the script.
    Parameters:
        command_dict (dict): The command dictionary to be checked.
    Returns:
        bool: True if the command dictionary is formatted correctly, False otherwise.
    """
    if not isinstance(command_dict, dict):
        logger.error("Error: Command is not a dictionary.")
        return False
    if "path" not in command_dict:
        logger.error("Error: Command dictionary does not contain 'path' key.")
        return False
    if not isinstance(command_dict["path"], str):
        logger.error("Error: 'path' key in command dictionary is not a string.")
        return False
    if "args" in command_dict and not isinstance(command_dict["args"], (str, list)):
        logger.error("Error: 'args' key in command dictionary is not a string or list.")
        return False
    return True


def load_data_config(dir_str: str) -> dict:
    """
    Loads the configuration data from the config.json file.
    The config.json file should be located in the specified directory.
    Parameters:
        dir_str (str): The directory where the config.json file is located.
    Returns:
        dict: A dictionary containing the configuration data.
    """
    try:
        with open(os.path.join(dir_str, "config.json"), "r") as file:
            data = json.load(file)
            return data
    except FileNotFoundError:
        logger.error("Error: config.json file not found.")
        return {}
    except json.JSONDecodeError:
        logger.error("Error: Failed to decode JSON from config.json.")
        return {}


def write_config(dir_str: str, key: str, value) -> None:
    """
    Writes the configuration data to the config.json file.
    The config.json file should be located in the specified directory.
    Parameters:
        dir_str (str): The directory where the config.json file is located.
        key (str): The key to be updated in the config.json file's config dict.
        value: The value to be set for the specified key.
    """
    try:
        with open(os.path.join(dir_str, "config.json"), "r") as file:
            data = json.load(file)
            data["config"][key] = value
        with open(os.path.join(dir_str, "config.json"), "w") as file:
            json.dump(data, file, indent=4)
    except FileNotFoundError:
        logger.error("Error: config.json file not found.")
    except json.JSONDecodeError:
        logger.error("Error: Failed to decode JSON from config.json.")
    except Exception as e:
        logger.exception(f"Error writing to config.json: {e}")


def create_button(
    row_index: int,
    column_index: int,
    root: ttk,
    title: str,
    command_dict: dict,
    width: int,
) -> None:
    """
    Creates a button in the specified row and column of the given root.
    """
    command_dict["title"] = title  # Store the title in the command_dict for resetting
    button = ttk.Button(
        root,
        text=title,
        command=lambda: launch_app(command_dict, button),
        width=width,
    )
    button.grid(row=row_index, column=column_index, padx=20, pady=10)


def get_path() -> str:
    """
    Get the working path of the script for use later.
    Returns:
        - str: The file path string for where the script is running.
    """

    # Determine the correct path to the icon depending on if the app is bundled or not
    if getattr(sys, "frozen", False):
        app_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    else:
        app_path = os.path.dirname(__file__)

    return app_path


def is_dark_mode() -> bool:
    """
    This function checks the system's theme settings to determine if dark mode is enabled.
    Returns:
        bool: True if dark mode is enabled, False otherwise.
    """
    system = platform.system()

    # If the system is Windows, check the registry for dark mode settings
    if system == "Windows":
        # Import the winreg module to access the Windows registry
        import winreg

        # Check if the registry key exists for dark mode
        try:
            # Open the registry key for the current user
            registry_key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize",
            )
            value, _ = winreg.QueryValueEx(registry_key, "AppsUseLightTheme")
            winreg.CloseKey(registry_key)
            return True if value == 0 else False
        except FileNotFoundError:
            return False
    # If the system is macOS, check the defaults for dark mode settings
    elif system == "Darwin":

        try:
            # Check if the defaults command is available
            result = subprocess.run(
                ["defaults", "read", "-g", "AppleInterfaceStyle"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            return True if "Dark" in result.stdout else False
        except Exception:
            return False

    # If the system is Linux, check for GNOME or KDE desktop environments
    elif system == "Linux":
        # Check for GNOME or KDE desktop environments
        try:
            # Check if the gsettings command is available
            result = subprocess.run(
                ["gsettings", "get", "org.gnome.desktop.interface", "gtk-theme"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            return True if "dark" in result.stdout.lower() else False
        except Exception:
            return False

    else:
        return False


def create_window(scripts_dict: dict) -> None:
    """
    Creates the main window and populates it with buttons based on the provided scripts_dict.
    Parameters:
        scripts_dict (dict): A dictionary containing the configuration data for the buttons.
    """

    global ROW_LIMIT, ALWAYS, PROCESS

    if is_dark_mode():
        theme_name = "darkly"
    else:
        theme_name = "flatly"

    # Create the main window
    root = ttk.Window(themename=theme_name)
    root.title("Launcher")

    app_path = get_path()

    # Set the icon for the window
    if os.name == "nt":
        root.iconbitmap(os.path.join(app_path, "assets", "icon.ico"))
    elif os.name == "posix":
        root.iconphoto(
            True,
            ttk.PhotoImage(file=os.path.join(app_path, "src", "assets", "icon.png")),
        )

    # Set the button size and padding params to use to calculate the window size
    button_width = max(len(key) for key in scripts_dict.keys()) * 10

    root.resizable(False, False)
    root.attributes("-topmost", ALWAYS)

    notebook_frame = ttk.Notebook(root)
    notebook_frame.grid(row=0, column=0, padx=20, pady=10, sticky="nsew")

    # Create the frames for the tabs
    master_frame = ttk.Frame(notebook_frame)
    settings_frame = ttk.Frame(notebook_frame)

    # Add the frames as tabs to the notebook
    notebook_frame.add(master_frame, text="Scripts")
    notebook_frame.add(settings_frame, text="Settings")

    # Create a label for the title
    title_label = ttk.Label(master_frame, text="Script Launcher", font=("Arial", 18))
    title_label.grid(row=0, column=0, padx=10, pady=10, sticky="n")

    # Create a frame for the buttons
    button_frame = ttk.Frame(master_frame)
    button_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

    def update_layout():
        """
        Updates the layout of buttons based on the current ROW_LIMIT.
        """
        for widget in button_frame.winfo_children():
            widget.destroy()  # Clear existing buttons

        # Create buttons based on the scripts_dict
        row_index = 0
        column_index = 0
        for button_title, command_dict in scripts_dict.items():
            create_button(
                row_index,
                column_index,
                button_frame,
                button_title,
                command_dict,
                int(button_width / 10),
            )
            row_index += 1
            column_index += 1 if row_index >= ROW_LIMIT else 0
            if row_index == ROW_LIMIT:
                row_index = 0

    # Define the function to toggle the "Always on Top" attribute
    def toggle_always_on_top():
        global ALWAYS
        root.attributes("-topmost", always_on_top_var.get())
        if always_on_top_var.get() == 1:
            if not ALWAYS:
                ALWAYS = True
                write_config(script_dir, "ALWAYS", ALWAYS)
        else:
            if ALWAYS:
                ALWAYS = False
                write_config(script_dir, "ALWAYS", ALWAYS)

    # Define the settings section
    # Add a frame for the settings tab
    section_frame = ttk.Frame(settings_frame)
    section_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

    # Configure the settings_frame to expand and fill the window
    settings_frame.grid_rowconfigure(0, weight=1)
    settings_frame.grid_columnconfigure(0, weight=1)

    # Configure the section_frame to expand and fill the window and set weights
    section_frame.grid_rowconfigure(0, weight=0)
    section_frame.grid_rowconfigure(1, weight=0)
    section_frame.grid_rowconfigure(2, weight=0)
    section_frame.grid_rowconfigure(3, weight=0)
    section_frame.grid_rowconfigure(4, weight=0)
    section_frame.grid_columnconfigure(0, weight=1)
    section_frame.grid_columnconfigure(1, weight=1)
    section_frame.grid_columnconfigure(2, weight=1)

    # Create a label for the settings tab
    settings_label = ttk.Label(section_frame, text="Settings", font=("Arial", 18))
    settings_label.grid(row=0, column=0, padx=10, pady=10, sticky="n", columnspan=3)

    # Create a checkbox for "Always on Top"
    always_on_top_var = ttk.IntVar(value=1 if ALWAYS else 0)
    always_on_top_checkbox = ttk.Checkbutton(
        section_frame,
        text="Always on Top",
        variable=always_on_top_var,
        command=toggle_always_on_top,
    )
    always_on_top_checkbox.grid(row=1, column=0, padx=10, pady=10, sticky="w")

    # Add a section to change the number of rows
    row_limit_frame = ttk.Frame(section_frame)
    row_limit_frame.grid(row=2, column=0, padx=10, pady=10, sticky="w")

    row_limit_label = ttk.Label(row_limit_frame, text="Number of Rows:")
    row_limit_label.grid(row=0, column=0, sticky="w")

    row_limit_var = ttk.IntVar(value=ROW_LIMIT)

    def update_row_limit():
        """
        Updates the ROW_LIMIT value, saves it to the config, and refreshes the layout.
        """
        global ROW_LIMIT
        new_row_limit = row_limit_var.get()
        if new_row_limit > 0:  # Ensure the value is valid
            ROW_LIMIT = new_row_limit
            write_config(script_dir, "ROW_LIMIT", ROW_LIMIT)
            update_layout()

    row_limit_spinbox = ttk.Spinbox(
        row_limit_frame,
        from_=3,
        to=10,
        textvariable=row_limit_var,
        command=update_row_limit,
        width=5,
        state="readonly",
    )
    row_limit_spinbox.grid(row=0, column=1, padx=5, sticky="w")

    # Add bottom padding to the window
    bottom_padding = ttk.Frame(root)
    bottom_padding.grid(row=1, column=0, pady=10, sticky="s")

    # Trigger the initial layout update
    update_layout()

    root.mainloop()


if __name__ == "__main__":
    # Create the logger
    logger = create_logger()

    # Set the current working directory to the script's directory
    script_path = sys.argv[0]
    if os.path.dirname(script_path):
        script_dir = os.path.dirname(script_path)
    else:
        script_dir = os.getcwd()

    # Load the configuration data
    data = load_data_config(script_dir)

    # Check if data is loaded successfully
    if not data:
        logger.error("No data loaded. Exiting.")
        sys.exit(1)

    # Get the row limit from the config file
    ROW_LIMIT = data.get("config", {}).get("ROW_LIMIT", ROW_LIMIT)

    # Get the "Always on Top" setting from the config file
    ALWAYS = data.get("config", {}).get("ALWAYS", False)

    # Get the scripts dictionary from the loaded data
    scripts_dict = data.get("scripts", {})

    # Create and launch the main window
    create_window(scripts_dict)
