import customtkinter as ctk

from models.patient import get_balance, get_patients
from ui.constants import BODY_FONT, CARD_CORNER, HEADING_FONT, SMALL_FONT, TITLE_FONT


class Dashboard(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")

        self.open_callback = None
        self.add_callback = None

        self.grid(row=0, column=0, sticky="nsew")
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)

        self._build_ui()
        self.load_patients()

    def _build_ui(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=(24, 12))

        ctk.CTkLabel(
            header,
            text="Dental Clinic Manager",
            font=TITLE_FONT,
        ).pack(side="left")

        ctk.CTkButton(
            header,
            text="+ Add Patient",
            width=140,
            command=self._on_add,
        ).pack(side="right")

        toolbar = ctk.CTkFrame(self, fg_color="transparent")
        toolbar.pack(fill="x", padx=30, pady=(0, 12))

        self.search_entry = ctk.CTkEntry(
            toolbar,
            width=360,
            placeholder_text="Search by name or phone...",
        )
        self.search_entry.pack(side="left", padx=(0, 10))
        self.search_entry.bind("<KeyRelease>", lambda _event: self.load_patients())

        ctk.CTkButton(
            toolbar,
            text="Search",
            width=100,
            command=self.load_patients,
        ).pack(side="left")

        self.empty_label = ctk.CTkLabel(
            self,
            text="No patients found.",
            font=BODY_FONT,
            text_color="gray",
        )

        self.cards_frame = ctk.CTkScrollableFrame(
            self,
            label_text="Patients",
            label_font=HEADING_FONT,
            corner_radius=CARD_CORNER,
        )
        self.cards_frame.pack(fill="both", expand=True, padx=30, pady=(0, 24))

    def _on_add(self):
        if self.add_callback:
            self.add_callback()

    def load_patients(self):
        for widget in self.cards_frame.winfo_children():
            widget.destroy()

        keyword = self.search_entry.get().strip()
        patients = get_patients(keyword)

        if not patients:
            self.empty_label.pack(pady=40)
            return

        self.empty_label.pack_forget()

        for patient in patients:
            self._create_patient_card(patient)

    def _create_patient_card(self, patient):
        patient_id, name, phone, notes, total = patient
        balance = get_balance(patient_id) or {"paid": 0, "remaining": total}

        card = ctk.CTkFrame(self.cards_frame, corner_radius=CARD_CORNER)
        card.pack(fill="x", padx=8, pady=8)

        top = ctk.CTkFrame(card, fg_color="transparent")
        top.pack(fill="x", padx=16, pady=(14, 6))

        ctk.CTkLabel(
            top,
            text=name,
            font=("Segoe UI", 18, "bold"),
        ).pack(side="left")

        ctk.CTkLabel(
            top,
            text=f"Total: {total:.2f}",
            font=SMALL_FONT,
            text_color="#2563eb",
        ).pack(side="right")

        ctk.CTkLabel(
            card,
            text=f"Phone: {phone or '-'}",
            font=BODY_FONT,
            anchor="w",
        ).pack(fill="x", padx=16)

        preview = (notes or "").replace("\n", " ").strip()
        if preview:
            ctk.CTkLabel(
                card,
                text=f"Notes: {preview[:90]}{'...' if len(preview) > 90 else ''}",
                font=SMALL_FONT,
                text_color="gray",
                anchor="w",
            ).pack(fill="x", padx=16, pady=(2, 0))

        ctk.CTkLabel(
            card,
            text=f"Paid: {balance['paid']:.2f}  |  Remaining: {balance['remaining']:.2f}",
            font=SMALL_FONT,
            anchor="w",
        ).pack(fill="x", padx=16, pady=(4, 0))

        ctk.CTkButton(
            card,
            text="Open Patient",
            width=140,
            command=lambda pid=patient_id: self._open_patient(pid),
        ).pack(anchor="e", padx=16, pady=12)

    def _open_patient(self, patient_id: int):
        if self.open_callback:
            self.open_callback(patient_id)
