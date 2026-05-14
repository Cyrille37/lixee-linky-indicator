import os

APP_NAME = "lixee-linky-indicator"
APP_VERSION = "0.1"
APP_FOLDER = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

CONFIG_FILENAME = f".{APP_NAME}"

REFRESH_SECONDS = 5
# Power thresholds for icon colors (in VA)
LOW_THRESHOLD = -100  # Below this: green icon
HIGH_THRESHOLD = 1  # Above this: red icon
