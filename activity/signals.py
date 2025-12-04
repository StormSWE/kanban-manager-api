import logging
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from tasks.models import Task, Subtask
from comments.models import Comment
from projects.models import Project

from .services import create_activity_log

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Task)
def task_activity(sender, instance, created, **kwargs):
    data = {"project_id": str(instance.project_id)}
    action = "task_created" if created else "task_updated"
    create_activity_log(user=getattr(instance, "assigned_to", None), action=action, target=instance, metadata=data)


@receiver(pre_save, sender=Task)
def task_move_activity(sender, instance, **kwargs):
    if not instance.pk:
        return
    try:
        old = Task.objects.get(pk=instance.pk)
    except Task.DoesNotExist:
        return
    if old.board_list_id != instance.board_list_id:
        data = {"project_id": str(instance.project_id), "from_list": str(old.board_list_id), "to_list": str(instance.board_list_id)}
        create_activity_log(user=getattr(instance, "assigned_to", None), action="task_moved", target=instance, metadata=data)


@receiver(post_save, sender=Subtask)
def subtask_activity(sender, instance, created, **kwargs):
    data = {"project_id": str(instance.task.project_id), "task_id": str(instance.task_id)}
    action = "subtask_created" if created else "subtask_updated"
    # Use the task's assigned user as the actor if available
    user = getattr(instance.task, "assigned_to", None)
    create_activity_log(user=user, action=action, target=instance, metadata=data)


@receiver(post_save, sender=Comment)
def comment_activity(sender, instance, created, **kwargs):
    data = {"project_id": str(instance.task.project_id), "task_id": str(instance.task_id)}
    action = "comment_created" if created else "comment_updated"
    create_activity_log(user=instance.user, action=action, target=instance, metadata=data)


@receiver(post_save, sender=Project)
def project_activity(sender, instance, created, **kwargs):
    data = {"project_id": str(instance.id)}
    action = "project_created" if created else "project_updated"
    create_activity_log(user=getattr(instance, "created_by", None), action=action, target=instance, metadata=data)
