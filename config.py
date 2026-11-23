"""Central configuration for the Buoy Detection System."""
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent

# Place your trained Roboflow/Ultralytics weights here.
MODEL_PATH = PROJECT_DIR / "weights" / "best.pt"
CAPTURES_DIR = PROJECT_DIR / "captures"

# Camera indices to scan when Refresh Camera is clicked.
CAMERA_SCAN_RANGE = range(0, 6)

# Detection defaults.
DEFAULT_CONFIDENCE = 0.45
DEFAULT_IMAGE_SIZE = 640
AVAILABLE_IMAGE_SIZES = (320, 416, 512, 640, 800, 960)

# Optional explicit mapping from the EXACT class names in your model to a
# canonical target. Use lowercase keys; accepted values are "red" or "green".
# Example if model.names is {0: "buoy_merah", 1: "buoy_hijau"}:
# CLASS_NAME_MAP = {"buoy_merah": "red", "buoy_hijau": "green"}
CLASS_NAME_MAP = {"red_buoy": "red", "green_buoy": "green"}

# Automatic aliases are checked after CLASS_NAME_MAP. Extend these tuples if
# your Roboflow class names use another naming convention.
RED_CLASS_ALIASES = (
    "red buoy", "buoy red", "red", "buoy merah", "merah", "red_buoy",
    "buoy_red", "redbuoy",
)
GREEN_CLASS_ALIASES = (
    "green buoy", "buoy green", "green", "buoy hijau", "hijau", "green_buoy",
    "buoy_green", "greenbuoy",
)

# OpenCV camera backend preference on Windows.
CAMERA_BACKENDS = ("DSHOW", "MSMF", "ANY")

# Keep the video preview responsive on high-resolution displays.
MAX_PREVIEW_WIDTH = 1200
MAX_PREVIEW_HEIGHT = 900
