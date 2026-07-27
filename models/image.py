import os
import shutil
from datetime import datetime

from database import get_connection
from paths import patient_images_dir


def add_image(patient_id: int, source_path: str) -> str:
    if not os.path.isfile(source_path):
        raise FileNotFoundError(f"Image not found: {source_path}")

    folder = patient_images_dir(patient_id)
    os.makedirs(folder, exist_ok=True)

    base_name = os.path.basename(source_path)
    name, ext = os.path.splitext(base_name)
    destination = os.path.join(folder, base_name)
    counter = 1

    while os.path.exists(destination):
        destination = os.path.join(folder, f"{name}_{counter}{ext}")
        counter += 1

    shutil.copy2(source_path, destination)

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO images (patient_id, path, date)
        VALUES (?, ?, ?)
        """,
        (patient_id, destination, datetime.now().strftime("%Y-%m-%d")),
    )
    conn.commit()
    conn.close()
    return destination


def get_images(patient_id: int) -> list[tuple]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, path, date
        FROM images
        WHERE patient_id = ?
        ORDER BY id DESC
        """,
        (patient_id,),
    )
    images = cursor.fetchall()
    conn.close()
    return images


def delete_image(image_id: int) -> None:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT path FROM images WHERE id = ?", (image_id,))
    result = cursor.fetchone()

    if result and os.path.isfile(result[0]):
        os.remove(result[0])

    cursor.execute("DELETE FROM images WHERE id = ?", (image_id,))
    conn.commit()
    conn.close()


def delete_patient_images(patient_id: int) -> None:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT path FROM images WHERE patient_id = ?", (patient_id,))
    paths = [row[0] for row in cursor.fetchall()]
    cursor.execute("DELETE FROM images WHERE patient_id = ?", (patient_id,))
    conn.commit()
    conn.close()

    for path in paths:
        if os.path.isfile(path):
            os.remove(path)

    folder = patient_images_dir(patient_id)
    if os.path.isdir(folder):
        shutil.rmtree(folder, ignore_errors=True)
