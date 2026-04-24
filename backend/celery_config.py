# backend/celery_config.py

from celery.schedules import crontab
import os

redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
broker_url = redis_url
result_backend = redis_url

task_serializer = 'json'
accept_content = ['json']
result_serializer = 'json'
timezone = 'UTC'
enable_utc = True

# Schedule tasks
beat_schedule = {
    # Run anomaly detection every 6 hours
    'run-outbreak-detection': {
        'task': 'tasks.run_outbreak_detection',
        'schedule': crontab(minute=0, hour='*/6'),  # Every 6 hours
        'args': (None,)  # None = all locations
    },
    
    # Optional: Clean old data every day
    'cleanup-old-anomalies': {
        'task': 'tasks.cleanup_old_anomalies',
        'schedule': crontab(hour=0, minute=0),  # Daily at midnight
    }
}