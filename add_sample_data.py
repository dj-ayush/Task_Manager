"""
Script to add sample data for testing
"""
from database import SessionLocal, engine, Base
from models import User, Task, TaskStage, UserRole, TaskStatus
from datetime import date, timedelta
import random

def add_sample_data():
    """
    Add sample users and tasks for testing
    """
    db = SessionLocal()
    
    try:
        # Create sample users
        users = [
            User(
                name="John Doe",
                email="john@example.com",
                phone="1234567890",
                role=UserRole.ADMIN
            ),
            User(
                name="Jane Smith",
                email="jane@example.com",
                phone="0987654321",
                role=UserRole.CREATOR
            ),
            User(
                name="Bob Johnson",
                email="bob@example.com",
                phone="1122334455",
                role=UserRole.CREATOR
            )
        ]
        
        for user in users:
            db.add(user)
        db.commit()
        
        # Create sample tasks with due dates
        tasks = [
            Task(
                lesson_id="LESSON001",
                assigned_to=1,
                start_date=date.today() - timedelta(days=5),
                due_date=date.today() - timedelta(days=2),  # Overdue
                status=TaskStatus.PENDING
            ),
            Task(
                lesson_id="LESSON002",
                assigned_to=2,
                start_date=date.today() - timedelta(days=3),
                due_date=date.today() + timedelta(days=2),
                status=TaskStatus.PENDING
            ),
            Task(
                lesson_id="LESSON003",
                assigned_to=3,
                start_date=date.today() - timedelta(days=10),
                due_date=date.today() - timedelta(days=3),  # Overdue
                status=TaskStatus.PENDING
            )
        ]
        
        for task in tasks:
            db.add(task)
        db.commit()
        
        # Add stages for tasks
        stages = [
            "AI Image Creation",
            "Image Voice-over",
            "Screen Recording",
            "Screen Voice-over",
            "AI Audio Track",
            "Video Editing"
        ]
        
        for task in tasks:
            for stage_name in stages:
                stage = TaskStage(
                    task_id=task.id,
                    stage_name=stage_name,
                    stage_status="Pending"
                )
                db.add(stage)
        db.commit()
        
        print("Sample data added successfully!")
        print(f"Added {len(users)} users")
        print(f"Added {len(tasks)} tasks")
        print(f"Added {len(tasks) * len(stages)} stages")
        
    except Exception as e:
        print(f"Error adding sample data: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    add_sample_data()