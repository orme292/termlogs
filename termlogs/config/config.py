import os
import configparser
from pathlib import Path

DEFAULT_LOG_DIR = "~/.termlogs"

def get_session_logs_directory(override: str="") -> str:
    # If an override is provided, use that instead of the config file
    if override != "":
        override = os.path.expanduser(override)
        log_path = Path(os.path.expanduser(override))
        if not log_path.is_dir():
            raise Exception(f"Error: {log_path} is not a valid directory.")
        print(f"Using session log directory: {override}")
        return override

    # If an override is NOT provided, then get the value from the config file.
    config_path = os.path.expanduser(DEFAULT_LOG_DIR)
    if not os.path.exists(config_path):
        raise FileNotFoundError(config_path)

    config = configparser.ConfigParser()
    config.read(config_path)

    log_path: Path
    try:
        log_path = Path(config["settings"]["session_logs_path"])
        if not log_path.is_dir():
            raise FileNotFoundError(f"Error: {log_path} is not a valid directory.")
        return config["settings"]["session_logs_path"]

    except KeyError:
        raise KeyError(f"session_logs_path not found in [settings] section of {config_path}")
    except FileNotFoundError:
        raise FileNotFoundError(f"Log dir is not a directory: {log_path}")
