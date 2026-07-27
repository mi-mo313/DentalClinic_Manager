from datetime import datetime

from database import get_connection


def add_patient(name: str, phone: str, notes: str, total: float) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO patients (name, phone, notes, total, created_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (name, phone, notes, total, datetime.now().strftime("%Y-%m-%d")),
    )
    patient_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return patient_id


def get_patients(keyword: str = "") -> list[tuple]:
    conn = get_connection()
    cursor = conn.cursor()

    if keyword:
        like = f"%{keyword.strip()}%"
        cursor.execute(
            """
            SELECT id, name, phone, notes, total
            FROM patients
            WHERE name LIKE ? OR phone LIKE ?
            ORDER BY id DESC
            """,
            (like, like),
        )
    else:
        cursor.execute(
            """
            SELECT id, name, phone, notes, total
            FROM patients
            ORDER BY id DESC
            """
        )

    data = cursor.fetchall()
    conn.close()
    return data


def get_patient(patient_id: int) -> tuple | None:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM patients WHERE id = ?", (patient_id,))
    patient = cursor.fetchone()
    conn.close()
    return patient


def update_patient(
    patient_id: int,
    name: str,
    phone: str,
    notes: str,
    total: float,
) -> None:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE patients
        SET name = ?, phone = ?, notes = ?, total = ?
        WHERE id = ?
        """,
        (name, phone, notes, total, patient_id),
    )
    conn.commit()
    conn.close()


def delete_patient(patient_id: int) -> None:
    from models.image import delete_patient_images

    delete_patient_images(patient_id)

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM payments WHERE patient_id = ?", (patient_id,))
    cursor.execute("DELETE FROM visits WHERE patient_id = ?", (patient_id,))
    cursor.execute("DELETE FROM patients WHERE id = ?", (patient_id,))
    conn.commit()
    conn.close()


def add_payment(patient_id: int, amount: float) -> None:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO payments (patient_id, amount, date)
        VALUES (?, ?, ?)
        """,
        (patient_id, amount, datetime.now().strftime("%Y-%m-%d")),
    )
    conn.commit()
    conn.close()


def get_payments(patient_id: int) -> list[tuple]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT amount, date
        FROM payments
        WHERE patient_id = ?
        ORDER BY id DESC
        """,
        (patient_id,),
    )
    data = cursor.fetchall()
    conn.close()
    return data


def get_balance(patient_id: int) -> dict | None:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT total FROM patients WHERE id = ?", (patient_id,))
    row = cursor.fetchone()
    if row is None:
        conn.close()
        return None

    total = row[0] or 0

    cursor.execute(
        """
        SELECT COALESCE(SUM(amount), 0)
        FROM payments
        WHERE patient_id = ?
        """,
        (patient_id,),
    )
    paid = cursor.fetchone()[0] or 0
    conn.close()

    return {
        "total": total,
        "paid": paid,
        "remaining": total - paid,
    }
