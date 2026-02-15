import logging
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select
from typing import List
from datetime import datetime, timedelta
from ..database import get_session
from ..models.task import Task
from ..models.user import User
from ..schemas.task import TaskCreate, TaskRead, TaskUpdate
from ..middleware.auth import get_current_user
from ..services.task_service import create_task, get_tasks, get_task, get_task_for_user, update_task, delete_task
from ..services.reminder_service import ReminderService

# Set up logging
logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/", response_model=List[TaskRead])
def read_tasks(
    search: str = None,
    filter_by: str = None,
    sort_by: str = None,
    sort_order: str = Query('desc', enum=['asc', 'desc']),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get all tasks for the current user with optional search, filter, and sort
    """
    logger.info(f"User {current_user.id} requested tasks with search='{search}', filter='{filter_by}', sort='{sort_by}'")
    try:
        tasks = get_tasks(session, current_user.id, search=search, filter_by=filter_by, sort_by=sort_by, sort_order=sort_order)
        logger.info(f"Successfully retrieved {len(tasks)} tasks for user {current_user.id}")
        return tasks
    except Exception as e:
        logger.error(f"Error retrieving tasks for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving tasks"
        )

@router.post("/", response_model=TaskRead)
async def create_task_endpoint(
    task: TaskCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Create a new task for the current user
    """
    logger.info(f"User {current_user.id} attempting to create new task")
    try:
        # Create a Task instance with the user_id from the authenticated user
        db_task = Task(
            **task.dict(),
            user_id=current_user.id
        )
        created_task = await create_task(session, db_task)
        logger.info(f"Successfully created task {created_task.id} for user {current_user.id}")
        return created_task
    except Exception as e:
        logger.error(f"Error creating task for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the task"
        )

@router.get("/{task_id}", response_model=TaskRead)
def read_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get a specific task by ID
    """
    logger.info(f"User {current_user.id} attempting to access task {task_id}")
    try:
        task = get_task_for_user(session, task_id, current_user.id)
        if not task:
            logger.warning(f"User {current_user.id} attempted to access non-existent task {task_id}")
            raise HTTPException(status_code=404, detail="Task not found")
        logger.info(f"Successfully retrieved task {task_id} for user {current_user.id}")
        return task
    except HTTPException:
        logger.warning(f"Failed to retrieve task {task_id} for user {current_user.id}")
        raise
    except Exception as e:
        logger.error(f"Error retrieving task {task_id} for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving the task"
        )

@router.put("/{task_id}", response_model=TaskRead)
def update_task_endpoint(
    task_id: int,
    task: TaskUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Update a specific task by ID
    """
    logger.info(f"User {current_user.id} attempting to update task {task_id}")
    try:
        db_task = get_task_for_user(session, task_id, current_user.id)
        if not db_task:
            logger.warning(f"User {current_user.id} attempted to update non-existent task {task_id}")
            raise HTTPException(status_code=404, detail="Task not found")

        # Update the task with new values
        for field, value in task.dict(exclude_unset=True).items():
            setattr(db_task, field, value)

        updated_task = update_task(session, db_task)
        logger.info(f"Successfully updated task {task_id} for user {current_user.id}")
        return updated_task
    except HTTPException:
        logger.warning(f"Failed to update task {task_id} for user {current_user.id}")
        raise
    except Exception as e:
        logger.error(f"Error updating task {task_id} for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating the task"
        )

@router.delete("/{task_id}")
def delete_task_endpoint(
    task_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Delete a specific task by ID
    """
    logger.info(f"User {current_user.id} attempting to delete task {task_id}")
    try:
        # Try to delete the task directly with ownership verification
        statement = select(Task).where(Task.id == task_id, Task.user_id == current_user.id)
        db_task = session.exec(statement).first()

        if not db_task:
            # Task doesn't exist or doesn't belong to user - return success for idempotency
            logger.info(f"Task {task_id} not found for user {current_user.id}, possibly already deleted")
            return {"message": "Task deleted successfully"}

        # Task exists and belongs to user, proceed with deletion
        session.delete(db_task)
        session.commit()
        logger.info(f"Successfully deleted task {task_id} for user {current_user.id}")
        return {"message": "Task deleted successfully"}
    except HTTPException:
        # Re-raise HTTP exceptions (like 401 Unauthorized from get_current_user)
        logger.warning(f"HTTP exception in delete task {task_id} for user {current_user.id}")
        raise
    except Exception as e:
        logger.error(f"Error deleting task {task_id} for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while deleting the task"
        )


@router.get("/reminders/upcoming", response_model=List[TaskRead])
def get_upcoming_reminders(
    hours_ahead: int = Query(24, ge=1, le=168),  # 1 week max
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get tasks with due dates within the specified timeframe for the current user
    """
    logger.info(f"User {current_user.id} requesting upcoming reminders within {hours_ahead} hours")
    try:
        reminder_service = ReminderService()
        upcoming_tasks = reminder_service.get_upcoming_reminders(session, current_user.id, hours_ahead)
        logger.info(f"Successfully retrieved {len(upcoming_tasks)} upcoming tasks for user {current_user.id}")
        return upcoming_tasks
    except Exception as e:
        logger.error(f"Error retrieving upcoming tasks for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving upcoming tasks"
        )


@router.get("/due_soon", response_model=List[TaskRead])
def get_due_soon_tasks(
    hours_ahead: int = Query(24, ge=1, le=168),  # 1 week max
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get tasks that are due soon (within specified hours) for the current user
    """
    logger.info(f"User {current_user.id} requesting tasks due within {hours_ahead} hours")
    try:
        cutoff_time = datetime.utcnow() + timedelta(hours=hours_ahead)
        
        statement = select(Task).where(
            Task.user_id == current_user.id,
            Task.due_date != None,
            Task.due_date <= cutoff_time,
            Task.completed == False
        ).order_by(Task.due_date.asc())
        
        due_soon_tasks = session.exec(statement).all()
        logger.info(f"Successfully retrieved {len(due_soon_tasks)} tasks due soon for user {current_user.id}")
        return due_soon_tasks
    except Exception as e:
        logger.error(f"Error retrieving due soon tasks for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving due soon tasks"
        )