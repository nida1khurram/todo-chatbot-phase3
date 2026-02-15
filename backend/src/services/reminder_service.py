"""
Reminder Service for Todo Application
This module handles task reminders, scheduling, and notifications
"""

import logging
from datetime import datetime, timedelta
from sqlmodel import Session, select
from typing import List
from ..models.task import Task
from ..models.user import User
from ..services.notification_service import NotificationService
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from ..database import engine
import asyncio

logger = logging.getLogger(__name__)

class ReminderService:
    def __init__(self):
        self.notification_service = NotificationService()
        self.scheduler = AsyncIOScheduler()
        
    def start_scheduler(self):
        """Start the reminder scheduler"""
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("Reminder scheduler started")
    
    def stop_scheduler(self):
        """Stop the reminder scheduler"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Reminder scheduler stopped")
    
    def schedule_reminders_for_task(self, task: Task):
        """Schedule reminders for a specific task based on due date"""
        if not task.due_date:
            logger.info(f"No due date for task {task.id}, skipping reminder scheduling")
            return
        
        # Schedule a reminder 24 hours before due date if it's more than 1 hour away
        time_diff = task.due_date - datetime.utcnow()
        if time_diff.total_seconds() > 3600:  # More than 1 hour until due
            reminder_time = task.due_date - timedelta(hours=24)
            if reminder_time > datetime.utcnow():  # Only schedule if reminder time is in the future
                job_id = f"reminder_task_{task.id}_24h"
                self.scheduler.add_job(
                    self._send_reminder,
                    'date',
                    run_date=reminder_time,
                    id=job_id,
                    args=[task.id, task.user_id, "24_hours"]
                )
                logger.info(f"Scheduled 24-hour reminder for task {task.id} at {reminder_time}")
        
        # Schedule a reminder 1 hour before due date
        if time_diff.total_seconds() > 60:  # More than 1 minute until due
            reminder_time = task.due_date - timedelta(hours=1)
            if reminder_time > datetime.utcnow():  # Only schedule if reminder time is in the future
                job_id = f"reminder_task_{task.id}_1h"
                self.scheduler.add_job(
                    self._send_reminder,
                    'date',
                    run_date=reminder_time,
                    id=job_id,
                    args=[task.id, task.user_id, "1_hour"]
                )
                logger.info(f"Scheduled 1-hour reminder for task {task.id} at {reminder_time}")
    
    def schedule_recurring_task(self, task: Task):
        """Schedule recurring tasks based on recurrence rule"""
        if not task.recurrence_rule or not task.recurrence_end_date:
            logger.info(f"Task {task.id} is not recurring, skipping recurrence scheduling")
            return
            
        # Cancel any existing recurrence jobs for this task
        self.cancel_recurring_task(task.id)
        
        # Schedule the recurring task creation
        job_id = f"recurring_task_{task.id}"
        
        # Map recurrence rules to cron triggers
        if task.recurrence_rule == "daily":
            trigger = CronTrigger(hour=9, minute=0)  # Daily at 9 AM
        elif task.recurrence_rule == "weekly":
            trigger = CronTrigger(day_of_week=0, hour=9, minute=0)  # Weekly on Sunday at 9 AM
        elif task.recurrence_rule == "monthly":
            trigger = CronTrigger(day=1, hour=9, minute=0)  # Monthly on 1st at 9 AM
        elif task.recurrence_rule == "yearly":
            trigger = CronTrigger(month=1, day=1, hour=9, minute=0)  # Yearly on Jan 1 at 9 AM
        else:
            logger.warning(f"Unknown recurrence rule for task {task.id}: {task.recurrence_rule}")
            return
        
        # Only schedule if the end date is in the future
        if task.recurrence_end_date > datetime.utcnow():
            self.scheduler.add_job(
                self._create_next_occurrence,
                trigger,
                id=job_id,
                args=[task.id, task.user_id],
                end_date=task.recurrence_end_date
            )
            logger.info(f"Scheduled recurring task {task.id} with rule {task.recurrence_rule}")
    
    def cancel_reminders_for_task(self, task_id: int):
        """Cancel all scheduled reminders for a specific task"""
        jobs_to_remove = []
        for job in self.scheduler.get_jobs():
            if job.id.startswith(f"reminder_task_{task_id}_"):
                jobs_to_remove.append(job.id)
        
        for job_id in jobs_to_remove:
            self.scheduler.remove_job(job_id)
            logger.info(f"Cancelled reminder job {job_id}")
    
    def cancel_recurring_task(self, task_id: int):
        """Cancel recurring task scheduling for a specific task"""
        job_id = f"recurring_task_{task_id}"
        if self.scheduler.get_job(job_id):
            self.scheduler.remove_job(job_id)
            logger.info(f"Cancelled recurring task job {job_id}")
    
    async def _send_reminder(self, task_id: int, user_id: int, reminder_type: str):
        """Internal method to send a reminder for a task"""
        try:
            # Create a new session for this async job to avoid session lifecycle issues
            with Session(engine) as session:
                # Get the task and user
                task = session.get(Task, task_id)
                user = session.get(User, user_id)
                
                if not task or not user:
                    logger.error(f"Could not find task {task_id} or user {user_id} for reminder")
                    return
                
                # Prepare reminder message
                if reminder_type == "24_hours":
                    message = f"Reminder: Your task '{task.title}' is due tomorrow!"
                elif reminder_type == "1_hour":
                    message = f"Reminder: Your task '{task.title}' is due in 1 hour!"
                else:
                    message = f"Reminder: Your task '{task.title}' is due soon!"
                
                # Send notification
                await self.notification_service.send_notification(user.email, message, task_id)
                logger.info(f"Sent {reminder_type} reminder for task {task_id} to user {user_id}")
                
        except Exception as e:
            logger.error(f"Error sending reminder for task {task_id}: {str(e)}")
    
    async def _create_next_occurrence(self, task_id: int, user_id: int):
        """Internal method to create the next occurrence of a recurring task"""
        try:
            # Create a new session for this async job to avoid session lifecycle issues
            with Session(engine) as session:
                # Get the original task
                original_task = session.get(Task, task_id)
                
                if not original_task:
                    logger.error(f"Could not find original task {task_id} for recurrence")
                    return
                
                # Check if we've reached the end date
                if original_task.recurrence_end_date and datetime.utcnow() > original_task.recurrence_end_date:
                    logger.info(f"Recurring task {task_id} has reached end date, stopping recurrence")
                    self.cancel_recurring_task(task_id)
                    return
                
                # Create a new task based on the original
                next_task = Task(
                    title=original_task.title,
                    description=original_task.description,
                    user_id=user_id,
                    priority=original_task.priority,
                    tags=original_task.tags,
                    recurrence_rule=original_task.recurrence_rule,
                    recurrence_end_date=original_task.recurrence_end_date
                )
                
                # Set the due date for the next occurrence based on recurrence rule
                if original_task.recurrence_rule == "daily":
                    next_task.due_date = datetime.utcnow() + timedelta(days=1)
                elif original_task.recurrence_rule == "weekly":
                    next_task.due_date = datetime.utcnow() + timedelta(weeks=1)
                elif original_task.recurrence_rule == "monthly":
                    # Simple monthly calculation (same day next month)
                    import calendar
                    now = datetime.utcnow()
                    next_month = now.month + 1
                    next_year = now.year
                    if next_month > 12:
                        next_month = 1
                        next_year += 1
                    # Ensure the day exists in the next month (handles months with fewer days)
                    max_day = calendar.monthrange(next_year, next_month)[1]
                    next_day = min(now.day, max_day)
                    next_task.due_date = now.replace(year=next_year, month=next_month, day=next_day)
                elif original_task.recurrence_rule == "yearly":
                    next_task.due_date = original_task.due_date.replace(year=original_task.due_date.year + 1)
                
                # Add the new task to the database
                session.add(next_task)
                session.commit()
                session.refresh(next_task)
                
                logger.info(f"Created next occurrence of task {task_id} as task {next_task.id}")
                
                # Schedule reminders for the new task
                self.schedule_reminders_for_task(next_task)
                
        except Exception as e:
            logger.error(f"Error creating next occurrence for task {task_id}: {str(e)}")
    
    def get_upcoming_reminders(self, session: Session, user_id: int, hours_ahead: int = 24) -> List[Task]:
        """Get tasks with due dates within the specified timeframe"""
        cutoff_time = datetime.utcnow() + timedelta(hours=hours_ahead)
        
        statement = select(Task).where(
            Task.user_id == user_id,
            Task.due_date != None,
            Task.due_date <= cutoff_time,
            Task.completed == False
        ).order_by(Task.due_date.asc())
        
        upcoming_tasks = session.exec(statement).all()
        logger.info(f"Found {len(upcoming_tasks)} upcoming tasks for user {user_id}")
        
        return upcoming_tasks