from __future__ import annotations

from typing import Any, Optional

from django.contrib.contenttypes.models import ContentType
from django.db import transaction

from .models import ActivityLog


@transaction.atomic
def create_activity_log(user: Optional[Any], action: str, target: Optional[Any] = None, metadata: Optional[dict] = None) -> ActivityLog:
    """
    Helper that creates an ActivityLog for a given action and target object.
    The `target` can be any model instance; we store its content type and pk.
    If the target has a `project_id` property or metadata indicating a `project_id` this function will not modify it; signals should pass along project context.
    """
    if metadata is None:
        metadata = {}
    target_type = ""
    target_id = ""
    if target is not None:
        ct = ContentType.objects.get_for_model(target.__class__)
        target_type = f"{ct.app_label}.{ct.model}"
        target_id = str(getattr(target, "pk", getattr(target, "id", "")))
    log = ActivityLog.objects.create(
        user=user if user is not None else None,
        action=action,
        target_type=target_type,
        target_id=target_id,
        metadata=metadata,
    )
    return log
