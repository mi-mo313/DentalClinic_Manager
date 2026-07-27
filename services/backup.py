import os
import shutil
from datetime import datetime

from paths import BACKUPS_DIR, DB_PATH, IMAGES_DIR, ensure_app_dirs


def create_backup() -> str:
    ensure_app_dirs()

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    backup_folder = os.path.join(BACKUPS_DIR, f"backup_{timestamp}")
    os.makedirs(backup_folder, exist_ok=True)

    if os.path.exists(DB_PATH):
        shutil.copy2(DB_PATH, backup_folder)
    else:
        raise FileNotFoundError("Database file not found.")

    if os.path.exists(IMAGES_DIR):
        shutil.copytree(
            IMAGES_DIR,
            os.path.join(backup_folder, "images"),
            dirs_exist_ok=True,
        )

    return backup_folder
