#!/usr/bin/env python3
import requests
import os
import gi
import re
gi.require_version("Gtk", "3.0")
gi.require_version("PangoCairo", "1.0")
try:
    gi.require_version("AppIndicator3", "0.1")
    from gi.repository import AppIndicator3 as appindicator
except ImportError:
    from gi.repository import AppIndicator as appindicator
from gi.repository import Gtk, GLib, Gio

# Import from constants module instead of main
from lib.constants import (
    APP_NAME, APP_VERSION, APP_FOLDER, CONFIG_FILENAME,
    REFRESH_SECONDS, LOW_THRESHOLD, HIGH_THRESHOLD
)

ASSETS_PATH = os.path.join(APP_FOLDER, "assets")
ICON_PATH = os.path.join(ASSETS_PATH, "solar-panel.svg")
ICON_PATH_GREEN = os.path.join(ASSETS_PATH, "solar-panel-green.svg")
ICON_PATH_YELLOW = os.path.join(ASSETS_PATH, "solar-panel-yellow.svg")
ICON_PATH_RED = os.path.join(ASSETS_PATH, "solar-panel-red.svg")
TEXT_PATTERN = "8888 VA"

ip = "192.168.1.183"

class LixeeLinkyIndicator:
    def __init__(self, configfile):
        self.timeout_source = None  # Store timeout source ID
        self.refresh_seconds = REFRESH_SECONDS
        self.low_threshold = LOW_THRESHOLD
        self.high_threshold = HIGH_THRESHOLD

        self.read_config(configfile)

        self.indicator = appindicator.Indicator.new(
            APP_NAME, "", appindicator.IndicatorCategory.APPLICATION_STATUS
        )
        self.indicator.set_status(appindicator.IndicatorStatus.ACTIVE)

        # Set the solar icon
        self.indicator.set_icon_full(ICON_PATH, APP_NAME)
        # No initial label - will be set on first update
        self.indicator.set_label("... VA", TEXT_PATTERN)

        self.menu = Gtk.Menu()
        item_quit = Gtk.MenuItem(label="Quitter")
        item_quit.connect("activate", self.quit)
        self.menu.append(item_quit)

        self.menu.show_all()
        self.indicator.set_menu(self.menu)

        # Start the initial timeout
        self.restart_timeout()

    def update_indicator(self):
        try:
            response = requests.get(f"http://{ip}/getLinky")
            data = response.json()
            power_value = data["2820_1295"]
            text = f"{power_value} VA"

            # Set label
            self.indicator.set_label(text, TEXT_PATTERN)

            # Change icon color based on power value
            if power_value < self.low_threshold:
                self.indicator.set_icon_full(ICON_PATH_GREEN, APP_NAME)
            elif power_value > self.high_threshold:
                self.indicator.set_icon_full(ICON_PATH_RED, APP_NAME)
            else:
                self.indicator.set_icon_full(ICON_PATH_YELLOW, APP_NAME)

        except Exception as e:
            print(f"Erreur: {e}")
            self.indicator.set_label("ERR", TEXT_PATTERN)
            self.indicator.set_icon_full(
                ICON_PATH, APP_NAME
            )  # Reset to default on error
        return True

    def on_config_changed(self, filemonitor, file, other_file, event_type):
        if event_type != Gio.FileMonitorEvent.CHANGES_DONE_HINT:
            return
        print("Config changed !")
        self.read_config(file.get_path())

    def read_config(self, config_file):
        print("Reading config...")
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = f.readlines()
        except IOError as e:
            print(f"Error reading config file: {e}")
            config = []
        
        line_pattern = re.compile(r"^([A-Za-z_]+)=(.*)$")
        config_changed = False
        
        for line in config:
            line = line.strip()
            if line == "" or line.startswith('#'):
                continue
            result = line_pattern.search(line)
            if not result or result.group(2) is None:
                print("ERROR:", f"Configuration unknown line format for: {line}")
                continue
            
            key = result.group(1).upper()
            value_str = result.group(2).strip()
            print(f"{result.group(1)} = {value_str}")

            try:
                if key == "REFRESH_SECONDS":
                    new_value = int(value_str)
                    if 1 <= new_value <= 1800:  # Validate reasonable range
                        self.refresh_seconds = new_value
                        config_changed = True
                    else:
                        print(f"Warning: REFRESH_SECONDS value {new_value} out of range (1-1800)")
                elif key == "LOW_THRESHOLD":
                    self.low_threshold = int(value_str)
                    config_changed = True
                elif key == "HIGH_THRESHOLD":
                    self.high_threshold = int(value_str)
                    config_changed = True
            except ValueError:
                print(f"Error: Invalid integer value for {key}: {value_str}")
        
        # Restart timeout if refresh interval changed
        if config_changed:
            GLib.idle_add(self.restart_timeout)

    def restart_timeout(self):
        """Restart the GLib timeout with the current refresh_seconds value"""
        if self.timeout_source is not None:
            GLib.source_remove(self.timeout_source)
        
        # Ensure reasonable minimum interval
        effective_interval = max(1, self.refresh_seconds)
        
        self.timeout_source = GLib.timeout_add_seconds(
            effective_interval,
            self.update_indicator
        )
        print(f"Timeout restarted with {effective_interval} second interval")
        return False  # Return False to remove the idle source
    
    def quit(self, widget):
        Gtk.main_quit()


if __name__ == "__main__":
    print("Lixee-linky-indicator starting!")

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
