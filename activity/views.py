from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions
from rest_framework.response import Response

from projects.permissions import IsProjectMember
from projects.models import Project

from .models import ActivityLog
from .serializers import ActivityLogSerializer


class ProjectActivityListView(generics.ListAPIView):
	serializer_class = ActivityLogSerializer
	permission_classes = (permissions.IsAuthenticated, IsProjectMember)

	def get_queryset(self):
		project_pk = self.kwargs.get("project_pk")
		# Only include activity logs that include project id in metadata
		return ActivityLog.objects.filter(metadata__project_id=str(project_pk))

