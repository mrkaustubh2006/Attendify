# Smart Attendance System
A modern, production-ready, and secure QR-based attendance management system built for colleges and schools. The application uses a modular clean architecture with custom glassmorphic dashboards, light/dark themes, role-based authorization, and instant Excel/PDF reporting.
---
## 🚀 Key Features
- **Anti-Cheat QR Scanner:** Teachers start real-time sessions targeting a specific class and subject. Students scan dynamic QR passes using their phone or webcam; duplicate scans or cross-class scans are automatically prevented.
- **Three User Roles:**
  - **Admin:** Dashboard charts, full CRUD (Students, Teachers, Subjects), view logs, system exports.
  - **Teacher:** Session manager, live camera scanner queue, spreadsheet/PDF export filters.
  - **Student:** Profile view, subject-wise attendance percentages, dynamic QR code renderer, QR download.
- **Modern Responsive Design:** Crafted with customized slate theme tokens, glassmorphism card highlights, micro-animations, and full mobile optimization.
---
## 🛠️ Tech Stack & Libraries
- **Backend:** Flask, Flask-SQLAlchemy (ORM), Flask-Bcrypt (password crypts), Flask-Login (session controls), Flask-JWT-Extended (secure API scanner authorizations).
- **Database:** MySQL (Default production database, auto-fallbacks to SQLite for easy local testing).
- **Frontend:** HTML5, CSS3, Bootstrap 5, Javascript, Chart.js (dashboard metrics), `html5-qrcode` (HTML5 device camera reading).
- **Reporting & Generation:** `pandas` and `openpyxl` (Excel), `reportlab` (PDF), `qrcode` (dynamic QR code generator).
---
## 📂 Project Directory Structure
```text
Smart-Attendance/
│
├── app.py                 # Central app orchestrator & db bootstrapper
├── config.py              # System path configuration and fallback rules
├── requirements.txt       # Dependencies manifest
├── .env                   # Local env configuration template
│
├── database/
│   └── schema.sql         # Raw MySQL DDL schema dump
│
├── models/
│   ├── __init__.py        # Models entry export
│   ├── database.py        # SQLAlchemy database instance
│   ├── user.py            # User credentials model
│   ├── student.py         # Student metadata & QR tokens
│   ├── teacher.py         # Teacher metadata
│   ├── subject.py         # Subject model
│   └── attendance.py      # Attendance records & scanning session tracker
│
├── routes/
│   ├── auth.py            # Registrations, Logins, Logouts (session + JWT)
│   ├── admin.py           # Admin dashboards and CRUDs
│   ├── teacher.py         # Teacher launcher control panel
│   ├── student.py         # Student dashboard and QR downloads
│   └── api.py             # REST API for scanner updates and exports
│
├── services/
│   ├── qr_service.py      # Dynamic base64 QR generators
│   └── export_service.py  # Pandas & Reportlab export generation
│
├── static/
│   ├── css/
│   │   └── styles.css     # Theme variables, glassmorphism cards, layouts
│   └── js/
│       └── app.js         # Theme toggle caching and menu interactions
│
├── templates/             # HTML templates (base, dashboards, scanner, CRUDs)
│   ├── admin/
│   ├── teacher/
│   └── student/
│
└── tests/                 # Automation suite
```
---
## ⚙️ Setup and Installation
### 1. Clone & Navigate
Ensure you are in the project folder root:
```bash
cd SmartAttendance
```
### 2. Environment Configuration
Create a `.env` file in the root based on the template:
```env
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=dev_secret_key_change_in_production_12345
JWT_SECRET_KEY=jwt_secret_key_change_in_production_54321