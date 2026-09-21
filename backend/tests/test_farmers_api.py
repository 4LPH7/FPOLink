"""Tests for Farmer management API endpoints."""


def test_farmer_crud_and_search(client):
    # 1. Register admin to create an FPO first
    admin_res = client.post(
        "/api/auth/register",
        json={
            "name": "Farmer Admin Test",
            "phone": "9222222222",
            "password": "adminpassword",
            "role": "admin",
            "consent_given": True,
        },
    )
    admin_token = admin_res.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    fpo_res = client.post(
        "/api/fpos/",
        json={
            "name": "Erode Turmeric Growers",
            "registration_number": "FPO-TEST-FAR-01",
            "district": "Erode",
            "village": "Kodumudi",
            "state": "Tamil Nadu",
            "contact_phone": "9222222222",
        },
        headers=admin_headers,
    )
    fpo_id = fpo_res.json()["id"]

    # 2. Register new farmer under FPO
    farmer_payload = {
        "name": "Palanisamy G",
        "phone": "9333333333",
        "password": "farmerpassword",
        "village": "Kodumudi",
        "taluk": "Kodumudi",
        "district": "Erode",
        "farm_area_acres": 3.5,
        "language_preference": "ta",
        "consent_given": True,
    }
    create_farmer_res = client.post(
        f"/api/farmers/{fpo_id}",
        json=farmer_payload,
        headers=admin_headers,
    )
    assert create_farmer_res.status_code == 201
    farmer = create_farmer_res.json()
    farmer_id = farmer["id"]
    assert farmer["name"] == "Palanisamy G"
    assert farmer["farm_area_acres"] == 3.5

    # 3. Duplicate phone registration under FPO should fail (409)
    dup_res = client.post(
        f"/api/farmers/{fpo_id}",
        json=farmer_payload,
        headers=admin_headers,
    )
    assert dup_res.status_code == 409

    # 4. List farmers with pagination
    list_res = client.get(f"/api/farmers/{fpo_id}?page=1&page_size=10", headers=admin_headers)
    assert list_res.status_code == 200
    data = list_res.json()
    assert data["total"] >= 1
    assert any(f["id"] == farmer_id for f in data["farmers"])

    # 5. Search farmers
    search_res = client.get(
        f"/api/farmers/{fpo_id}?search=Palanisamy",
        headers=admin_headers,
    )
    assert search_res.status_code == 200
    search_data = search_res.json()
    assert len(search_data["farmers"]) >= 1
    assert search_data["farmers"][0]["name"] == "Palanisamy G"

    # 6. Get farmer details
    detail_res = client.get(f"/api/farmers/detail/{farmer_id}")
    assert detail_res.status_code == 200
    assert detail_res.json()["village"] == "Kodumudi"

    # 7. Update farmer
    update_res = client.put(
        f"/api/farmers/detail/{farmer_id}",
        json={"farm_area_acres": 4.0, "village": "North Kodumudi"},
        headers=admin_headers,
    )
    assert update_res.status_code == 200
    assert update_res.json()["farm_area_acres"] == 4.0
    assert update_res.json()["village"] == "North Kodumudi"

    # 8. WhatsApp invite link (T2.1)
    invite_res = client.get(
        f"/api/farmers/{farmer_id}/whatsapp-invite",
        headers=admin_headers,
    )
    assert invite_res.status_code == 200
    invite_data = invite_res.json()
    assert invite_data["farmer_id"] == farmer_id
    assert "wa.me" in invite_data["invite_url"]
    assert "text=" in invite_data["invite_url"]
