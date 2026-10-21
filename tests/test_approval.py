"""FR-04 – Booking Approval and Status tests."""

from datetime import date, time, timedelta

from main import Booking, Equipment, db


def _future_date():
    return date.today() + timedelta(days=3)


def test_staff_can_view_pending_bookings(staff_client, app):
    # Create a pending booking first
    with app.app_context():
        eq = Equipment.query.filter_by(status="Available").first()
        booking = Booking(
            user_id=2,  # seeded student
            equipment_id=eq.id,
            booking_date=_future_date(),
            start_time=time(9, 0),
            end_time=time(10, 0),
            status="Pending",
        )
        db.session.add(booking)
        db.session.commit()

    response = staff_client.get("/bookings")
    assert response.status_code == 200
    assert b"Pending" in response.data


def test_staff_can_approve_pending_booking(staff_client, app):
    with app.app_context():
        eq = Equipment.query.filter_by(status="Available").first()
        booking = Booking(
            user_id=2,
            equipment_id=eq.id,
            booking_date=_future_date(),
            start_time=time(11, 0),
            end_time=time(12, 0),
            status="Pending",
        )
        db.session.add(booking)
        db.session.commit()
        booking_id = booking.id

    response = staff_client.post(
        f"/bookings/{booking_id}/approve",
        follow_redirects=True,
    )
    assert response.status_code == 200

    with app.app_context():
        booking = db.session.get(Booking, booking_id)
        assert booking.status == "Approved"


def test_staff_can_reject_with_reason(staff_client, app):
    with app.app_context():
        eq = Equipment.query.filter_by(status="Available").first()
        booking = Booking(
            user_id=2,
            equipment_id=eq.id,
            booking_date=_future_date(),
            start_time=time(13, 0),
            end_time=time(14, 0),
            status="Pending",
        )
        db.session.add(booking)
        db.session.commit()
        booking_id = booking.id

    response = staff_client.post(
        f"/bookings/{booking_id}/reject",
        data={"rejection_reason": "Equipment needed for maintenance"},
        follow_redirects=True,
    )
    assert response.status_code == 200

    with app.app_context():
        booking = db.session.get(Booking, booking_id)
        assert booking.status == "Rejected"
        assert booking.rejection_reason == "Equipment needed for maintenance"


def test_student_can_see_own_booking_status(student_client, app):
    with app.app_context():
        eq = Equipment.query.filter_by(status="Available").first()
        # student is user_id=2 in the seed
        booking = Booking(
            user_id=2,
            equipment_id=eq.id,
            booking_date=_future_date(),
            start_time=time(15, 0),
            end_time=time(16, 0),
            status="Approved",
        )
        db.session.add(booking)
        db.session.commit()

    response = student_client.get("/bookings")
    assert response.status_code == 200
    assert b"Approved" in response.data


def test_student_cannot_approve_booking(student_client, app):
    with app.app_context():
        eq = Equipment.query.filter_by(status="Available").first()
        booking = Booking(
            user_id=2,
            equipment_id=eq.id,
            booking_date=_future_date(),
            start_time=time(16, 0),
            end_time=time(17, 0),
            status="Pending",
        )
        db.session.add(booking)
        db.session.commit()
        booking_id = booking.id

    response = student_client.post(
        f"/bookings/{booking_id}/approve",
        follow_redirects=True,
    )
    assert response.status_code == 200
    # Status should remain Pending
    with app.app_context():
        booking = db.session.get(Booking, booking_id)
        assert booking.status == "Pending"