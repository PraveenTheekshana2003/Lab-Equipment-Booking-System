"""
Lab Equipment Booking System
Flask application implementing FR-00 to FR-04.
"""

import os
from datetime import date, datetime, time
from functools import wraps

from flask import (
    Flask,
    abort,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import (
    LoginManager,
    UserMixin,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

# ---------------------------------------------------------------------------
# App configuration
# ---------------------------------------------------------------------------
app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-change-in-production")
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL", "sqlite:///" + os.path.join(app.instance_path, "lab_booking.db")
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

os.makedirs(app.instance_path, exist_ok=True)

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message_category = "warning"


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------
class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="student")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    bookings = db.relationship("Booking", backref="user", lazy=True)

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    @property
    def is_staff(self) -> bool:
        return self.role == "staff"


class Equipment(db.Model):
    __tablename__ = "equipment"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    category = db.Column(db.String(80), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), nullable=False, default="Available")
    image = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    bookings = db.relationship("Booking", backref="equipment", lazy=True)

    @property
    def is_available(self) -> bool:
        return self.status == "Available"


class Booking(db.Model):
    __tablename__ = "bookings"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    equipment_id = db.Column(db.Integer, db.ForeignKey("equipment.id"), nullable=False)
    booking_date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    status = db.Column(db.String(20), nullable=False, default="Pending")
    rejection_reason = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def duration_minutes(self) -> int:
        start_dt = datetime.combine(self.booking_date, self.start_time)
        end_dt = datetime.combine(self.booking_date, self.end_time)
        return int((end_dt - start_dt).total_seconds() / 60)


# ---------------------------------------------------------------------------
# Auth helpers
# ---------------------------------------------------------------------------
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


def staff_required(f):
    """Decorator: only staff users may access the view."""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_staff:
            flash("Staff access required.", "danger")
            return redirect(url_for("dashboard"))
        return f(*args, **kwargs)

    return decorated_function


# ---------------------------------------------------------------------------
# Booking validation (FR-03)
# ---------------------------------------------------------------------------
def validate_booking(
    equipment: Equipment,
    booking_date: date,
    start_time: time,
    end_time: time,
    exclude_booking_id: int | None = None,
) -> list[str]:
    """Validate a booking request against all FR-03 rules."""
    errors: list[str] = []

    if end_time <= start_time:
        errors.append("End time must be later than start time.")

    start_dt = datetime.combine(booking_date, start_time)
    end_dt = datetime.combine(booking_date, end_time)
    duration = (end_dt - start_dt).total_seconds() / 60
    if duration < 30:
        errors.append("Booking must last at least 30 minutes.")
    if duration > 240:
        errors.append("Booking cannot exceed 4 hours.")

    now = datetime.now()
    if start_dt < now:
        errors.append("Booking cannot start in the past.")

    if equipment.status == "Out of service":
        errors.append("This equipment is currently out of service and cannot be booked.")

    query = Booking.query.filter(
        Booking.equipment_id == equipment.id,
        Booking.booking_date == booking_date,
        Booking.status.in_(["Pending", "Approved"]),
    )
    if exclude_booking_id:
        query = query.filter(Booking.id != exclude_booking_id)

    for b in query.all():
        if start_time < b.end_time and end_time > b.start_time:
            errors.append(
                f"Overlaps with an existing {b.status.lower()} booking "
                f"({b.start_time.strftime('%H:%M')} – {b.end_time.strftime('%H:%M')})."
            )
            break

    return errors


# ---------------------------------------------------------------------------
# Routes – Public / Auth (FR-00)
# ---------------------------------------------------------------------------
@app.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")

        errors = []
        if not username or len(username) < 3:
            errors.append("Username must be at least 3 characters.")
        if not email or "@" not in email:
            errors.append("A valid email address is required.")
        if not password or len(password) < 6:
            errors.append("Password must be at least 6 characters.")
        if password != confirm:
            errors.append("Passwords do not match.")
        if User.query.filter_by(username=username).first():
            errors.append("Username already taken.")
        if User.query.filter_by(email=email).first():
            errors.append("Email already registered.")

        if errors:
            for e in errors:
                flash(e, "danger")
            return render_template("login.html", active_tab="register")

        user = User(username=username, email=email, role="student")
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash("Registration successful! Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("login.html", active_tab="register")


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            flash(f"Welcome back, {user.username}!", "success")
            next_page = request.args.get("next")
            return redirect(next_page or url_for("dashboard"))
        flash("Invalid username or password.", "danger")

    return render_template("login.html", active_tab="login")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("index"))


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------
@app.route("/dashboard")
@login_required
def dashboard():
    if current_user.is_staff:
        pending_count = Booking.query.filter_by(status="Pending").count()
        approved_count = Booking.query.filter_by(status="Approved").count()
        total_equipment = Equipment.query.count()
        available_equipment = Equipment.query.filter_by(status="Available").count()
        recent_bookings = (
            Booking.query.order_by(Booking.created_at.desc()).limit(8).all()
        )
        return render_template(
            "dashboard.html",
            pending_count=pending_count,
            approved_count=approved_count,
            total_equipment=total_equipment,
            available_equipment=available_equipment,
            recent_bookings=recent_bookings,
        )
    else:
        my_bookings = (
            Booking.query.filter_by(user_id=current_user.id)
            .order_by(Booking.created_at.desc())
            .limit(8)
            .all()
        )
        return render_template("dashboard.html", my_bookings=my_bookings)


# ---------------------------------------------------------------------------
# Equipment Catalogue (FR-01)
# ---------------------------------------------------------------------------
@app.route("/equipment")
@login_required
def equipment_list():
    category = request.args.get("category", "").strip()
    query = Equipment.query
    if category:
        query = query.filter_by(category=category)
    items = query.order_by(Equipment.name).all()
    categories = (
        db.session.query(Equipment.category).distinct().order_by(Equipment.category).all()
    )
    categories = [c[0] for c in categories]
    return render_template(
        "equipment.html",
        equipment=items,
        categories=categories,
        selected_category=category,
    )


@app.route("/equipment/add", methods=["GET", "POST"])
@login_required
@staff_required
def equipment_add():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        category = request.form.get("category", "").strip()
        description = request.form.get("description", "").strip()
        status = request.form.get("status", "Available")
        image = request.form.get("image", "").strip() or None

        if not name or not category or not description:
            flash("Name, category and description are required.", "danger")
            return render_template("equipment_form.html", equipment=None)

        eq = Equipment(
            name=name,
            category=category,
            description=description,
            status=status,
            image=image,
        )
        db.session.add(eq)
        db.session.commit()
        flash(f"Equipment '{name}' added successfully.", "success")
        return redirect(url_for("equipment_list"))

    return render_template("equipment_form.html", equipment=None)


@app.route("/equipment/<int:eq_id>/edit", methods=["GET", "POST"])
@login_required
@staff_required
def equipment_edit(eq_id):
    eq = db.session.get(Equipment, eq_id)
    if not eq:
        abort(404)

    if request.method == "POST":
        eq.name = request.form.get("name", "").strip()
        eq.category = request.form.get("category", "").strip()
        eq.description = request.form.get("description", "").strip()
        eq.status = request.form.get("status", "Available")
        eq.image = request.form.get("image", "").strip() or None

        if not eq.name or not eq.category or not eq.description:
            flash("Name, category and description are required.", "danger")
            return render_template("equipment_form.html", equipment=eq)

        db.session.commit()
        flash(f"Equipment '{eq.name}' updated.", "success")
        return redirect(url_for("equipment_list"))

    return render_template("equipment_form.html", equipment=eq)


@app.route("/equipment/<int:eq_id>/delete", methods=["POST"])
@login_required
@staff_required
def equipment_delete(eq_id):
    eq = db.session.get(Equipment, eq_id)
    if not eq:
        abort(404)
    name = eq.name
    db.session.delete(eq)
    db.session.commit()
    flash(f"Equipment '{name}' deleted.", "info")
    return redirect(url_for("equipment_list"))


# ---------------------------------------------------------------------------
# Booking Request (FR-02) + Validation (FR-03)
# ---------------------------------------------------------------------------
@app.route("/bookings")
@login_required
def bookings():
    if current_user.is_staff:
        status_filter = request.args.get("status", "")
        query = Booking.query
        if status_filter:
            query = query.filter_by(status=status_filter)
        all_bookings = query.order_by(Booking.created_at.desc()).all()
        return render_template(
            "bookings.html",
            bookings=all_bookings,
            status_filter=status_filter,
            is_staff=True,
        )
    else:
        my_bookings = (
            Booking.query.filter_by(user_id=current_user.id)
            .order_by(Booking.created_at.desc())
            .all()
        )
        return render_template(
            "bookings.html",
            bookings=my_bookings,
            status_filter="",
            is_staff=False,
        )


@app.route("/bookings/request", methods=["GET", "POST"])
@login_required
def booking_request():
    equipment_list_ = (
        Equipment.query.filter_by(status="Available").order_by(Equipment.name).all()
    )

    if request.method == "POST":
        equipment_id = request.form.get("equipment_id", type=int)
        booking_date_str = request.form.get("booking_date", "")
        start_time_str = request.form.get("start_time", "")
        end_time_str = request.form.get("end_time", "")

        equipment = db.session.get(Equipment, equipment_id) if equipment_id else None
        if not equipment:
            flash("Please select a valid equipment item.", "danger")
            return render_template("booking_form.html", equipment_list=equipment_list_)

        try:
            booking_date = datetime.strptime(booking_date_str, "%Y-%m-%d").date()
            start_time = datetime.strptime(start_time_str, "%H:%M").time()
            end_time = datetime.strptime(end_time_str, "%H:%M").time()
        except ValueError:
            flash("Invalid date or time format.", "danger")
            return render_template("booking_form.html", equipment_list=equipment_list_)

        errors = validate_booking(equipment, booking_date, start_time, end_time)
        if errors:
            for e in errors:
                flash(e, "danger")
            return render_template(
                "booking_form.html",
                equipment_list=equipment_list_,
                form_data=request.form,
            )

        booking = Booking(
            user_id=current_user.id,
            equipment_id=equipment.id,
            booking_date=booking_date,
            start_time=start_time,
            end_time=end_time,
            status="Pending",
        )
        db.session.add(booking)
        db.session.commit()
        flash("Booking request submitted successfully. Status: Pending.", "success")
        return redirect(url_for("bookings"))

    return render_template("booking_form.html", equipment_list=equipment_list_)


# ---------------------------------------------------------------------------
# Booking Approval (FR-04)
# ---------------------------------------------------------------------------
@app.route("/bookings/<int:booking_id>/approve", methods=["POST"])
@login_required
@staff_required
def booking_approve(booking_id):
    booking = db.session.get(Booking, booking_id)
    if not booking:
        abort(404)
    if booking.status != "Pending":
        flash("Only pending bookings can be approved.", "warning")
        return redirect(url_for("bookings"))

    errors = validate_booking(
        booking.equipment,
        booking.booking_date,
        booking.start_time,
        booking.end_time,
        exclude_booking_id=booking.id,
    )
    if errors:
        flash("Cannot approve: " + "; ".join(errors), "danger")
        return redirect(url_for("bookings"))

    booking.status = "Approved"
    db.session.commit()
    flash(f"Booking #{booking.id} approved.", "success")
    return redirect(url_for("bookings"))


@app.route("/bookings/<int:booking_id>/reject", methods=["POST"])
@login_required
@staff_required
def booking_reject(booking_id):
    booking = db.session.get(Booking, booking_id)
    if not booking:
        abort(404)
    if booking.status != "Pending":
        flash("Only pending bookings can be rejected.", "warning")
        return redirect(url_for("bookings"))

    reason = request.form.get("rejection_reason", "").strip()
    booking.status = "Rejected"
    booking.rejection_reason = reason or None
    db.session.commit()
    flash(f"Booking #{booking.id} rejected.", "info")
    return redirect(url_for("bookings"))


# ---------------------------------------------------------------------------
# About
# ---------------------------------------------------------------------------
@app.route("/about")
def about():
    return render_template("about.html")


# ---------------------------------------------------------------------------
# Seed data (matches what the tests expect)
# ---------------------------------------------------------------------------
def seed_data():
    """Create staff, student and sample equipment if database is empty."""
    if User.query.filter_by(role="staff").first():
        return

    # id=1 → staff
    staff = User(username="staff", email="staff@lab.edu", role="staff")
    staff.set_password("staff123")
    db.session.add(staff)

    # id=2 → student  (tests use user_id=2)
    student = User(username="student", email="student@lab.edu", role="student")
    student.set_password("student123")
    db.session.add(student)

    samples = [
        {
            "name": "Test Pi",
            "category": "SBC",
            "description": "Test Raspberry Pi kit used by automated tests.",
            "status": "Available",
            "image": "raspberry-pi.jpg",
        },
        {
            "name": "Broken Scope",
            "category": "Test equipment",
            "description": "Out of service oscilloscope for validation tests.",
            "status": "Out of service",
            "image": None,
        },
        {
            "name": "Raspberry Pi 4 Kit",
            "category": "Single-board computers",
            "description": "Complete Raspberry Pi 4 starter kit.",
            "status": "Available",
            "image": "raspberry-pi.jpg",
        },
        {
            "name": "Arduino Uno Kit",
            "category": "Microcontrollers",
            "description": "Arduino Uno R3 with sensors and breadboard.",
            "status": "Available",
            "image": "arduino.jpg",
        },
        {
            "name": "Digital Oscilloscope",
            "category": "Test equipment",
            "description": "100 MHz dual-channel digital storage oscilloscope.",
            "status": "Available",
            "image": "oscilloscope.jpg",
        },
        {
            "name": "VR Headset (Meta Quest)",
            "category": "Virtual Reality",
            "description": "Standalone VR headset for immersive experiences.",
            "status": "Available",
            "image": "vr-headset.jpg",
        },
        {
            "name": "3D Printer (Ender-3)",
            "category": "Fabrication",
            "description": "FDM 3D printer with heated bed.",
            "status": "Available",
            "image": "3d-printer.jpg",
        },
    ]
    for s in samples:
        db.session.add(Equipment(**s))

    db.session.commit()
    print("Seed data created: staff/staff123, student/student123 + equipment.")


@app.cli.command("init-db")
def init_db_command():
    """Initialise the database and seed sample data."""
    db.create_all()
    seed_data()
    print("Database initialised.")


def create_app(test_config=None):
    """Return configured app (used by tests)."""
    if test_config:
        app.config.update(test_config)
    return app


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        seed_data()
    app.run(debug=True, port=5000)