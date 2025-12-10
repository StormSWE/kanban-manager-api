from __future__ import annotations

import logging
from typing import Optional

from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMessage

logger = logging.getLogger(__name__)


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 3})
def send_email_task(self, subject: str, body: str, recipient_email: str) -> Optional[int]:
    """Send a single email using Django's EmailMessage. Runs in Celery worker."""
    try:
        email = EmailMessage(
            subject=subject,
            body=body,
            from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
            to=[recipient_email],
        )
        sent_count = email.send(fail_silently=False)
        if sent_count:
            logger.info("Email sent successfully to %s subject=%s", recipient_email, subject)
        else:
            logger.warning("Email send returned 0 for %s subject=%s", recipient_email, subject)
        return sent_count
    except Exception:
        logger.exception("Email send failed to %s subject=%s", recipient_email, subject)
        raise


def send_email(subject: str, body: str, recipient_email: str):
    """Enqueue an email to be sent asynchronously via Celery."""
    if not recipient_email:
        logger.warning("Skipping email send because recipient is empty for subject=%s", subject)
        return None
    return send_email_task.delay(subject, body, recipient_email)
