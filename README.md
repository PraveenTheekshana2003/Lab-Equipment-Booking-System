# Lab Equipment Booking System

A web-based Lab Equipment Booking System built with Flask, SQLite, and pytest to manage equipment reservations for university students and lab staff.

---

## Group Members & GitHub Usernames

| Name               | GitHub Username       | Module Allocation              | Coordination Role |
| :----------------- | :-------------------- | :----------------------------- | :---------------- |
| M.P.Theekshana     | PraveenTheekshana2003 | M1: Accounts & Authentication  | Project Manager   |
| W.T.Subhani        | Tharu-S               | M2: Equipment Catalogue        | QA Lead           |
| G.S.Vimukthi       | Shahanvimukthi        | M3: Booking Form & Model       | GitHub / CI Lead  |
| G.D.Navodya        | DiniNavoR             | M4: Validation & Tests         | Review Lead       |
| R.A.D.G.Y.Ranawaka | Githmi812             | M5: Approval, Integration & CI |                   |

---

## Software Requirements

* **Python** (version 3.11 or newer)
* **Flask** & **Flask-SQLAlchemy**
* **pytest** & **pytest-cov**
* **Ruff** (for code linting)
* **Git** & **GitHub Actions**

---

## Installation Instructions

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/PraveenTheekshana2003/Lab-Equipment-Booking-System.git](https://github.com/PraveenTheekshana2003/Lab-Equipment-Booking-System.git)
   cd Lab-Equipment-Booking-System


---

## How to Run the Application

1. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate


$$ Install the dependencies:
pip install -r requirements.txt

$$ Initialize the database and run the Flask development server
python app.py
Note : Open your browser and navigate to http://127.0.0.1:5000


---

## How to Run the Tests and Linting

$$ Run code linting with Ruff
ruff check .

$$ Run automated tests with pytest
pytest

$$ Run tests with line coverage (pytest-cov)
pytest --cov=.
