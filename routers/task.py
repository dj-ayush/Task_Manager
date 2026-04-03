"""
Task CRUD operations router
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import date

from database import get_db
from models import Task, TaskStage, TaskStatus, User
from schemas import TaskCreate, TaskResponse, TaskUpdate
from services.reminder_service import ReminderService

router = APIRouter(prefix="/tasks", tags=["tasks"])

# Predefined stages for each task
STAGES = [
    "AI Image Creation",
    "Image Voice-over",
    "Screen Recording",
    "Screen Voice-over",
    "AI Audio Track",
    "Video Editing"
]

def create_task_stages(db: Session, task_id: int):
    """
    Helper function to create all stages for a new task
    """
    for stage_name in STAGES:
        stage = TaskStage(
            task_id=task_id,
            stage_name=stage_name,
            stage_status="Pending"
        )
        db.add(stage)
    db.commit()

@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    """
    Create a new task with all required stages
    """
    # Check if user exists
    user = db.query(User).filter(User.id == task.assigned_to).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {task.assigned_to} not found"
        )
    
    # Check if lesson_id is unique
    existing_task = db.query(Task).filter(Task.lesson_id == task.lesson_id).first()
    if existing_task:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Task with lesson_id {task.lesson_id} already exists"
        )
    
    # Validate dates
    if task.start_date > task.due_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Start date cannot be after due date"
        )
    
    # Create task
    db_task = Task(**task.model_dump())
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    
    # Create stages
    create_task_stages(db, db_task.id)
    
    # Refresh to get stages
    db.refresh(db_task)
    
    return db_task

@router.get("/", response_model=List[TaskResponse])
def list_tasks(
    skip: int = 0, 
    limit: int = 100,
    status_filter: TaskStatus = None,
    db: Session = Depends(get_db)
):
    """
    List all tasks with optional status filter
    """
    query = db.query(Task)
    
    if status_filter:
        query = query.filter(Task.status == status_filter)
    
    tasks = query.offset(skip).limit(limit).all()
    return tasks

@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, db: Session = Depends(get_db)):
    """
    Get task details by ID
    """
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found"
        )
    return task

@router.put("/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, task_update: TaskUpdate, db: Session = Depends(get_db)):
    """
    Update task details
    """
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found"
        )
    
    # Update fields
    update_data = task_update.model_dump(exclude_unset=True)
    
    # Validate dates if both are provided
    if "start_date" in update_data and "due_date" in update_data:
        if update_data["start_date"] > update_data["due_date"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Start date cannot be after due date"
            )
    elif "start_date" in update_data:
        if update_data["start_date"] > task.due_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Start date cannot be after due date"
            )
    elif "due_date" in update_data:
        if task.start_date > update_data["due_date"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Start date cannot be after due date"
            )
    
    for field, value in update_data.items():
        setattr(task, field, value)
    
    db.commit()
    db.refresh(task)
    
    return task

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    """
    Delete a task and all associated stages
    """
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found"
        )
    
    db.delete(task)
    db.commit()
    
    return None