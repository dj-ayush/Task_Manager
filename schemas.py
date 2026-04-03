"""
Pydantic schemas for request/response validation
"""
from pydantic import BaseModel, EmailStr, Field
from datetime import date, datetime
from typing import Optional, List
from enum import Enum

# Enums for validation
class TaskStatus(str, Enum):
    PENDING = "Pending"
    COMPLETED = "Completed"

class StageStatus(str, Enum):
    PENDING = "Pending"
    COMPLETED = "Completed"

class UserRole(str, Enum):
    ADMIN = "Admin"
    CREATOR = "Creator"

class ReminderType(str, Enum):
    EMAIL = "EMAIL"
    WHATSAPP = "WHATSAPP"
    IVR = "IVR"

# User schemas
class UserBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    phone: str = Field(..., min_length=10, max_length=15)
    role: UserRole = UserRole.CREATOR

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)

class UserResponse(UserBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Task Stage schemas
class TaskStageBase(BaseModel):
    stage_name: str
    stage_status: StageStatus = StageStatus.PENDING

class TaskStageResponse(TaskStageBase):
    id: int
    task_id: int
    last_updated: datetime
    
    class Config:
        from_attributes = True

class TaskStageUpdate(BaseModel):
    stage_status: StageStatus

# Task schemas
class TaskBase(BaseModel):
    lesson_id: str = Field(..., min_length=1, max_length=50)
    assigned_to: int
    start_date: date
    due_date: date

class TaskCreate(TaskBase):
    pass

class TaskResponse(TaskBase):
    id: int
    status: TaskStatus
    created_at: datetime
    updated_at: Optional[datetime] = None
    assigned_user: Optional[UserResponse] = None
    stages: Optional[List[TaskStageResponse]] = None
    
    class Config:
        from_attributes = True

class TaskUpdate(BaseModel):
    lesson_id: Optional[str] = Field(None, min_length=1, max_length=50)
    assigned_to: Optional[int] = None
    start_date: Optional[date] = None
    due_date: Optional[date] = None
    status: Optional[TaskStatus] = None

# Report schema
class TaskStageReport(BaseModel):
    task_id: int
    lesson_id: str
    task_status: TaskStatus
    due_date: date
    stage_id: int
    stage_name: str
    stage_status: StageStatus
    last_updated: datetime
    
    class Config:
        from_attributes = True

# Reminder Log schema
class ReminderLogResponse(BaseModel):
    id: int
    task_id: int
    reminder_type: ReminderType
    sent_date: datetime
    
    class Config:
        from_attributes = True