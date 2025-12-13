from __future__ import annotations

import logging

from celery import shared_task
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail

logger = logging.getLogger(__name__)
User = get_user_model()


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True)
def send_welcome_email(self, user_id: str) -> None:
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:  # pragma: no cover - safety guard
        logger.warning("User %s not found for welcome email", user_id)
        return

    subject = "Welcome to Kanban Manager"
    body = f"Hi {user.get_full_name() or 'there'}, welcome aboard!"
    send_mail(
        subject,
        body,
        getattr(settings, "DEFAULT_FROM_EMAIL", "no-reply@example.com"),
        [user.email],
        fail_silently=True,
    )
    logger.info("Welcome email queued for %s", user.email)


@shared_task(bind=True)
def notify_profile_updated(self, user_id: str) -> None:
    logger.info("Profile updated for user %s", user_id)
