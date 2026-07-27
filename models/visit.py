from datetime import datetime

from database import get_connection


def add_visit(patient_id: int, description: str, tooth_number: str) -> None:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO visits (patient_id, description, tooth_number, date)
        VALUES (?, ?, ?, ?)
        """,
        (
            patient_id,
            description.strip(),
            tooth_number.strip(),
            datetime.now().strftime("%Y-%m-%d"),
        ),
    )
    conn.commit()
    conn.close()


def get_visits(patient_id: int) -> list[tuple]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, description, tooth_number, date
        FROM visits
        WHERE patient_id = ?
        ORDER BY id DESC
        """,
        (patient_id,),
    )
    visits = cursor.fetchall()
    conn.close()
    return visits


def delete_visit(visit_id: int) -> None:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM visits WHERE id = ?", (visit_id,))
    conn.commit()
    conn.close()
