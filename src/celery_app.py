from celery import Celery
from datetime import datetime, timedelta
import os

celery = Celery(
    'todo_app',
    broker=os.environ.get('REDIS_URL', 'redis://localhost:6379/0'),
    backend=os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
)

celery.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,
    task_soft_time_limit=25 * 60,
    beat_schedule={
        'send-daily-reminders': {
            'task': 'src.celery_tasks.send_daily_reminders',
            'schedule': timedelta(hours=24),
        },
        'cleanup-old-tasks': {
            'task': 'src.celery_tasks.cleanup_old_tasks',
            'schedule': timedelta(days=7),
        },
    }
)

@celery.task(name='src.celery_tasks.send_daily_reminders')
def send_daily_reminders():
    """Send daily reminders for tasks due soon"""
    from src.models.database import db, Todo, User
    from src.services.email_service import send_todo_reminder
    
    # Get tasks due in next 24 hours
    tomorrow = datetime.utcnow() + timedelta(days=1)
    todos = Todo.query.filter(
        Todo.due_date <= tomorrow.date(),
        Todo.completed == False
    ).all()
    
    # Group by user
    users = {}
    for todo in todos:
        if todo.user_id not in users:
            users[todo.user_id] = []
        users[todo.user_id].append(todo)
    
    # Send reminders
    for user_id, user_todos in users.items():
        user = User.query.get(user_id)
        if user and user.email:
            send_todo_reminder(
                user.email,
                'reminder',
                {'count': len(user_todos)}
            )
    
    return f"Sent reminders to {len(users)} users"

@celery.task(name='src.celery_tasks.cleanup_old_tasks')
def cleanup_old_tasks():
    """Clean up completed tasks older than 30 days"""
    from src.models.database import db, Todo
    
    cutoff_date = datetime.utcnow() - timedelta(days=30)
    old_tasks = Todo.query.filter(
        Todo.completed == True,
        Todo.updated_at <= cutoff_date
    ).delete()
    
    db.session.commit()
    return f"Deleted {old_tasks} old tasks"
