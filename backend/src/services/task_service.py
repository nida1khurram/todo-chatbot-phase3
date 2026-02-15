import logging
from sqlmodel import Session, select
from typing import List
from datetime import datetime
from ..models.task import Task
from ..models.user import User
from .reminder_service import ReminderService
from .kafka_service import KafkaService

# Set up logging
logger = logging.getLogger(__name__)

async def create_task(session: Session, task: Task) -> Task:
    """
    Create a new task
    """
    logger.info(f"Creating new task for user ID: {task.user_id}")
    try:
        session.add(task)
        session.commit()
        session.refresh(task)
        
        # Schedule reminders if due date is set
        if task.due_date:
            reminder_service = ReminderService()
            reminder_service.schedule_reminders_for_task(task)
        
        # Schedule recurring tasks if applicable
        if task.recurrence_rule:
            reminder_service = ReminderService()
            reminder_service.schedule_recurring_task(task)
        
        # Publish task created event to Kafka
        try:
            kafka_service = KafkaService()
            task_dict = task.dict() if hasattr(task, 'dict') else {c.name: getattr(task, c.name) for c in task.__table__.columns}
            await kafka_service.send_task_event('created', task_dict, key=str(task.id))
        except Exception as e:
            logger.error(f"Error publishing task created event: {str(e)}")
        
        logger.info(f"Successfully created task with ID: {task.id}")
        return task
    except Exception as e:
        logger.error(f"Error creating task for user {task.user_id}: {str(e)}")
        raise

def get_tasks(session: Session, user_id: int, search: str = None, filter_by: str = None,
             sort_by: str = None, sort_order: str = 'asc') -> List[Task]:
    """
    Get all tasks for a specific user with optional search, filter, and sort
    """
    logger.info(f"Retrieving tasks for user ID: {user_id} with search='{search}', filter='{filter_by}', sort='{sort_by}'")
    try:
        statement = select(Task).where(Task.user_id == user_id)

        # Apply search filter if provided
        if search:
            statement = statement.where(
                Task.title.contains(search) |
                Task.description.contains(search) |
                Task.tags.contains(search) if Task.tags is not None else False
            )

        # Apply filter if provided
        if filter_by == 'completed':
            statement = statement.where(Task.completed == True)
        elif filter_by == 'pending':
            statement = statement.where(Task.completed == False)
        elif filter_by == 'high':
            statement = statement.where(Task.priority == 'high')
        elif filter_by == 'medium':
            statement = statement.where(Task.priority == 'medium')
        elif filter_by == 'low':
            statement = statement.where(Task.priority == 'low')
        elif filter_by == 'overdue':
            from datetime import datetime
            statement = statement.where(
                Task.due_date < datetime.utcnow(),
                Task.completed == False
            )

        # Apply sorting
        if sort_by == 'due_date':
            if sort_order == 'desc':
                statement = statement.order_by(Task.due_date.desc())
            else:
                statement = statement.order_by(Task.due_date.asc())
        elif sort_by == 'priority':
            if sort_order == 'desc':
                statement = statement.order_by(Task.priority.desc())
            else:
                statement = statement.order_by(Task.priority.asc())
        elif sort_by == 'title':
            if sort_order == 'desc':
                statement = statement.order_by(Task.title.desc())
            else:
                statement = statement.order_by(Task.title.asc())
        elif sort_by == 'created_at':
            if sort_order == 'desc':
                statement = statement.order_by(Task.created_at.desc())
            else:
                statement = statement.order_by(Task.created_at.asc())
        else:  # Default sort by created_at desc
            statement = statement.order_by(Task.created_at.desc())

        tasks = session.exec(statement).all()
        logger.info(f"Found {len(tasks)} tasks for user ID: {user_id}")
        return tasks
    except Exception as e:
        logger.error(f"Error retrieving tasks for user {user_id}: {str(e)}")
        raise

def get_task(session: Session, task_id: int) -> Task:
    """
    Get a specific task by ID
    """
    logger.info(f"Retrieving task by ID: {task_id}")
    try:
        statement = select(Task).where(Task.id == task_id)
        task = session.exec(statement).first()
        if task:
            logger.info(f"Found task with ID: {task.id}")
        else:
            logger.info(f"No task found with ID: {task_id}")
        return task
    except Exception as e:
        logger.error(f"Error retrieving task with ID {task_id}: {str(e)}")
        raise


def get_task_for_user(session: Session, task_id: int, user_id: int) -> Task:
    """
    Get a specific task by ID for a specific user (with ownership check)
    """
    logger.info(f"Retrieving task {task_id} for user {user_id}")
    try:
        statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
        task = session.exec(statement).first()
        if task:
            logger.info(f"Found task {task.id} for user {user_id}")
        else:
            logger.info(f"No task found with ID {task_id} for user {user_id}")
        return task
    except Exception as e:
        logger.error(f"Error retrieving task {task_id} for user {user_id}: {str(e)}")
        raise


def check_task_ownership(session: Session, task_id: int, user_id: int) -> bool:
    """
    Check if a user owns a specific task
    """
    logger.info(f"Checking ownership of task {task_id} for user {user_id}")
    try:
        statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
        task = session.exec(statement).first()
        is_owner = task is not None
        logger.info(f"Ownership check result for task {task_id} and user {user_id}: {is_owner}")
        return is_owner
    except Exception as e:
        logger.error(f"Error checking ownership of task {task_id} for user {user_id}: {str(e)}")
        raise

async def update_task(session: Session, task: Task) -> Task:
    """
    Update a task
    """
    logger.info(f"Updating task with ID: {task.id}")
    try:
        # Get the original task to check if due_date or recurrence changed
        original_task = session.get(Task, task.id)
        original_due_date = original_task.due_date if original_task else None
        original_recurrence_rule = original_task.recurrence_rule if original_task else None
        
        session.add(task)
        session.commit()
        session.refresh(task)
        
        # Handle reminder scheduling if due date changed
        if original_due_date != task.due_date:
            reminder_service = ReminderService()
            reminder_service.schedule_reminders_for_task(task)
        
        # Handle recurrence scheduling if recurrence rule changed
        if original_recurrence_rule != task.recurrence_rule:
            reminder_service = ReminderService()
            if original_recurrence_rule:
                reminder_service.cancel_recurring_task(task.id)
            if task.recurrence_rule:
                reminder_service.schedule_recurring_task(task)
        
        # Publish task updated event to Kafka
        try:
            kafka_service = KafkaService()
            task_dict = task.dict() if hasattr(task, 'dict') else {c.name: getattr(task, c.name) for c in task.__table__.columns}
            await kafka_service.send_task_event('updated', task_dict, key=str(task.id))
        except Exception as e:
            logger.error(f"Error publishing task updated event: {str(e)}")
        
        logger.info(f"Successfully updated task with ID: {task.id}")
        return task
    except Exception as e:
        logger.error(f"Error updating task with ID {task.id}: {str(e)}")
        raise

def delete_task(session: Session, task_id: int) -> bool:
    """
    Delete a task by ID
    """
    logger.info(f"Deleting task with ID: {task_id}")
    try:
        task = session.get(Task, task_id)
        if task:
            # Cancel any scheduled reminders for this task
            reminder_service = ReminderService()
            reminder_service.cancel_reminders_for_task(task_id)
            reminder_service.cancel_recurring_task(task_id)
            
            session.delete(task)
            session.commit()
            logger.info(f"Successfully deleted task with ID: {task_id}")
            return True
        else:
            logger.info(f"Task with ID {task_id} not found for deletion")
            return False
    except Exception as e:
        logger.error(f"Error deleting task with ID {task_id}: {str(e)}")
        raise