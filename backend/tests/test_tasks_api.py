"""FPO to-do list API: CRUD, status lifecycle, and tenant scoping."""

from datetime import date, timedelta

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.database  # noqa: F401  (registers SQLite JSONB/UUID compilers)
from app.api.deps import get_current_user
from app.api.tasks import router
from app.database import get_db
from app.models.base import Base
from app.models.fpo import FPO
from app.models.user import User, UserRole


@pytest.fixture
def ctx():
    engine = create_engine(
        "sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(bind=engine)
    db = sessionmaker(bind=engine)()
    fpos = []
    for i in (1, 2):
        f = FPO(
            name=f"FPO {i}",
            registration_number=f"R{i}",
            district="Erode",
            village="V",
            contact_phone="9",
        )
        db.add(f)
        fpos.append(f)
    db.flush()
    staff1 = User(
        name="S1",
        phone="9000000001",
        role=UserRole.FPO_STAFF,
        hashed_password="x",
        fpo_id=fpos[0].id,
    )
    staff2 = User(
        name="S2",
        phone="9000000002",
        role=UserRole.FPO_STAFF,
        hashed_password="x",
        fpo_id=fpos[1].id,
    )
    farmer = User(name="F", phone="9000000003", role=UserRole.FARMER, hashed_password="x")
    db.add_all([staff1, staff2, farmer])
    db.commit()
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_db] = lambda: db
    yield app, db, staff1, staff2, farmer
    db.close()
    Base.metadata.drop_all(bind=engine)


def test_task_crud_and_scoping(ctx):
    app, db, staff1, staff2, farmer = ctx
    client = TestClient(app)
    app.dependency_overrides[get_current_user] = lambda: staff1

    yesterday = (date.today() - timedelta(days=1)).isoformat()
    r = client.post(
        "/api/tasks",
        json={"title": "Visit Perundurai farmers", "priority": "high", "due_date": yesterday},
    )
    assert r.status_code == 201, r.text
    task = r.json()
    assert task["status"] == "todo" and task["is_overdue"] is True
    assert task["fpo_id"] == str(staff1.fpo_id)

    r = client.patch(f"/api/tasks/{task['id']}", json={"status": "done"})
    assert r.json()["completed_at"] is not None and r.json()["is_overdue"] is False
    assert client.get("/api/tasks/summary").json()["done"] == 1
    assert len(client.get("/api/tasks?status=done").json()) == 1

    # Another FPO's staff cannot see or edit it.
    app.dependency_overrides[get_current_user] = lambda: staff2
    assert client.get("/api/tasks").json() == []
    assert client.patch(f"/api/tasks/{task['id']}", json={"status": "todo"}).status_code == 404

    # Farmers have no access to the staff to-do list.
    app.dependency_overrides[get_current_user] = lambda: farmer
    assert client.get("/api/tasks").status_code == 403

    app.dependency_overrides[get_current_user] = lambda: staff1
    assert client.delete(f"/api/tasks/{task['id']}").status_code == 204
    assert client.get("/api/tasks").json() == []


def test_task_validation(ctx):
    app, db, staff1, *_ = ctx
    app.dependency_overrides[get_current_user] = lambda: staff1
    client = TestClient(app)
    assert client.post("/api/tasks", json={"title": ""}).status_code == 422
    assert client.post("/api/tasks", json={"title": "x", "status": "bogus"}).status_code == 422
