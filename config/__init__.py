from .celery import app as celery_app

# Also expose the Celery application as `app` to allow `-A config` usage
# as well as `-A config.celery`.
app = celery_app

__all__ = ("celery_app", "app")
