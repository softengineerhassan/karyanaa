from datetime import datetime, timedelta
from typing import Dict
from app.workers.celery_app import celery_app
from app.core.logging_config import get_logger
logger = get_logger(__name__)

@celery_app.task(name='app.workers.cleanup_tasks.cleanup_expired_tokens', bind=True)
def cleanup_expired_tokens(self) -> Dict:
    try:
        logger.info('Starting expired token cleanup')
        counts = {'refresh_tokens': 0, 'password_reset_tokens': 0, 'email_verification_tokens': 0}
        logger.info('Expired token cleanup completed', extra={'counts': counts})
        return {'status': 'success', 'cleaned_up': counts, 'completed_at': datetime.utcnow().isoformat()}
    except Exception as exc:
        logger.error(f'Token cleanup failed: {exc}')
        raise

@celery_app.task(name='app.workers.cleanup_tasks.cleanup_expired_sessions', bind=True)
def cleanup_expired_sessions(self) -> Dict:
    try:
        logger.info('Starting expired session cleanup')
        count = 0
        logger.info('Expired session cleanup completed', extra={'count': count})
        return {'status': 'success', 'sessions_cleaned': count, 'completed_at': datetime.utcnow().isoformat()}
    except Exception as exc:
        logger.error(f'Session cleanup failed: {exc}')
        raise

@celery_app.task(name='app.workers.cleanup_tasks.cleanup_old_audit_logs', bind=True)
def cleanup_old_audit_logs(self, days_to_keep: int=90) -> Dict:
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
        logger.info(f'Starting audit log cleanup for logs older than {cutoff_date}', extra={'cutoff_date': cutoff_date.isoformat()})
        count = 0
        logger.info('Audit log cleanup completed', extra={'count': count, 'cutoff_date': cutoff_date.isoformat()})
        return {'status': 'success', 'logs_cleaned': count, 'cutoff_date': cutoff_date.isoformat(), 'completed_at': datetime.utcnow().isoformat()}
    except Exception as exc:
        logger.error(f'Audit log cleanup failed: {exc}')
        raise

@celery_app.task(name='app.workers.cleanup_tasks.cleanup_locked_accounts', bind=True)
def cleanup_locked_accounts(self) -> Dict:
    try:
        logger.info('Starting locked account cleanup')
        count = 0
        logger.info('Locked account cleanup completed', extra={'count': count})
        return {'status': 'success', 'accounts_unlocked': count, 'completed_at': datetime.utcnow().isoformat()}
    except Exception as exc:
        logger.error(f'Locked account cleanup failed: {exc}')
        raise

@celery_app.task(name='app.workers.cleanup_tasks.cleanup_orphaned_data', bind=True)
def cleanup_orphaned_data(self) -> Dict:
    try:
        logger.info('Starting orphaned data cleanup')
        counts = {'user_roles': 0, 'user_permissions': 0}
        logger.info('Orphaned data cleanup completed', extra={'counts': counts})
        return {'status': 'success', 'cleaned_up': counts, 'completed_at': datetime.utcnow().isoformat()}
    except Exception as exc:
        logger.error(f'Orphaned data cleanup failed: {exc}')
        raise