from typing import Dict, Optional
from app.workers.celery_app import celery_app
from app.core.config import settings
from app.core.logging_config import get_logger
logger = get_logger(__name__)

@celery_app.task(name='app.workers.email_tasks.send_verification_email', bind=True, max_retries=3)
def send_verification_email(self, user_id: str, email: str, verification_token: str, full_name: Optional[str]=None) -> Dict:
    try:
        logger.info(f'Sending verification email', extra={'user_id': user_id, 'email': email})
        verification_url = f'{settings.CORS_ORIGINS[0]}/verify-email?token={verification_token}'
        logger.info(f'Verification email would be sent', extra={'user_id': user_id, 'email': email, 'verification_url': verification_url})
        return {'status': 'success', 'user_id': user_id, 'email': email}
    except Exception as exc:
        logger.error(f'Failed to send verification email: {exc}', extra={'user_id': user_id, 'email': email})
        raise self.retry(exc=exc)

@celery_app.task(name='app.workers.email_tasks.send_password_reset_email', bind=True, max_retries=3)
def send_password_reset_email(self, user_id: str, email: str, reset_token: str, full_name: Optional[str]=None) -> Dict:
    try:
        logger.info(f'Sending password reset email', extra={'user_id': user_id, 'email': email})
        reset_url = f'{settings.CORS_ORIGINS[0]}/reset-password?token={reset_token}'
        logger.info(f'Password reset email would be sent', extra={'user_id': user_id, 'email': email, 'reset_url': reset_url})
        return {'status': 'success', 'user_id': user_id, 'email': email}
    except Exception as exc:
        logger.error(f'Failed to send password reset email: {exc}', extra={'user_id': user_id, 'email': email})
        raise self.retry(exc=exc)

@celery_app.task(name='app.workers.email_tasks.send_welcome_email', bind=True, max_retries=3)
def send_welcome_email(self, user_id: str, email: str, full_name: Optional[str]=None) -> Dict:
    try:
        logger.info(f'Sending welcome email', extra={'user_id': user_id, 'email': email})
        logger.info(f'Welcome email would be sent', extra={'user_id': user_id, 'email': email})
        return {'status': 'success', 'user_id': user_id, 'email': email}
    except Exception as exc:
        logger.error(f'Failed to send welcome email: {exc}', extra={'user_id': user_id, 'email': email})
        raise self.retry(exc=exc)

@celery_app.task(name='app.workers.email_tasks.send_login_alert_email', bind=True, max_retries=2)
def send_login_alert_email(self, user_id: str, email: str, ip_address: str, user_agent: str, location: Optional[str]=None) -> Dict:
    try:
        logger.info(f'Sending login alert email', extra={'user_id': user_id, 'email': email, 'ip_address': ip_address})
        logger.info(f'Login alert email would be sent', extra={'user_id': user_id, 'email': email, 'ip_address': ip_address})
        return {'status': 'success', 'user_id': user_id, 'email': email}
    except Exception as exc:
        logger.error(f'Failed to send login alert email: {exc}', extra={'user_id': user_id, 'email': email})
        raise self.retry(exc=exc)

@celery_app.task(name='app.workers.email_tasks.send_password_changed_email', bind=True, max_retries=3)
def send_password_changed_email(self, user_id: str, email: str, full_name: Optional[str]=None) -> Dict:
    try:
        logger.info(f'Sending password changed email', extra={'user_id': user_id, 'email': email})
        logger.info(f'Password changed email would be sent', extra={'user_id': user_id, 'email': email})
        return {'status': 'success', 'user_id': user_id, 'email': email}
    except Exception as exc:
        logger.error(f'Failed to send password changed email: {exc}', extra={'user_id': user_id, 'email': email})
        raise self.retry(exc=exc)