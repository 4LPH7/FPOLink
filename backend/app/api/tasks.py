"""FPO operations to-do list: CRUD with FPO tenant scoping."""

from datetime import date, datetime, timezone
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload

from app.api.deps import require_role, verify_fpo_access
from app.database import get_db
from app.models.farmer import Farmer
from app.models.task import Task
from app.models.user import User
from app.schemas.task import TaskCreate, TaskResponse, TaskSummary, TaskUpdate

router = APIRouter(prefix="/api/tasks", tags=["tasks"])

STAFF_ROLES = ["admin", "fpo_admin", "fpo_staff", "field_agent", "data_operator"]
GLOBAL_ROLES = ("admin", "state_admin", "data_operator", "analyst")


def _role(user: User) -> str:
    return user.role.value if hasattr(user.role, "value") else str(user.role)


def _scoped(db: Session, user: User):
    q = db.query(Task).options(
        joinedload(Task.farmer).joinedload(Farmer.user), joinedload(Task.assigned_to)
    )
    if _role(user) not in GLOBAL_ROLES:
        if user.fpo_id is None:
            return q.filter(Task.created_by_id == user.id)
        q = q.filter(Task.fpo_id == user.fpo_id)
    return q


def _to_response(t: Task) -> TaskResponse:
    r = TaskResponse.model_validate(t)
    r.farmer_name = t.farmer.user.name if t.farmer and t.farmer.user else None
    r.assigned_to_name = t.assigned_to.name if t.assigned_to else None
    r.is_overdue = bool(t.due_date and t.status != "done" and t.due_date < date.today())
    return r


def _get(db: Session, task_id: UUID, user: User) -> Task:
    task = _scoped(db, user).filter(Task.id == task_id).first()
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


@router.get("", response_model=List[TaskResponse])
def list_tasks(
    status_filter: Optional[str] = Query(default=None, alias="status"),
    db: Session = Depends(get_db),
    user: User = Depends(require_role(STAFF_ROLES)),
):
    q = _scoped(db, user)
    if status_filter:
        q = q.filter(Task.status == status_filter)
    tasks = q.order_by(
        Task.status, Task.due_date.is_(None), Task.due_date, Task.created_at.desc()
    ).all()
    return [_to_response(t) for t in tasks]


@router.get("/summary", response_model=TaskSummary)
def task_summary(db: Session = Depends(get_db), user: User = Depends(require_role(STAFF_ROLES))):
    summary = TaskSummary()
    for t in _scoped(db, user).all():
        setattr(summary, t.status, getattr(summary, t.status, 0) + 1)
        if t.due_date and t.status != "done" and t.due_date < date.today():
            summary.overdue += 1
    return summary


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    payload: TaskCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_role(STAFF_ROLES)),
):
    fpo_id = payload.fpo_id or user.fpo_id
    if payload.farmer_id:
        farmer = db.query(Farmer).filter(Farmer.id == payload.farmer_id).first()
        if farmer is None:
            raise HTTPException(status_code=404, detail="Farmer not found")
        fpo_id = fpo_id or farmer.fpo_id
        if not verify_fpo_access(farmer.fpo_id, user):
            raise HTTPException(status_code=403, detail="Farmer belongs to another FPO")
    if fpo_id and not verify_fpo_access(fpo_id, user):
        raise HTTPException(status_code=403, detail="Not authorized for this FPO")

    data = payload.model_dump(exclude={"fpo_id"})
    task = Task(**data, fpo_id=fpo_id, created_by_id=user.id)
    if task.status == "done":
        task.completed_at = datetime.now(timezone.utc)
    db.add(task)
    db.commit()
    return _to_response(_get(db, task.id, user))


@router.patch("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: UUID,
    payload: TaskUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_role(STAFF_ROLES)),
):
    task = _get(db, task_id, user)
    changes = payload.model_dump(exclude_unset=True)
    if "farmer_id" in changes and changes["farmer_id"] is not None:
        farmer = db.query(Farmer).filter(Farmer.id == changes["farmer_id"]).first()
        if farmer is None:
            raise HTTPException(status_code=404, detail="Farmer not found")
        if task.fpo_id and farmer.fpo_id != task.fpo_id:
            raise HTTPException(status_code=403, detail="Farmer belongs to another FPO")
        if not verify_fpo_access(farmer.fpo_id, user):
            raise HTTPException(status_code=403, detail="Farmer belongs to another FPO")
    for key, value in changes.items():
        setattr(task, key, value)
    if "status" in changes:
        task.completed_at = datetime.now(timezone.utc) if task.status == "done" else None
    db.commit()
    return _to_response(_get(db, task.id, user))


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: UUID,
    db: Session = Depends(get_db),
    user: User = Depends(require_role(STAFF_ROLES)),
):
    task = _get(db, task_id, user)
    db.delete(task)
    db.commit()
