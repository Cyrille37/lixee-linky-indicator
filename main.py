#!/usr/bin/env python3
import os
import gi
import sys

gi.require_version("Gtk", "3.0")
#gi.require_version("PangoCairo", "1.0")
from gi.repository import Gtk, Gio

# Add lib directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'lib'))

from lib.constants import (
    APP_NAME, APP_VERSION, APP_FOLDER, CONFIG_FILENAME,
)

from lib.LixeeLinkyIndicator import LixeeLinkyIndicator

if __name__ == "__main__":
    print(f"{APP_NAME} {APP_VERSION} starting!")

    configfile = os.path.join(os.getenv("HOME"), CONFIG_FILENAME)
    if os.path.exists(configfile) is False:
        configfile = os.path.join(APP_FOLDER, CONFIG_FILENAME)

    indicator = LixeeLinkyIndicator(configfile)

    if os.path.exists(configfile):
        print(f"Monitoring configuration file: {configfile}")
        # Monitor config file changes
        file = Gio.File.new_for_path(configfile)
        monitor = file.monitor_file(Gio.FileMonitorFlags.NONE, None)
        monitor.connect("changed", indicator.on_config_changed)

    Gtk.main()
