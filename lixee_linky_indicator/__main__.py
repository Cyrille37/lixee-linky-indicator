#!/usr/bin/env python3
import os
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gio

from lixee_linky_indicator.constants import APP_NAME, APP_VERSION, CONFIG_FILENAME
from lixee_linky_indicator.LixeeLinkyIndicator import LixeeLinkyIndicator


def main():
    print(f"{APP_NAME} {APP_VERSION} starting!")

    configfile = os.path.join(os.getenv("HOME"), CONFIG_FILENAME)
    indicator = LixeeLinkyIndicator(configfile)

    if os.path.exists(configfile):
        print(f"Monitoring configuration file: {configfile}")
        file = Gio.File.new_for_path(configfile)
        monitor = file.monitor_file(Gio.FileMonitorFlags.NONE, None)
        monitor.connect("changed", indicator.on_config_changed)

    Gtk.main()


if __name__ == "__main__":
    main()
