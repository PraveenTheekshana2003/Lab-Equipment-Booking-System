"""FR-01 – Equipment Catalogue tests."""

from main import Equipment, db


def test_equipment_list_accessible(student_client):
    response = student_client.get("/equipment")
    assert response.status_code == 200
    assert b"Test Pi" in response.data or b"equipment" in response.data.lower()


def test_staff_can_add_equipment(staff_client, app):
    response = staff_client.post(
        "/equipment/add",
        data={
            "name": "New Oscilloscope",
            "category": "Test equipment",
            "description": "A brand new digital oscilloscope",
            "status": "Available",
            "image": "",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200

    with app.app_context():
        eq = Equipment.query.filter_by(name="New Oscilloscope").first()
        assert eq is not None
        assert eq.category == "Test equipment"
        assert eq.status == "Available"


def test_staff_can_edit_equipment(staff_client, app):
    with app.app_context():
        eq = Equipment.query.filter_by(name="Test Pi").first()
        assert eq is not None
        eq_id = eq.id

    response = staff_client.post(
        f"/equipment/{eq_id}/edit",
        data={
            "name": "Updated Pi Kit",
            "category": "SBC",
            "description": "Updated description",
            "status": "Available",
            "image": "raspberry-pi.jpg",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200

    with app.app_context():
        eq = db.session.get(Equipment, eq_id)
        assert eq.name == "Updated Pi Kit"
        assert eq.description == "Updated description"


def test_staff_can_delete_equipment(staff_client, app):
    with app.app_context():
        # Create a temporary item to delete
        temp = Equipment(
            name="Temp Delete Item",
            category="Temp",
            description="Will be deleted",
            status="Available",
        )
        db.session.add(temp)
        db.session.commit()
        eq_id = temp.id

    response = staff_client.post(
        f"/equipment/{eq_id}/delete",
        follow_redirects=True,
    )
    assert response.status_code == 200

    with app.app_context():
        eq = db.session.get(Equipment, eq_id)
        assert eq is None


def test_filter_by_category(student_client, app):
    response = student_client.get("/equipment?category=SBC")
    assert response.status_code == 200
    # Should contain the seeded "Test Pi" which is in category SBC
    assert b"Test Pi" in response.data or b"SBC" in response.data


def test_student_cannot_add_equipment(student_client):
    response = student_client.get("/equipment/add", follow_redirects=True)
    assert response.status_code == 200
    # Should not show the add form for students
    assert b"Staff" in response.data or b"required" in response.data.lower() or b"Dashboard" in response.data