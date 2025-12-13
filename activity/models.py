from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils import timezone


class ActivityLog(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="activity_logs")
	action = models.CharField(max_length=200)
	target_type = models.CharField(max_length=255, blank=True)
	target_id = models.CharField(max_length=255, blank=True)
	timestamp = models.DateTimeField(default=timezone.now)
	metadata = models.JSONField(default=dict, blank=True)

	class Meta:
		ordering = ("-timestamp", "-id")

	def __str__(self):
		return f"{self.action} by {self.user_id} on {self.target_type}:{self.target_id} at {self.timestamp}"

