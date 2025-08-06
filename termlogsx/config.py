"""
config.py - Configuration management for the Termlogs project

Project: termlogs
URL: github.com/orme292/termlogs
Author: Andrew Orme (github.com/orme292)
License: MIT

This module provides functions to determine the directory path for iTerm2
session logs. It supports an optional override path and falls back to reading
a configuration file located at ~/.termlogs. The configuration file must have
a [settings] section with a 'session_logs_path' key. If the target directory
does not exist, this module attempts to create it.

Constants:
    DEFAULT_PATH (str): Path to the configuration file.
    DEFAULT_LOG_PATH (str): Default log directory path.

Functions:
    get_session_logs_path(override: str = None) -> Path:
        Resolves and returns the session logs path, either from the override,
        the config file, or the default path. Ensures the path exists.
"""
import configparser
import os
from pathlib import Path

# The default path for the config file can't be changed.
DEFAULT_PATH = "~/.termlogs"
DEFAULT_LOG_PATH = "~/session_logs"


def get_session_logs_path(override: str = None) -> Path:
    path: Path

    if override is None or override == "":
        # if the override is empty or none, then read from the config file
        # the config file is always at the default location specified in
        # DEFAULT_PATH
        config = configparser.ConfigParser()
        config.read(os.path.expanduser(DEFAULT_PATH))
        try:
            path = Path(config["settings"]["session_logs_path"])
        except KeyError:
            raise Exception(f"session_logs_path not found in [settings] section of {DEFAULT_PATH}")
    else:
        # if an override is given, then we use that
        path = Path(os.path.expanduser(override))

    # check whether the path is a valid directory, otherwise fail
    if not path.is_dir():
        raise Exception(f"{path} is not a valid directory.")

    # if the path doesn't exist, create it or fail
    if not path.exists():
        try:
            path.mkdir(parents=True)
        except FileNotFoundError as e:
            raise Exception(f"Could not create directory: {path} {e}")
        except OSError as e:
            raise Exception(f"Could not create directory: {path} {e}")

    # return the path
    return path
