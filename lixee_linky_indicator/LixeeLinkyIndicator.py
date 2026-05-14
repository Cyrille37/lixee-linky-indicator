#!/usr/bin/env python3
import os
import re
import requests
import gi

gi.require_version("Gtk", "3.0")
gi.require_version("PangoCairo", "1.0")
try:
    gi.require_version("AppIndicator3", "0.1")
    from gi.repository import AppIndicator3 as appindicator
except ImportError:
    from gi.repository import AppIndicator as appindicator
from gi.repository import Gtk, GLib, Gio

from lixee_linky_indicator.constants import (
    APP_NAME, APP_VERSION, REFRESH_SECONDS, LOW_THRESHOLD, HIGH_THRESHOLD
)


def _get_assets_path():
    try:
        from importlib.resources import files
        return str(files("lixee_linky_indicator") / "assets")
    except Exception:
        return os.path.join(os.path.dirname(os.path.realpath(__file__)), "assets")


ASSETS_PATH = _get_assets_path()
ICON_PATH_DEFAULT = os.path.join(ASSETS_PATH, "solar-panel.svg")
ICON_PATH_LOW = os.path.join(ASSETS_PATH, "solar-panel-low.svg")
ICON_PATH_MIDDLE = os.path.join(ASSETS_PATH, "solar-panel-middle.svg")
ICON_PATH_HIGH = os.path.join(ASSETS_PATH, "solar-panel-high.svg")
TEXT_PATTERN = "8888 VA"


class LixeeLinkyIndicator:
    def __init__(self, configfile):
        self.timeout_source = None
        self.refresh_seconds = REFRESH_SECONDS
        self.low_threshold = LOW_THRESHOLD
        self.high_threshold = HIGH_THRESHOLD
        self.lixeebox_ip = None

        self.read_config(configfile)

        if self.lixeebox_ip is None:
            self.popupWarning(
                "Configuration incomplète",
                "Le fichier de configuration ne contient pas 'LIXEEBOX_IP'.\n"
                "Veuillez ajouter cette valeur et redémarrer l'application."
            )
            Gtk.main_quit()
            return

        self.indicator = appindicator.Indicator.new(
            APP_NAME, "", appindicator.IndicatorCategory.APPLICATION_STATUS
        )
        self.indicator.set_status(appindicator.IndicatorStatus.ACTIVE)
        self.indicator.set_icon_full(ICON_PATH_DEFAULT, APP_NAME)
        self.indicator.set_label("... VA", TEXT_PATTERN)

        self.menu = Gtk.Menu()
        item_quit = Gtk.MenuItem(label="Quitter")
        item_quit.connect("activate", self.quit)
        self.menu.append(item_quit)
        self.menu.show_all()
        self.indicator.set_menu(self.menu)

        self.restart_timeout()

    def update_indicator(self):
        try:
            response = requests.get(f"http://{self.lixeebox_ip}/getLinky")
            data = response.json()
            power_value = data["2820_1295"]
            text = f"{power_value} VA"

            self.indicator.set_label(text, TEXT_PATTERN)

            if power_value < self.low_threshold:
                self.indicator.set_icon_full(ICON_PATH_LOW, APP_NAME)
            elif power_value > self.high_threshold:
                self.indicator.set_icon_full(ICON_PATH_HIGH, APP_NAME)
            else:
                self.indicator.set_icon_full(ICON_PATH_MIDDLE, APP_NAME)

        except Exception as e:
            self.indicator.set_label("ERR", TEXT_PATTERN)
            self.indicator.set_icon_full(ICON_PATH_DEFAULT, APP_NAME)
        return True

    def on_config_changed(self, filemonitor, file, other_file, event_type):
        if event_type != Gio.FileMonitorEvent.CHANGES_DONE_HINT:
            return
        #print("Config changed!")
        self.read_config(file.get_path())

    def read_config(self, config_file):
        #print("Reading config...")
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = f.readlines()
        except IOError as e:
            #print(f"Error reading config file: {e}")
            config = []

        line_pattern = re.compile(r"^([A-Za-z_]+)=(.*)$")
        config_changed = False

        for line in config:
            line = line.strip()
            if line == "" or line.startswith('#'):
                continue
            result = line_pattern.search(line)
            if not result or result.group(2) is None:
                #print("ERROR:", f"Configuration unknown line format for: {line}")
                continue

            key = result.group(1).upper()
            value_str = result.group(2).strip()
            #print(f"{result.group(1)} = {value_str}")

            try:
                if key == "REFRESH_SECONDS":
                    new_value = int(value_str)
                    if 1 <= new_value <= 1800:
                        self.refresh_seconds = new_value
                        config_changed = True
                    else:
                        print(f"Warning: REFRESH_SECONDS value {new_value} out of range (1-1800)")
                elif key == "LOW_THRESHOLD":
                    self.low_threshold = int(value_str)
                elif key == "HIGH_THRESHOLD":
                    self.high_threshold = int(value_str)
                elif key == "LIXEEBOX_IP":
                    self.lixeebox_ip = value_str

            except ValueError:
                print(f"Error: Invalid integer value for {key}: {value_str}")

        if config_changed:
            GLib.idle_add(self.restart_timeout)

    def restart_timeout(self):
        if self.timeout_source is not None:
            GLib.source_remove(self.timeout_source)
        effective_interval = max(1, self.refresh_seconds)
        self.timeout_source = GLib.timeout_add_seconds(
            effective_interval, self.update_indicator
        )
        #print(f"Timeout restarted with {effective_interval} second interval")
        return False

    def quit(self, widget):
        Gtk.main_quit()

    def popupWarning(self, title, message):
        dialog = Gtk.MessageDialog(
            None, Gtk.DialogFlags.MODAL, Gtk.MessageType.WARNING,
            Gtk.ButtonsType.CLOSE, title
        )
        dialog.format_secondary_text(message)
        dialog.run()
        dialog.destroy()
