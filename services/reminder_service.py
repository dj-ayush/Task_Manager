"""
Reminder service for checking overdue tasks and sending reminders
"""
from sqlalchemy.orm import Session
from datetime import date, datetime, timedelta
from typing import List, Dict
import logging
from models import Task, TaskStatus, ReminderLog, ReminderType, User
from services.email_service import EmailService
from sqlalchemy import and_

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ReminderService:
    """
    Service class for handling task reminders with escalation logic
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.email_service = EmailService()
    
    def get_overdue_tasks(self) -> List[Dict]:
        """
        Get all pending tasks that are past due date
        
        Returns:
            List of overdue tasks with user information
        """
        current_date = date.today()
        
        overdue_tasks = self.db.query(Task).join(User).filter(
            and_(
                Task.status == TaskStatus.PENDING,
                Task.due_date < current_date
            )
        ).all()
        
        results = []
        for task in overdue_tasks:
            # Calculate delay in days
            delay_days = (current_date - task.due_date).days
            
            results.append({
                "task": task,
                "user": task.assigned_user,
                "delay_days": delay_days
            })
            
        return results
    
    def check_and_send_reminders(self):
        """
        Main method to check overdue tasks and send appropriate reminders
        This implements the escalation logic:
        - Email: delay > 0 days (immediately after due date)
        - WhatsApp: delay > 2 days
        - IVR: delay > 5 days
        """
        logger.info("Running reminder check...")
        overdue_tasks = self.get_overdue_tasks()
        
        for overdue_info in overdue_tasks:
            task = overdue_info["task"]
            user = overdue_info["user"]
            delay_days = overdue_info["delay_days"]
            
            # Check if reminder already sent today for this task
            today = datetime.now().date()
            
            # Email reminder logic (delay > 0 days)
            if delay_days > 0:
                email_sent = self._check_reminder_sent_today(task.id, ReminderType.EMAIL)
                if not email_sent:
                    self._send_email_reminder(task, user)
            
            # WhatsApp reminder logic (delay > 2 days)
            if delay_days > 2:
                whatsapp_sent = self._check_reminder_sent_today(task.id, ReminderType.WHATSAPP)
                if not whatsapp_sent:
                    self._log_reminder(task.id, ReminderType.WHATSAPP)
                    logger.info(f"WhatsApp reminder logged for task {task.id}")
            
            # IVR reminder logic (delay > 5 days)
            if delay_days > 5:
                ivr_sent = self._check_reminder_sent_today(task.id, ReminderType.IVR)
                if not ivr_sent:
                    self._log_reminder(task.id, ReminderType.IVR)
                    logger.info(f"IVR reminder logged for task {task.id}")
        
        logger.info(f"Reminder check completed. Processed {len(overdue_tasks)} overdue tasks.")
    
    def _check_reminder_sent_today(self, task_id: int, reminder_type: ReminderType) -> bool:
        """
        Check if a reminder of specific type was sent today for a task
        
        Args:
            task_id: Task ID
            reminder_type: Type of reminder
            
        Returns:
            bool: True if reminder was sent today
        """
        today = datetime.now().date()
        
        reminder = self.db.query(ReminderLog).filter(
            and_(
                ReminderLog.task_id == task_id,
                ReminderLog.reminder_type == reminder_type,
                ReminderLog.sent_date >= today
            )
        ).first()
        
        return reminder is not None
    
    def _send_email_reminder(self, task: Task, user: User):
        """
        Send email reminder and log it
        
        Args:
            task: Task object
            user: User object
        """
        success = self.email_service.send_task_reminder(
            to_email=user.email,
            task_id=task.id,
            lesson_id=task.lesson_id,
            due_date=task.due_date
        )
        
        if success:
            self._log_reminder(task.id, ReminderType.EMAIL)
            logger.info(f"Email reminder sent for task {task.id} to {user.email}")
        else:
            logger.error(f"Failed to send email reminder for task {task.id}")
    
    def _log_reminder(self, task_id: int, reminder_type: ReminderType):
        """
        Log reminder in the database
        
        Args:
            task_id: Task ID
            reminder_type: Type of reminder
        """
        reminder_log = ReminderLog(
            task_id=task_id,
            reminder_type=reminder_type,
            sent_date=datetime.now()
        )
        
        self.db.add(reminder_log)
        self.db.commit()