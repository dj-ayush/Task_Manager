"""
Stage management router
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models import TaskStage, Task, TaskStatus, StageStatus
from schemas import TaskStageResponse, TaskStageUpdate

router = APIRouter(prefix="/stages", tags=["stages"])

@router.get("/task/{task_id}", response_model=List[TaskStageResponse])
def get_task_stages(task_id: int, db: Session = Depends(get_db)):
    """
    Get all stages for a specific task
    """
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found"
        )
    
    stages = db.query(TaskStage).filter(TaskStage.task_id == task_id).all()
    return stages

@router.put("/{stage_id}", response_model=TaskStageResponse)
def update_stage_status(
    stage_id: int, 
    stage_update: TaskStageUpdate, 
    db: Session = Depends(get_db)
):
    """
    Update stage status
    """
    stage = db.query(TaskStage).filter(TaskStage.id == stage_id).first()
    if not stage:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Stage with id {stage_id} not found"
        )
    
    # Update stage status
    stage.stage_status = stage_update.stage_status
    
    # Check if all stages are completed to update task status
    all_stages = db.query(TaskStage).filter(TaskStage.task_id == stage.task_id).all()
    all_completed = all(s.stage_status == StageStatus.COMPLETED for s in all_stages)
    
    if all_completed:
        task = db.query(Task).filter(Task.id == stage.task_id).first()
        if task and task.status != TaskStatus.COMPLETED:
            task.status = TaskStatus.COMPLETED
            db.add(task)
    
    db.commit()
    db.refresh(stage)
    
    return stage

@router.get("/{stage_id}", response_model=TaskStageResponse)
def get_stage(stage_id: int, db: Session = Depends(get_db)):
    """
    Get stage details by ID
    """
    stage = db.query(TaskStage).filter(TaskStage.id == stage_id).first()
    if not stage:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Stage with id {stage_id} not found"
        )
    return stage