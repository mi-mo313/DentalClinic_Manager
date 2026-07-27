import customtkinter as ctk
from tkinter import messagebox

from models.patient import get_patient, update_patient
from ui.constants import BODY_FONT, ENTRY_WIDTH, TEXTBOX_HEIGHT, TITLE_FONT


class PatientEdit(ctk.CTkFrame):
    def __init__(self, parent, patient_id: int, back_callback):
        super().__init__(parent, fg_color="transparent")

        self.patient_id = patient_id
        self.back_callback = back_callback

        self.grid(row=0, column=0, sticky="nsew")
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)

        patient = get_patient(patient_id)
        if not patient:
            messagebox.showerror("Error", "Patient not found.")
            self.after(0, back_callback)
            return

        form = ctk.CTkScrollableFrame(self, label_text="Edit Patient", label_font=TITLE_FONT)
        form.pack(fill="both", expand=True, padx=40, pady=30)

        self.name_entry = self._add_field(form, "Patient Name *", patient[1])
        self.phone_entry = self._add_field(form, "Phone Number", patient[2] or "")
        self.total_entry = self._add_field(form, "Total Price *", str(patient[4] or 0))

        ctk.CTkLabel(form, text="Treatment Notes", font=BODY_FONT, anchor="w").pack(
            fill="x", pady=(8, 4)
        )
        self.notes_entry = ctk.CTkTextbox(form, width=ENTRY_WIDTH, height=TEXTBOX_HEIGHT)
        self.notes_entry.pack(anchor="w", pady=(0, 16))
        self.notes_entry.insert("1.0", patient[3] or "")

        buttons = ctk.CTkFrame(form, fg_color="transparent")
        buttons.pack(anchor="w", pady=8)

        ctk.CTkButton(buttons, text="Save Changes", width=140, command=self.save).grid(
            row=0, column=0, padx=(0, 10)
        )
        ctk.CTkButton(
            buttons,
            text="Cancel",
            width=100,
            fg_color="gray",
            hover_color="#555555",
            command=self.back_callback,
        ).grid(row=0, column=1)

    def _add_field(self, parent, label: str, value: str):
        ctk.CTkLabel(parent, text=label, font=BODY_FONT, anchor="w").pack(fill="x", pady=(8, 4))
        entry = ctk.CTkEntry(parent, width=ENTRY_WIDTH)
        entry.pack(anchor="w", pady=(0, 4))
        entry.insert(0, value)
        return entry

    def save(self):
        name = self.name_entry.get().strip()
        phone = self.phone_entry.get().strip()
        notes = self.notes_entry.get("1.0", "end").strip()

        if not name:
            messagebox.showerror("Validation Error", "Patient name is required.")
            return

        try:
            total = float(self.total_entry.get().strip() or "0")
        except ValueError:
            messagebox.showerror("Validation Error", "Please enter a valid total price.")
            return

        if total < 0:
            messagebox.showerror("Validation Error", "Total price cannot be negative.")
            return

        try:
            update_patient(self.patient_id, name, phone, notes, total)
        except Exception as exc:
            messagebox.showerror("Error", f"Could not update patient:\n{exc}")
            return

        messagebox.showinfo("Saved", "Patient updated successfully.")
        self.back_callback()
