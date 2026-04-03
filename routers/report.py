"""
Report generation router
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List

from database import get_db
from models import Task, TaskStage
from schemas import TaskStageReport

router = APIRouter(prefix="/reports", tags=["reports"])

@router.get("/task-stage", response_model=List[TaskStageReport])
def get_task_stage_report(db: Session = Depends(get_db)):
    """
    Generate report joining task and stage data
    Returns comprehensive report with task and stage information
    """
    # Join Task and TaskStage tables
    results = db.query(
        Task.id.label("task_id"),
        Task.lesson_id,
        Task.status.label("task_status"),
        Task.due_date,
        TaskStage.id.label("stage_id"),
        TaskStage.stage_name,
        TaskStage.stage_status,
        TaskStage.last_updated
    ).join(
        TaskStage, and_(Task.id == TaskStage.task_id)
    ).order_by(
        Task.id, TaskStage.id
    ).all()
    
    # Convert to response model
    report_data = []
    for result in results:
        report_data.append(TaskStageReport(
            task_id=result.task_id,
            lesson_id=result.lesson_id,
            task_status=result.task_status,
            due_date=result.due_date,
            stage_id=result.stage_id,
            stage_name=result.stage_name,
            stage_status=result.stage_status,
            last_updated=result.last_updated
        ))
    
    return report_data

@router.get("/overdue-summary")
def get_overdue_summary(db: Session = Depends(get_db)):
    """
    Get summary of overdue tasks
    """
    from datetime import date
    from services.reminder_service import ReminderService
    
    reminder_service = ReminderService(db)
    overdue_tasks = reminder_service.get_overdue_tasks()
    
    summary = {
        "total_overdue": len(overdue_tasks),
        "tasks": []
    }
    
    for task_info in overdue_tasks:
        task = task_info["task"]
        user = task_info["user"]
        delay_days = task_info["delay_days"]
        
        summary["tasks"].append({
            "task_id": task.id,
            "lesson_id": task.lesson_id,
            "assigned_to": user.name,
            "due_date": task.due_date,
            "delay_days": delay_days,
            "status": task.status
        })
    
    return summary