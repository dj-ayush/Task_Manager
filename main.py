"""
Main FastAPI application entry point
"""
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from contextlib import asynccontextmanager
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import logging
from pydantic import BaseModel

from database import engine, Base
from routers import task, stage, report
from services.reminder_service import ReminderService
from database import SessionLocal
from models import ReminderLog, User  # Added User import

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize scheduler
scheduler = BackgroundScheduler()

# Login request model
class LoginRequest(BaseModel):
    email: str
    password: str

def run_reminder_check():
    """
    Function to run reminder check
    """
    logger.info("Running scheduled reminder check")
    db = SessionLocal()
    try:
        reminder_service = ReminderService(db)
        reminder_service.check_and_send_reminders()
    except Exception as e:
        logger.error(f"Error in reminder check: {str(e)}")
    finally:
        db.close()

# Startup and shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting application...")
    
    # Schedule reminder check to run daily at 9:00 AM
    scheduler.add_job(
        run_reminder_check,
        trigger=CronTrigger(hour=9, minute=0),
        id="reminder_check",
        replace_existing=True
    )
    scheduler.start()
    logger.info("Scheduler started")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")
    scheduler.shutdown()

# Create FastAPI app
app = FastAPI(
    title="AI Video Tutorial Task Management System",
    description="Task management system for AI video tutorial creation with reminder escalation",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for frontend
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include routers
app.include_router(task.router)
app.include_router(stage.router)
app.include_router(report.router)

# Redirect root to login page (changed from index.html to login.html)
@app.get("/")
async def root():
    """
    Redirect to login page
    """
    return RedirectResponse(url="/static/login.html")

# Login endpoint
@app.post("/login")
def login(login_data: LoginRequest, db: SessionLocal = Depends(lambda: SessionLocal())):
    """
    Simple login endpoint - validates user from database
    """
    try:
        # Find user by email
        user = db.query(User).filter(User.email == login_data.email).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Simple password validation (for demo - accept any password if user exists)
        if login_data.password in ["admin123", "password123", "demo"] or len(login_data.password) > 0:
            # Return user info (excluding sensitive data)
            return {
                "message": "Login successful",
                "user": {
                    "id": user.id,
                    "name": user.name,
                    "email": user.email,
                    "role": user.role.value if hasattr(user.role, 'value') else str(user.role)
                }
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login error: {str(e)}"
        )
    finally:
        db.close()

# API information endpoint (for developers)
@app.get("/api")
def api_info():
    """
    API information endpoint
    """
    return {
        "message": "AI Video Tutorial Task Management System",
        "version": "1.0.0",
        "docs": "/docs",
        "frontend": "/static/index.html",
        "login": "/static/login.html",
        "endpoints": {
            "tasks": {
                "list": "GET /tasks",
                "create": "POST /tasks",
                "update": "PUT /tasks/{id}",
                "delete": "DELETE /tasks/{id}"
            },
            "stages": {
                "list": "GET /stages/task/{task_id}",
                "update": "PUT /stages/{id}"
            },
            "reports": {
                "task_stage": "GET /reports/task-stage",
                "overdue_summary": "GET /reports/overdue-summary"
            },
            "reminders": {
                "trigger": "POST /admin/trigger-reminders",
                "logs": "GET /reminder-logs"
            },
            "auth": {
                "login": "POST /login"
            }
        }
    }

@app.get("/health")
def health_check():
    """
    Health check endpoint
    """
    return {"status": "healthy"}

# Optional: Manual trigger for reminder check (for testing)
@app.post("/admin/trigger-reminders")
def trigger_reminders_manually():
    """
    Manually trigger reminder check (admin endpoint for testing)
    """
    db = SessionLocal()
    try:
        reminder_service = ReminderService(db)
        reminder_service.check_and_send_reminders()
        return {"message": "Reminder check triggered successfully"}
    except Exception as e:
        return {"error": str(e)}
    finally:
        db.close()

# Endpoint to get reminder logs for frontend
@app.get("/reminder-logs")
def get_reminder_logs(db: SessionLocal = Depends(lambda: SessionLocal())):
    """
    Get all reminder logs for frontend display
    """
    try:
        logs = db.query(ReminderLog).order_by(ReminderLog.sent_date.desc()).all()
        return logs
    finally:
        db.close()