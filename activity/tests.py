from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from projects.models import Project, ProjectMember
from teams.models import Team, TeamMember
from boards.models import Board, BoardList
from tasks.models import Task
from comments.models import Comment
from .models import ActivityLog

User = get_user_model()


class ActivityApiTests(APITestCase):
	def setUp(self):
		self.user = User.objects.create_user(email="actor@example.com", password="StrongPass123")
		self.team = Team.objects.create(name="Team Alpha", description="", created_by=self.user)
		TeamMember.objects.create(team=self.team, user=self.user, role=TeamMember.RoleChoices.OWNER)
		self.project = Project.objects.create(team=self.team, name="Project A")
		ProjectMember.objects.create(project=self.project, user=self.user, role=ProjectMember.RoleChoices.MANAGER)
		self.board = Board.objects.create(project=self.project, name="Activity Board")
		self.list_todo = BoardList.objects.filter(board=self.board).first()
		self.client.force_authenticate(self.user)

	def test_project_activity_logged_on_task_comment(self):
		# create a task
		task = Task.objects.create(project=self.project, board_list=self.list_todo, title="Task X", position=1)
		# create a comment
		comment = Comment.objects.create(task=task, user=self.user, text="Hello")
		# Now query activity for project
		url = reverse("activity:project-activity", args=[self.project.id])
		response = self.client.get(url)
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		# at least one of the logs must include project_id
		data = response.data.get("results", response.data)
		self.assertTrue(any(item["metadata"].get("project_id") == str(self.project.id) for item in data))

