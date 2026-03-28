from celery import Celery
from celery.schedules import crontab
from app.core.config import settings

# If Celery broker/backend settings are commented out in config, fall back to
# in-memory alternatives to avoid Redis dependency.
_broker = getattr(settings, 'CELERY_BROKER_URL', 'memory://')
_backend = getattr(settings, 'CELERY_RESULT_BACKEND', 'cache+memory://')
celery_app = Celery('auth_service', broker=_broker, backend=_backend)
celery_app.conf.update(task_serializer='json', accept_content=['json'], result_serializer='json', timezone='UTC', enable_utc=True, task_acks_late=True, task_reject_on_worker_lost=True, task_time_limit=300, task_soft_time_limit=240, worker_prefetch_multiplier=1, worker_max_tasks_per_child=1000, worker_disable_rate_limits=False, result_expires=3600, task_routes={'app.workers.email_tasks.*': {'queue': 'email'}, 'app.workers.cleanup_tasks.*': {'queue': 'cleanup'}, 'app.workers.sync_tasks.*': {'queue': 'sync'}, 'app.workers.indexing_tasks.*': {'queue': 'indexing'}}, imports=['app.workers.email_tasks', 'app.workers.cleanup_tasks'])
celery_app.conf.beat_schedule = {'cleanup-expired-tokens': {'task': 'app.workers.cleanup_tasks.cleanup_expired_tokens', 'schedule': crontab(minute=0), 'options': {'queue': 'cleanup'}}, 'cleanup-expired-sessions': {'task': 'app.workers.cleanup_tasks.cleanup_expired_sessions', 'schedule': crontab(minute=0, hour='*/6'), 'options': {'queue': 'cleanup'}}, 'cleanup-old-audit-logs': {'task': 'app.workers.cleanup_tasks.cleanup_old_audit_logs', 'schedule': crontab(minute=0, hour=3, day_of_month=1), 'options': {'queue': 'cleanup'}}}

class AuthServiceTask(celery_app.Task):
    abstract = True
    autoretry_for = (Exception,)
    retry_backoff = True
    retry_backoff_max = 600
    retry_jitter = True
    max_retries = 3

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        print(f'Task {self.name}[{task_id}] failed: {exc}')

    def on_success(self, retval, task_id, args, kwargs):
        pass

    def on_retry(self, exc, task_id, args, kwargs, einfo):
        print(f'Task {self.name}[{task_id}] retrying: {exc}')
celery_app.Task = AuthServiceTask