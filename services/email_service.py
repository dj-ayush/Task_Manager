"""
Email service for sending reminders via SMTP
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
import os
from dotenv import load_dotenv
import logging

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmailService:
    """
    Service class for handling email operations
    """
    
    def __init__(self):
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.sender_email = os.getenv("SENDER_EMAIL")
        self.sender_password = os.getenv("SENDER_PASSWORD")
        
    def send_email(self, to_email: str, subject: str, body: str) -> bool:
        """
        Send an email using SMTP
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Email body content
            
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        if not self.sender_email or not self.sender_password:
            logger.error("Email credentials not configured")
            return False
            
        try:
            # Create message
            message = MIMEMultipart()
            message["From"] = self.sender_email
            message["To"] = to_email
            message["Subject"] = subject
            
            # Attach body
            message.attach(MIMEText(body, "plain"))
            
            # Connect to SMTP server and send
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(message)
                
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            return False
    
    def send_task_reminder(self, to_email: str, task_id: int, lesson_id: str, due_date) -> bool:
        """
        Send a task reminder email
        
        Args:
            to_email: Recipient email
            task_id: Task ID
            lesson_id: Lesson ID
            due_date: Due date of the task
            
        Returns:
            bool: True if email sent successfully
        """
        subject = f"Task Reminder: Lesson {lesson_id} is Overdue"
        body = f"""
        Dear User,
        
        This is a reminder that task for lesson '{lesson_id}' (Task ID: {task_id}) 
        is overdue. The due date was {due_date}.
        
        Please complete the task as soon as possible.
        
        Best regards,
        Task Management System
        """
        
        return self.send_email(to_email, subject, body)