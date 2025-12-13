from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from django.conf import settings
from django.core.files.base import File
from django.core.files.storage import default_storage


def user_avatar_upload_path(instance, filename: str) -> str:
    ext = Path(filename).suffix or ".jpg"
    identifier = instance.pk or uuid4()
    return f"users/{identifier}/avatar{ext}"


def replace_user_avatar(user, new_file: File | None) -> None:
    old_path = user.avatar.name if user.avatar else None
    if new_file is None:
        user.avatar = None
    else:
        user.avatar = new_file
    if old_path and default_storage.exists(old_path):
        default_storage.delete(old_path)


def build_avatar_response(user) -> str | None:
    if user.avatar and hasattr(user.avatar, "url"):
        url = user.avatar.url
        if url.startswith("http"):
            return url
        media_url = getattr(settings, "MEDIA_URL", "").rstrip("/")
        return f"{media_url}{url}" if media_url else url
    return None
