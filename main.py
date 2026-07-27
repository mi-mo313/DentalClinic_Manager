import customtkinter as ctk

from database import create_tables
from paths import ensure_app_dirs
from screens.add_patient import AddPatient
from screens.dashboard import Dashboard
from screens.patient_details import PatientDetails
from screens.patient_edit import PatientEdit


class DentalApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Dental Clinic Manager")
        self.geometry("1200x800")
        self.minsize(960, 640)

        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.current_page = None
        self.show_dashboard()

    def clear_page(self):
        if self.current_page is not None:
            self.current_page.destroy()
            self.current_page = None

    def show_dashboard(self):
        self.clear_page()
        self.current_page = Dashboard(self)
        self.current_page.open_callback = self.show_patient_details
        self.current_page.add_callback = self.show_add_patient

    def show_patient_details(self, patient_id: int):
        self.clear_page()
        self.current_page = PatientDetails(
            parent=self,
            patient_id=patient_id,
            back_callback=self.show_dashboard,
            edit_callback=self.show_edit,
            delete_callback=self.show_dashboard,
        )

    def show_edit(self, patient_id: int):
        self.clear_page()
        self.current_page = PatientEdit(
            parent=self,
            patient_id=patient_id,
            back_callback=lambda: self.show_patient_details(patient_id),
        )

    def show_add_patient(self):
        self.clear_page()
        self.current_page = AddPatient(self, self.show_dashboard)


def main():
    ensure_app_dirs()
    create_tables()

    app = DentalApp()
    app.mainloop()


if __name__ == "__main__":
    main()
