import os
import configparser

def get_session_logs_directory() -> str:
    config_path = os.path.expanduser("~/.termlogs")
    if not os.path.exists(config_path):
        raise FileNotFoundError(config_path)

    config = configparser.ConfigParser()
    config.read(config_path)

    try:
        return config["settings"]["session_logs_path"]
    except KeyError:
        raise KeyError("session_logs_path not found in [settings] section of " + config_path)
