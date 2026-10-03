"""Tests for FPO CRUD and Dashboard endpoints."""


def test_fpo_lifecycle_and_dashboard(client, db):
    from app.models.user import User, UserRole
    from app.services.jwt import create_access_token

    admin = User(
        name="FPO Admin Test",
        phone="9111111111",
        hashed_password="test-hash",
        role=UserRole.ADMIN,
    )
    db.add(admin)
    db.commit()
    admin_token = create_access_token(admin.id, "admin")
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # 2. Create FPO (admin only)
    fpo_payload = {
        "name": "Erode Organic Spices FPO",
        "registration_number": "FPO-TEST-ERD-99",
        "district": "Erode",
        "village": "Perundurai",
        "state": "Tamil Nadu",
        "contact_phone": "9111111111",
        "contact_email": "erode.fpo@example.com",
    }
    create_res = client.post("/api/fpos/", json=fpo_payload, headers=admin_headers)
    assert create_res.status_code == 201
    fpo = create_res.json()
    fpo_id = fpo["id"]
    assert fpo["name"] == "Erode Organic Spices FPO"

    # 3. Unauthorized creation without token
    anon_res = client.post("/api/fpos/", json=fpo_payload)
    assert anon_res.status_code == 401

    # 4. List FPOs
    assert client.get("/api/fpos/").status_code == 401
    list_res = client.get("/api/fpos/", headers=admin_headers)
    assert list_res.status_code == 200
    fpos = list_res.json()["fpos"]
    assert any(f["id"] == fpo_id for f in fpos)

    # 5. Get FPO by ID
    assert client.get(f"/api/fpos/{fpo_id}").status_code == 401
    get_res = client.get(f"/api/fpos/{fpo_id}", headers=admin_headers)
    assert get_res.status_code == 200
    assert get_res.json()["name"] == "Erode Organic Spices FPO"

    # 6. Update FPO
    update_res = client.put(
        f"/api/fpos/{fpo_id}",
        json={"village": "Updated Perundurai Town"},
        headers=admin_headers,
    )
    assert update_res.status_code == 200
    assert update_res.json()["village"] == "Updated Perundurai Town"

    # 7. Get FPO Dashboard stats
    dash_res = client.get(f"/api/fpos/{fpo_id}/dashboard", headers=admin_headers)
    assert dash_res.status_code == 200
    stats = dash_res.json()
    assert "member_count" in stats
    assert "total_farm_area_acres" in stats
    assert "crop_distribution" in stats
