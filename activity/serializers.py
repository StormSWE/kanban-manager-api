from __future__ import annotations

from rest_framework import serializers

from .models import ActivityLog


class ActivityLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityLog
        fields = ("id", "user", "action", "target_type", "target_id", "timestamp", "metadata")
        read_only_fields = ("id", "timestamp")
