"""Application paths — works for normal runs and PyInstaller bundles."""

import os
import sys


def get_app_dir() -> str:
    """Directory where the app stores data (next to the exe when frozen)."""
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


APP_DIR = get_app_dir()
DATA_DIR = os.path.join(APP_DIR, "data")
IMAGES_DIR = os.path.join(APP_DIR, "images")
INVOICES_DIR = os.path.join(APP_DIR, "invoices")
BACKUPS_DIR = os.path.join(APP_DIR, "backups")
DB_PATH = os.path.join(DATA_DIR, "clinic.db")


def ensure_app_dirs() -> None:
    """Create all runtime folders if they do not exist."""
    for folder in (DATA_DIR, IMAGES_DIR, INVOICES_DIR, BACKUPS_DIR):
        os.makedirs(folder, exist_ok=True)


def patient_images_dir(patient_id: int) -> str:
    return os.path.join(IMAGES_DIR, f"patient_{patient_id}")
