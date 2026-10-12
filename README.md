# Lab Equipment Booking System

A web-based Lab Equipment Booking System built with Flask, SQLite, and pytest to manage equipment reservations for university students and lab staff.

---

## Group Members & GitHub Usernames

| Name               | Index No | Reg No       | GitHub Username       | Module Allocation                | Coordination Role |
| :----------------- | :------- | :----------- | :-------------------- | :------------------------------- | :---------------- |
| M.P.Theekshana     |    6316  | ASP/2023/165 | PraveenTheekshana2003 | M1: Accounts & Authentication    | Project Manager   |
| W.T.Subhani        |    6243  | ASP/2023/102 | Tharu-S               | M2: Equipment Catalogue          | QA Lead           |
| G.S.Vimukthi       |    6215  | ASP/2023/035 | Shahanvimukthi        | M3: Booking Form & Model         | GitHub / CI Lead  |
| G.D.Navodya        |    6219  | ASP/2023/024 | DiniNavoR             | M4: Validation & Tests           | Review Lead       |
| R.A.D.G.Y.Ranawaka |    6311  | ASP/2023/158 | Githmi812             | M5: Approval, Integration & CI   | Coordinator       |

---

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

$$ Run code linting with Ruff -> 
ruff check .

$$ Run automated tests with pytest -> 
pytest

$$ Run tests with line coverage (pytest-cov) -> 
pytest --cov=.
