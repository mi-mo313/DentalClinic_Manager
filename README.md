# DentalClinic Manager

DentalClinic Manager is a desktop application for managing day-to-day operations in a dental clinic. It is built with Python and designed to run completely offline using a local SQLite database.

The project focuses on simplicity, reliability, and ease of deployment. It does not require an internet connection, cloud services, or external APIs, making it suitable for small clinics that prefer to keep all patient data on a local machine.

## Features

- Manage patient records
- Record treatment notes
- Track multiple payments per patient
- Automatically calculate outstanding balances
- Store patient visit history
- Attach X-rays and other medical images
- Generate PDF invoices
- Create local database backups
- Search patients by name or phone number

## Tech Stack

- Python 3
- CustomTkinter
- SQLite
- Pillow
- ReportLab

## Project Structure

```text
DentalClinic_Manager/
│
├── main.py
├── database.py
│
├── models/
├── screens/
├── services/
│
├── data/
├── images/
├── invoices/
└── backups/
```

## Getting Started

Clone the repository:

```bash
git clone https://github.com/your-username/DentalClinic_Manager.git
```

Install the required packages:

```bash
pip install customtkinter pillow reportlab
```

Run the application:

```bash
py main.py
```

## Building an Executable

To create a standalone Windows executable:

```bash
pip install pyinstaller
```

```bash
pyinstaller --onefile --windowed main.py
```

The executable will be available in the `dist` directory.

## Database

The application uses SQLite for local storage.

Current data model includes:

- `patients`
- `payments`
- `visits`
- `images`

All application data remains on the local machine.

## Design Goals

The project was built around a few simple principles:

- Keep the application fully offline.
- Use a lightweight and portable database.
- Keep the codebase modular and easy to maintain.
- Make common clinic tasks quick and straightforward.

## Roadmap

Planned improvements include:

- Appointment scheduling
- Calendar view
- Financial reports
- Treatment templates
- Export to Excel
- Dark mode
- Multi-language support
- Better image management
- Printing support

## License

This project is licensed under the MIT License.
