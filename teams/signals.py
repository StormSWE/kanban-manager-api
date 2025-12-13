import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import TeamInvite, TeamMember

logger = logging.getLogger(__name__)


@receiver(post_save, sender=TeamMember)
def log_membership(sender, instance, created, **kwargs):
    if created:
        logger.info("User %s joined team %s as %s", instance.user_id, instance.team_id, instance.role)


@receiver(post_save, sender=TeamInvite)
def log_invite(sender, instance, created, **kwargs):
    if created:
        logger.info("Invite created for %s to join team %s", instance.email, instance.team_id)
