from datetime import date, datetime
from typing import Literal, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

TaskStatus = Literal["todo", "in_progress", "done"]
TaskPriority = Literal["low", "medium", "high", "urgent"]
TaskCategory = Literal["general", "harvest", "procurement", "farmer_visit", "buyer", "data"]


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = None
    status: TaskStatus = "todo"
    priority: TaskPriority = "medium"
    category: TaskCategory = "general"
    due_date: Optional[date] = None
    farmer_id: Optional[UUID] = None
    harvest_id: Optional[UUID] = None
    assigned_to_id: Optional[UUID] = None
    fpo_id: Optional[UUID] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    category: Optional[TaskCategory] = None
    due_date: Optional[date] = None
    farmer_id: Optional[UUID] = None
    assigned_to_id: Optional[UUID] = None


class TaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    fpo_id: Optional[UUID] = None
    title: str
    description: Optional[str] = None
    status: str
    priority: str
    category: str
    due_date: Optional[date] = None
    farmer_id: Optional[UUID] = None
    farmer_name: Optional[str] = None
    harvest_id: Optional[UUID] = None
    assigned_to_id: Optional[UUID] = None
    assigned_to_name: Optional[str] = None
    completed_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    is_overdue: bool = False


class TaskSummary(BaseModel):
    todo: int = 0
    in_progress: int = 0
    done: int = 0
    overdue: int = 0
