from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Team, TeamMember

User = get_user_model()


class TeamApiTests(APITestCase):
	def setUp(self):
		self.owner = User.objects.create_user(email="owner@example.com", password="VeryStrong123")
		self.client.force_authenticate(self.owner)
		self.team = Team.objects.create(name="Core Team", description="Test", created_by=self.owner)
		TeamMember.objects.create(team=self.team, user=self.owner, role=TeamMember.RoleChoices.OWNER)

	def test_create_team(self):
		url = reverse("teams:team-list")
		payload = {"name": "API Team", "description": "Created via API"}
		response = self.client.post(url, payload, format="json")
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		self.assertEqual(response.data["name"], "API Team")

	def test_add_member(self):
		user = User.objects.create_user(email="member@example.com", password="Pass123456")
		url = reverse("teams:team-members", args=[self.team.id])
		payload = {"user_id": user.id, "role": TeamMember.RoleChoices.MEMBER}
		response = self.client.post(url, payload, format="json")
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		self.assertTrue(TeamMember.objects.filter(team=self.team, user=user).exists())

	def test_transfer_owner(self):
		new_owner = User.objects.create_user(email="new-owner@example.com", password="Pass123456")
		TeamMember.objects.create(team=self.team, user=new_owner, role=TeamMember.RoleChoices.ADMIN)
		url = reverse("teams:team-transfer-owner", args=[self.team.id])
		response = self.client.post(url, {"new_owner_id": new_owner.id}, format="json")
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertTrue(TeamMember.objects.filter(team=self.team, user=new_owner, role=TeamMember.RoleChoices.OWNER).exists())
