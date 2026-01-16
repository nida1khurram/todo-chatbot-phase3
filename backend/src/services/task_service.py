import logging
from sqlmodel import Session, select
from typing import List
from ..models.task import Task
from ..models.user import User

# Set up logging
logger = logging.getLogger(__name__)

def create_task(session: Session, task: Task) -> Task:
    """
    Create a new task
    """
    logger.info(f"Creating new task for user ID: {task.user_id}")
    try:
        session.add(task)
        session.commit()
        session.refresh(task)
        logger.info(f"Successfully created task with ID: {task.id}")
        return task
    except Exception as e:
        logger.error(f"Error creating task for user {task.user_id}: {str(e)}")
        raise

def get_tasks(session: Session, user_id: int) -> List[Task]:
    """
    Get all tasks for a specific user
    """
    logger.info(f"Retrieving all tasks for user ID: {user_id}")
    try:
        statement = select(Task).where(Task.user_id == user_id)
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

def update_task(session: Session, task: Task) -> Task:
    """
    Update a task
    """
    logger.info(f"Updating task with ID: {task.id}")
    try:
        session.add(task)
        session.commit()
        session.refresh(task)
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