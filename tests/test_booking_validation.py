"""FR-03 – Booking Validation tests (Boundary Value Analysis + Equivalence Partitioning)."""

from datetime import date, time, timedelta

from main import Booking, Equipment, db, validate_booking


def _tomorrow():
    return date.today() + timedelta(days=1)


def _day_after_tomorrow():
    return date.today() + timedelta(days=2)


# ---------------------------------------------------------------------------
# Helper: get the seeded Available equipment
# ---------------------------------------------------------------------------
def get_available_equipment(app):
    with app.app_context():
        return Equipment.query.filter_by(status="Available").first()


def get_oos_equipment(app):
    with app.app_context():
        return Equipment.query.filter_by(status="Out of service").first()


# ---------------------------------------------------------------------------
# Direct unit tests on validate_booking()
# ---------------------------------------------------------------------------

def test_end_time_before_start_time(app):
    """T01 – End time before start time → Reject"""
    eq = get_available_equipment(app)
    errors = validate_booking(eq, _tomorrow(), time(14, 0), time(13, 0))
    assert len(errors) > 0
    assert any("later" in e.lower() or "end" in e.lower() for e in errors)


def test_end_time_equal_start_time(app):
    """T02 – End time equal to start time → Reject"""
    eq = get_available_equipment(app)
    errors = validate_booking(eq, _tomorrow(), time(10, 0), time(10, 0))
    assert len(errors) > 0


def test_duration_29_minutes(app):
    """T03 – Duration 29 min → Reject"""
    eq = get_available_equipment(app)
    errors = validate_booking(eq, _tomorrow(), time(10, 0), time(10, 29))
    assert len(errors) > 0
    assert any("30" in e for e in errors)


def test_duration_30_minutes(app):
    """T04 – Duration 30 min → Accept"""
    eq = get_available_equipment(app)
    errors = validate_booking(eq, _tomorrow(), time(10, 0), time(10, 30))
    assert errors == []


def test_duration_4_hours(app):
    """T05 – Duration exactly 4 hours → Accept"""
    eq = get_available_equipment(app)
    errors = validate_booking(eq, _tomorrow(), time(9, 0), time(13, 0))
    assert errors == []


def test_duration_4_hours_1_minute(app):
    """T06 – Duration 4 h 1 min → Reject"""
    eq = get_available_equipment(app)
    errors = validate_booking(eq, _tomorrow(), time(9, 0), time(13, 1))
    assert len(errors) > 0
    assert any("4" in e or "exceed" in e.lower() for e in errors)


def test_booking_in_the_past(app):
    """T07 – Booking starts in the past → Reject"""
    eq = get_available_equipment(app)
    yesterday = date.today() - timedelta(days=1)
    errors = validate_booking(eq, yesterday, time(10, 0), time(11, 0))
    assert len(errors) > 0
    assert any("past" in e.lower() for e in errors)


def test_out_of_service_equipment(app):
    """T08 – Equipment Out of service → Reject"""
    eq = get_oos_equipment(app)
    assert eq is not None
    errors = validate_booking(eq, _tomorrow(), time(10, 0), time(11, 0))
    assert len(errors) > 0
    assert any("out of service" in e.lower() for e in errors)


def test_overlap_with_existing_booking(app):
    """T09 – New booking overlaps existing Pending/Approved → Reject"""
    eq = get_available_equipment(app)

    with app.app_context():
        # Create an existing Approved booking 10:00–11:00
        existing = Booking(
            user_id=1,  # seeded student
            equipment_id=eq.id,
            booking_date=_tomorrow(),
            start_time=time(10, 0),
            end_time=time(11, 0),
            status="Approved",
        )
        db.session.add(existing)
        db.session.commit()

    # Overlapping request 10:30–11:30
    errors = validate_booking(eq, _tomorrow(), time(10, 30), time(11, 30))
    assert len(errors) > 0
    assert any("overlap" in e.lower() for e in errors)


def test_starts_exactly_when_previous_ends(app):
    """T10 – New booking starts exactly when previous ends → Accept"""
    eq = get_available_equipment(app)

    with app.app_context():
        existing = Booking(
            user_id=1,
            equipment_id=eq.id,
            booking_date=_tomorrow(),
            start_time=time(10, 0),
            end_time=time(11, 0),
            status="Approved",
        )
        db.session.add(existing)
        db.session.commit()

    # Starts exactly at 11:00
    errors = validate_booking(eq, _tomorrow(), time(11, 0), time(12, 0))
    assert errors == []


# ---------------------------------------------------------------------------
# Integration tests via the booking form route
# ---------------------------------------------------------------------------

def test_valid_booking_request_creates_pending(student_client, app):
    """Valid booking is stored with status Pending (FR-02 + FR-03)."""
    eq = get_available_equipment(app)

    response = student_client.post(
        "/bookings/request",
        data={
            "equipment_id": eq.id,
            "booking_date": _day_after_tomorrow().isoformat(),
            "start_time": "14:00",
            "end_time": "15:00",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200

    with app.app_context():
        booking = Booking.query.filter_by(
            equipment_id=eq.id,
            booking_date=_day_after_tomorrow(),
        ).first()
        assert booking is not None
        assert booking.status == "Pending"
        assert booking.start_time == time(14, 0)
        assert booking.end_time == time(15, 0)


def test_invalid_duration_rejected_by_form(student_client, app):
    """Form rejects duration < 30 minutes."""
    eq = get_available_equipment(app)

    response = student_client.post(
        "/bookings/request",
        data={
            "equipment_id": eq.id,
            "booking_date": _tomorrow().isoformat(),
            "start_time": "10:00",
            "end_time": "10:20",  # only 20 minutes
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"30" in response.data or b"minutes" in response.data.lower()