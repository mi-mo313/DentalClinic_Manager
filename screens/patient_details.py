import os

import customtkinter as ctk
from PIL import Image
from tkinter import filedialog, messagebox

from models.image import add_image, delete_image, get_images
from models.patient import (
    add_payment,
    delete_patient,
    get_balance,
    get_patient,
    get_payments,
)
from models.visit import add_visit, delete_visit, get_visits
from services.backup import create_backup
from services.pdf import create_invoice
from ui.constants import BODY_FONT, HEADING_FONT, SMALL_FONT, SUBHEADING_FONT, TITLE_FONT


class PatientDetails(ctk.CTkFrame):
    THUMB_SIZE = (120, 120)

    def __init__(self, parent, patient_id: int, back_callback, edit_callback=None, delete_callback=None):
        super().__init__(parent, fg_color="transparent")

        self.patient_id = patient_id
        self.back_callback = back_callback
        self.edit_callback = edit_callback
        self.delete_callback = delete_callback
        self._image_refs: list[ctk.CTkImage] = []

        self.grid(row=0, column=0, sticky="nsew")
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)

        if not get_patient(patient_id):
            messagebox.showerror("Error", "Patient not found.")
            self.after(0, back_callback)
            return

        self._build_ui()
        self.refresh_all()

    def _build_ui(self):
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=24, pady=20)

        header = ctk.CTkFrame(scroll, fg_color="transparent")
        header.pack(fill="x", pady=(0, 12))

        self.title_label = ctk.CTkLabel(header, text="", font=TITLE_FONT, anchor="w")
        self.title_label.pack(side="left")

        ctk.CTkButton(header, text="Back", width=90, command=self.back_callback).pack(side="right")

        self.info_label = ctk.CTkLabel(
            scroll,
            text="",
            font=BODY_FONT,
            justify="left",
            anchor="w",
        )
        self.info_label.pack(fill="x", pady=(0, 16))

        self._build_payments_section(scroll)
        self._build_visits_section(scroll)
        self._build_images_section(scroll)
        self._build_actions(scroll)

    def _build_payments_section(self, parent):
        ctk.CTkLabel(parent, text="Payments", font=HEADING_FONT, anchor="w").pack(
            fill="x", pady=(8, 6)
        )

        payment_frame = ctk.CTkFrame(parent)
        payment_frame.pack(fill="x", pady=(0, 8))

        self.payment_entry = ctk.CTkEntry(
            payment_frame,
            width=180,
            placeholder_text="Amount",
        )
        self.payment_entry.grid(row=0, column=0, padx=12, pady=12)

        ctk.CTkButton(
            payment_frame,
            text="Add Payment",
            command=self._add_payment,
        ).grid(row=0, column=1, padx=12, pady=12)

        self.payments_box = ctk.CTkTextbox(parent, height=120)
        self.payments_box.pack(fill="x", pady=(0, 12))
        self.payments_box.configure(state="disabled")

    def _build_visits_section(self, parent):
        ctk.CTkLabel(parent, text="Visits", font=HEADING_FONT, anchor="w").pack(
            fill="x", pady=(8, 6)
        )

        visit_form = ctk.CTkFrame(parent)
        visit_form.pack(fill="x", pady=(0, 8))

        self.tooth_entry = ctk.CTkEntry(visit_form, width=120, placeholder_text="Tooth #")
        self.tooth_entry.grid(row=0, column=0, padx=10, pady=12)

        self.visit_desc_entry = ctk.CTkEntry(
            visit_form,
            width=320,
            placeholder_text="Visit description",
        )
        self.visit_desc_entry.grid(row=0, column=1, padx=10, pady=12)

        ctk.CTkButton(visit_form, text="Add Visit", command=self._add_visit).grid(
            row=0, column=2, padx=10, pady=12
        )

        self.visits_frame = ctk.CTkFrame(parent, fg_color="transparent")
        self.visits_frame.pack(fill="x", pady=(0, 12))

    def _build_images_section(self, parent):
        images_header = ctk.CTkFrame(parent, fg_color="transparent")
        images_header.pack(fill="x", pady=(8, 6))

        ctk.CTkLabel(images_header, text="X-Rays / Images", font=HEADING_FONT, anchor="w").pack(
            side="left"
        )
        ctk.CTkButton(
            images_header,
            text="Add Image",
            width=120,
            command=self._add_image,
        ).pack(side="right")

        self.images_frame = ctk.CTkFrame(parent, fg_color="transparent")
        self.images_frame.pack(fill="x", pady=(0, 12))

    def _build_actions(self, parent):
        ctk.CTkLabel(parent, text="Actions", font=SUBHEADING_FONT, anchor="w").pack(
            fill="x", pady=(8, 6)
        )

        buttons = ctk.CTkFrame(parent, fg_color="transparent")
        buttons.pack(fill="x", pady=(0, 20))

        actions = [
            ("Generate PDF", self._make_pdf),
            ("Create Backup", self._backup),
        ]
        if self.edit_callback:
            actions.append(("Edit Patient", lambda: self.edit_callback(self.patient_id)))
        actions.append(("Delete Patient", self._delete_patient))

        for index, (label, command) in enumerate(actions):
            color = "#b91c1c" if label == "Delete Patient" else None
            hover = "#991b1b" if label == "Delete Patient" else None
            btn_kwargs = {"text": label, "command": command, "width": 140}
            if color:
                btn_kwargs["fg_color"] = color
                btn_kwargs["hover_color"] = hover
            ctk.CTkButton(buttons, **btn_kwargs).grid(row=0, column=index, padx=6, pady=4)

    def refresh_all(self):
        patient = get_patient(self.patient_id)
        balance = get_balance(self.patient_id)
        if not patient or not balance:
            return

        self.title_label.configure(text=patient[1])
        self.info_label.configure(
            text=(
                f"Phone: {patient[2] or '-'}\n\n"
                f"Notes:\n{patient[3] or '-'}\n\n"
                f"Total: {balance['total']:.2f}\n"
                f"Paid: {balance['paid']:.2f}\n"
                f"Remaining: {balance['remaining']:.2f}"
            )
        )
        self._load_payments()
        self._load_visits()
        self._load_images()

    def _load_payments(self):
        self.payments_box.configure(state="normal")
        self.payments_box.delete("1.0", "end")

        payments = get_payments(self.patient_id)
        if payments:
            for amount, date in payments:
                self.payments_box.insert("end", f"{date}: {amount:.2f}\n")
        else:
            self.payments_box.insert("end", "No payments recorded.\n")

        self.payments_box.configure(state="disabled")

    def _load_visits(self):
        for widget in self.visits_frame.winfo_children():
            widget.destroy()

        visits = get_visits(self.patient_id)
        if not visits:
            ctk.CTkLabel(
                self.visits_frame,
                text="No visits recorded.",
                font=SMALL_FONT,
                text_color="gray",
            ).pack(anchor="w")
            return

        for visit_id, description, tooth_number, date in visits:
            row = ctk.CTkFrame(self.visits_frame)
            row.pack(fill="x", pady=4)

            text = f"{date}  |  Tooth {tooth_number or '-'}  |  {description or '-'}"
            ctk.CTkLabel(row, text=text, font=BODY_FONT, anchor="w").pack(
                side="left", fill="x", expand=True, padx=12, pady=10
            )
            ctk.CTkButton(
                row,
                text="Delete",
                width=70,
                fg_color="#b91c1c",
                hover_color="#991b1b",
                command=lambda vid=visit_id: self._remove_visit(vid),
            ).pack(side="right", padx=10, pady=8)

    def _load_images(self):
        for widget in self.images_frame.winfo_children():
            widget.destroy()
        self._image_refs.clear()

        images = get_images(self.patient_id)
        if not images:
            ctk.CTkLabel(
                self.images_frame,
                text="No images uploaded.",
                font=SMALL_FONT,
                text_color="gray",
            ).pack(anchor="w")
            return

        grid = ctk.CTkFrame(self.images_frame, fg_color="transparent")
        grid.pack(fill="x")

        for index, (image_id, path, date) in enumerate(images):
            card = ctk.CTkFrame(grid)
            card.grid(row=index // 4, column=index % 4, padx=8, pady=8)

            thumb = self._make_thumbnail(path)
            if thumb:
                ctk.CTkLabel(card, text="", image=thumb).pack(padx=8, pady=(8, 4))
            else:
                ctk.CTkLabel(card, text=os.path.basename(path), font=SMALL_FONT).pack(
                    padx=8, pady=(8, 4)
                )

            ctk.CTkLabel(card, text=date, font=SMALL_FONT, text_color="gray").pack()
            ctk.CTkButton(
                card,
                text="Open",
                width=70,
                command=lambda p=path: self._open_image(p),
            ).pack(pady=(4, 0))
            ctk.CTkButton(
                card,
                text="Delete",
                width=70,
                fg_color="#b91c1c",
                hover_color="#991b1b",
                command=lambda iid=image_id: self._remove_image(iid),
            ).pack(pady=(4, 8))

    def _make_thumbnail(self, path: str) -> ctk.CTkImage | None:
        if not os.path.isfile(path):
            return None
        try:
            image = Image.open(path)
            image.thumbnail(self.THUMB_SIZE)
            ctk_image = ctk.CTkImage(light_image=image, dark_image=image, size=image.size)
            self._image_refs.append(ctk_image)
            return ctk_image
        except OSError:
            return None

    def _add_payment(self):
        raw = self.payment_entry.get().strip()
        if not raw:
            messagebox.showerror("Validation Error", "Enter a payment amount.")
            return

        try:
            amount = float(raw)
        except ValueError:
            messagebox.showerror("Validation Error", "Enter a valid payment amount.")
            return

        if amount <= 0:
            messagebox.showerror("Validation Error", "Payment must be greater than zero.")
            return

        try:
            add_payment(self.patient_id, amount)
        except Exception as exc:
            messagebox.showerror("Error", f"Could not add payment:\n{exc}")
            return

        self.payment_entry.delete(0, "end")
        messagebox.showinfo("Success", "Payment added.")
        self.refresh_all()

    def _add_visit(self):
        tooth = self.tooth_entry.get().strip()
        description = self.visit_desc_entry.get().strip()

        if not description:
            messagebox.showerror("Validation Error", "Visit description is required.")
            return

        try:
            add_visit(self.patient_id, description, tooth)
        except Exception as exc:
            messagebox.showerror("Error", f"Could not add visit:\n{exc}")
            return

        self.tooth_entry.delete(0, "end")
        self.visit_desc_entry.delete(0, "end")
        messagebox.showinfo("Success", "Visit added.")
        self._load_visits()

    def _remove_visit(self, visit_id: int):
        if not messagebox.askyesno("Confirm", "Delete this visit?"):
            return
        try:
            delete_visit(visit_id)
        except Exception as exc:
            messagebox.showerror("Error", f"Could not delete visit:\n{exc}")
            return
        self._load_visits()

    def _add_image(self):
        file_path = filedialog.askopenfilename(
            title="Select Image",
            filetypes=[
                ("Image files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif;*.webp"),
                ("All files", "*.*"),
            ],
        )
        if not file_path:
            return

        try:
            add_image(self.patient_id, file_path)
        except Exception as exc:
            messagebox.showerror("Error", f"Could not add image:\n{exc}")
            return

        messagebox.showinfo("Success", "Image added.")
        self._load_images()

    def _remove_image(self, image_id: int):
        if not messagebox.askyesno("Confirm", "Delete this image?"):
            return
        try:
            delete_image(image_id)
        except Exception as exc:
            messagebox.showerror("Error", f"Could not delete image:\n{exc}")
            return
        self._load_images()

    def _open_image(self, path: str):
        if not os.path.isfile(path):
            messagebox.showerror("Error", "Image file not found.")
            return
        try:
            os.startfile(path)
        except OSError as exc:
            messagebox.showerror("Error", f"Could not open image:\n{exc}")

    def _make_pdf(self):
        try:
            file_path = create_invoice(self.patient_id)
        except Exception as exc:
            messagebox.showerror("Error", f"Could not create invoice:\n{exc}")
            return
        messagebox.showinfo("PDF Created", f"Invoice saved to:\n{file_path}")

    def _backup(self):
        try:
            folder = create_backup()
        except Exception as exc:
            messagebox.showerror("Error", f"Backup failed:\n{exc}")
            return
        messagebox.showinfo("Backup Complete", f"Backup saved to:\n{folder}")

    def _delete_patient(self):
        if not messagebox.askyesno(
            "Delete Patient",
            "Delete this patient and all related payments, visits, and images?",
        ):
            return

        try:
            delete_patient(self.patient_id)
        except Exception as exc:
            messagebox.showerror("Error", f"Could not delete patient:\n{exc}")
            return

        messagebox.showinfo("Deleted", "Patient deleted successfully.")
        if self.delete_callback:
            self.delete_callback()
        else:
            self.back_callback()
