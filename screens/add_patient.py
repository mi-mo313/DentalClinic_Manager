import customtkinter as ctk
from tkinter import messagebox

from models.patient import add_patient
from ui.constants import BODY_FONT, ENTRY_WIDTH, TEXTBOX_HEIGHT, TITLE_FONT


class AddPatient(ctk.CTkFrame):
    def __init__(self, parent, back_callback):
        super().__init__(parent, fg_color="transparent")
        self.back_callback = back_callback

        self.grid(row=0, column=0, sticky="nsew")
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)

        form = ctk.CTkScrollableFrame(self, label_text="Add New Patient", label_font=TITLE_FONT)
        form.pack(fill="both", expand=True, padx=40, pady=30)

        self.name_entry = self._add_field(form, "Patient Name *")
        self.phone_entry = self._add_field(form, "Phone Number")
        self.total_entry = self._add_field(form, "Total Price *", default="0")

        ctk.CTkLabel(form, text="Treatment Notes", font=BODY_FONT, anchor="w").pack(
            fill="x", pady=(8, 4)
        )
        self.notes_entry = ctk.CTkTextbox(form, width=ENTRY_WIDTH, height=TEXTBOX_HEIGHT)
        self.notes_entry.pack(anchor="w", pady=(0, 16))

        buttons = ctk.CTkFrame(form, fg_color="transparent")
        buttons.pack(anchor="w", pady=8)

        ctk.CTkButton(buttons, text="Save Patient", width=140, command=self.save_patient).grid(
            row=0, column=0, padx=(0, 10)
        )
        ctk.CTkButton(
            buttons,
            text="Back",
            width=100,
            fg_color="gray",
            hover_color="#555555",
            command=self.back_callback,
        ).grid(row=0, column=1)

    def _add_field(self, parent, label: str, default: str = ""):
        ctk.CTkLabel(parent, text=label, font=BODY_FONT, anchor="w").pack(fill="x", pady=(8, 4))
        entry = ctk.CTkEntry(parent, width=ENTRY_WIDTH)
        entry.pack(anchor="w", pady=(0, 4))
        if default:
            entry.insert(0, default)
        return entry

    def save_patient(self):
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
            add_patient(name=name, phone=phone, notes=notes, total=total)
        except Exception as exc:
            messagebox.showerror("Error", f"Could not save patient:\n{exc}")
            return

        messagebox.showinfo("Success", "Patient added successfully.")
        self.back_callback()
