# Lab Equipment Booking System

A small web-based system for managing shared lab equipment bookings (Raspberry Pi, Arduino, oscilloscopes, VR headsets, 3D printers, etc.).


## Group Members

| Name | GitHub Username | Registration No | Module | Coordination Role |
|------|-----------------|-----------------|--------|-------------------|
| Praveen Theekshana | PraveenTheekshana2003 |  ASP/2023/165 | M1 – Accounts & Authentication | Project Manager |
| Tharushi Subhani | Tharu-S | ASP/2023/102 | M2 – Equipment Catalogue | QA Lead |
| Shahan Vimukthi | Shahanvimukthi | ASP/2023/035 | M3 – Booking form & model | GitHub/CI Lead |
| Dinithi Nvodya | DiniNavoR | ASP/2023/024 | M4 – Booking validation & tests | Review Lead |
| Githma Yovinma | Githmi812 | ASP/2023/158 | M5 – Approval, integration & CI | Coordinator |


## Features (FR-00 – FR-04)

- **FR-00** Student registration & login; staff accounts seeded; hashed passwords; role-based access
- **FR-01** Equipment catalogue (CRUD for staff); filter by category; status Available / Out of service
- **FR-02** Students request bookings (equipment + date + start/end time)
- **FR-03** Validation: duration 30 min–4 h, no past bookings, no overlaps on Pending/Approved, out-of-service blocked
- **FR-04** Staff approve/reject pending requests; students view own status

## Technology

| Area | Technology |
|------|------------|
| Language | Python 3.11+ |
| Framework | Flask |
| Database | SQLite |
| ORM | Flask-SQLAlchemy |
| Auth | Flask-Login + Werkzeug password hashing |
| Front-end | Jinja2, HTML, CSS (glassmorphism) |
| Testing | pytest + pytest-cov |
| Linting | Ruff |
| CI | GitHub Actions |

## Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd Lab-Equipment-Booking-System

# Create virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Initialise database (creates tables + seed data)
flask --app main init-db
# Or simply run the app once – seed runs automatically
```

## Running the Application

```bash
python main.py
# or
flask --app main run --debug
```

Open http://127.0.0.1:5000

### Default accounts (after seed)

| Role | Username | Password |
|------|----------|----------|
| Staff | `staff` | `staff123` |
| Student | `student` | `student123` |


## Running Tests

```bash
pytest -v
pytest --cov=main --cov-report=term-missing
```

## Project Structure

```
Lab-Equipment-Booking-System/
├── main.py                 # Application, models, routes, validation
├── conftest.py             # Pytest fixtures
├── requirements.txt
├── .gitignore
├── README.md
├── TESTING.md
├── REVIEW_CHECKLIST.md
├── RETROSPECTIVE.md
├── .github/workflows/ci.yml
├── static/
│   ├── css/style.css
│   ├── js/auth.js
│   └── images/             # Place equipment images here
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── dashboard.html
│   ├── equipment.html
│   ├── equipment_form.html
│   ├── bookings.html
│   ├── booking_form.html
│   └── about.html
└── tests/
    ├── test_auth.py
    ├── test_equipment.py
    ├── test_booking_validation.py
    └── test_approval.py
```

## Equipment Images

Place the following images in `static/images/` (filenames used by seed data):

- `raspberry-pi.jpg`
- `arduino.jpg`
- `oscilloscope.jpg`
- `vr-headset.jpg`
- `3d-printer.jpg`


## Security Notes

- Passwords are stored with Werkzeug’s `generate_password_hash` (never plain text).
- Students cannot access staff-only routes (`@staff_required`).
- No secrets committed; use environment variable `SECRET_KEY` for production.
- SQLite DB lives in `instance/` and is git-ignored.
