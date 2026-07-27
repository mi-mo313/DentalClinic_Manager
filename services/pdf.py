import os
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas

from models.patient import get_balance, get_patient, get_payments
from models.visit import get_visits
from paths import INVOICES_DIR, ensure_app_dirs


def _draw_line(pdf, y: float, text: str, font: str = "Helvetica", size: int = 12) -> float:
    pdf.setFont(font, size)
    pdf.drawString(2 * cm, y, text[:110])
    return y - 0.45 * cm


def create_invoice(patient_id: int) -> str:
    ensure_app_dirs()

    patient = get_patient(patient_id)
    if not patient:
        raise ValueError("Patient not found.")

    balance = get_balance(patient_id)
    payments = get_payments(patient_id)
    visits = get_visits(patient_id)

    file_name = os.path.join(
        INVOICES_DIR,
        f"invoice_{patient_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf",
    )

    pdf = canvas.Canvas(file_name, pagesize=A4)
    _, height = A4
    y = height - 2 * cm

    y = _draw_line(pdf, y, "Dental Clinic Invoice", "Helvetica-Bold", 18)
    y -= 0.4 * cm
    y = _draw_line(pdf, y, f"Date: {datetime.now().strftime('%Y-%m-%d')}")
    y = _draw_line(pdf, y, f"Patient: {patient[1]}")
    y = _draw_line(pdf, y, f"Phone: {patient[2] or '-'}")

    y -= 0.3 * cm
    y = _draw_line(pdf, y, "Treatment Notes:", "Helvetica-Bold", 12)
    notes = (patient[3] or "").split("\n") or ["-"]
    for line in notes:
        if y < 3 * cm:
            pdf.showPage()
            y = height - 2 * cm
        y = _draw_line(pdf, y, line)

    y -= 0.3 * cm
    y = _draw_line(pdf, y, f"Total: {balance['total']:.2f}")
    y = _draw_line(pdf, y, f"Paid: {balance['paid']:.2f}")
    y = _draw_line(pdf, y, f"Remaining: {balance['remaining']:.2f}")

    y -= 0.3 * cm
    y = _draw_line(pdf, y, "Payments:", "Helvetica-Bold", 12)
    if payments:
        for amount, date in payments:
            if y < 3 * cm:
                pdf.showPage()
                y = height - 2 * cm
            y = _draw_line(pdf, y, f"{date}: {amount:.2f}")
    else:
        y = _draw_line(pdf, y, "No payments recorded.")

    y -= 0.3 * cm
    y = _draw_line(pdf, y, "Visits:", "Helvetica-Bold", 12)
    if visits:
        for _visit_id, description, tooth_number, date in visits:
            if y < 3 * cm:
                pdf.showPage()
                y = height - 2 * cm
            y = _draw_line(
                pdf,
                y,
                f"{date} | Tooth {tooth_number or '-'} | {description or '-'}",
            )
    else:
        y = _draw_line(pdf, y, "No visits recorded.")

    pdf.save()
    return file_name
