"""
SQLAlchemy models for the application
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Date, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import enum

class TaskStatus(str, enum.Enum):
    PENDING = "Pending"
    COMPLETED = "Completed"

class StageStatus(str, enum.Enum):
    PENDING = "Pending"
    COMPLETED = "Completed"

class UserRole(str, enum.Enum):
    ADMIN = "Admin"
    CREATOR = "Creator"

class ReminderType(str, enum.Enum):
    EMAIL = "EMAIL"
    WHATSAPP = "WHATSAPP"
    IVR = "IVR"

class User(Base):
    """
    User model for system users
    """
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False, index=True)
    phone = Column(String(20), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.CREATOR)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    tasks = relationship("Task", back_populates="assigned_user")

class Task(Base):
    """
    Task model representing a lesson
    """
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    lesson_id = Column(String(50), nullable=False, unique=True, index=True)
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=False)
    start_date = Column(Date, nullable=False)
    due_date = Column(Date, nullable=False)
    status = Column(Enum(TaskStatus), default=TaskStatus.PENDING)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    assigned_user = relationship("User", back_populates="tasks")
    stages = relationship("TaskStage", back_populates="task", cascade="all, delete-orphan")
    reminder_logs = relationship("ReminderLog", back_populates="task")

class TaskStage(Base):
    """
    Task stage model for workflow tracking
    """
    __tablename__ = "task_stages"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    stage_name = Column(String(100), nullable=False)
    stage_status = Column(Enum(StageStatus), default=StageStatus.PENDING)
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    task = relationship("Task", back_populates="stages")

class ReminderLog(Base):
    """
    Reminder log model for tracking all reminders sent
    """
    __tablename__ = "reminder_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    reminder_type = Column(Enum(ReminderType), nullable=False)
    sent_date = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    task = relationship("Task", back_populates="reminder_logs")