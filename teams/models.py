from __future__ import annotations

from uuid import uuid4

from django.conf import settings
from django.db import models
from django.utils import timezone

User = settings.AUTH_USER_MODEL


def generate_invite_token():
	return uuid4().hex


class Team(models.Model):
	name = models.CharField(max_length=150)
	description = models.TextField(blank=True)
	created_by = models.ForeignKey(User, related_name="teams_created", on_delete=models.CASCADE)
	created_at = models.DateTimeField(default=timezone.now)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ("name",)

	def __str__(self):
		return self.name

	@property
	def owners(self):
		return self.members.filter(role=TeamMember.RoleChoices.OWNER)


class TeamMember(models.Model):
	class RoleChoices(models.TextChoices):
		OWNER = "owner", "Owner"
		ADMIN = "admin", "Admin"
		MEMBER = "member", "Member"
		VIEWER = "viewer", "Viewer"

	team = models.ForeignKey(Team, related_name="members", on_delete=models.CASCADE)
	user = models.ForeignKey(User, related_name="team_memberships", on_delete=models.CASCADE)
	role = models.CharField(max_length=20, choices=RoleChoices.choices, default=RoleChoices.MEMBER)
	joined_at = models.DateTimeField(default=timezone.now)

	class Meta:
		unique_together = ("team", "user")
		ordering = ("team", "user")

	def __str__(self):
		return f"{self.user} -> {self.team} ({self.role})"

	@property
	def is_owner(self):
		return self.role == self.RoleChoices.OWNER


class TeamInvite(models.Model):
	class StatusChoices(models.TextChoices):
		PENDING = "pending", "Pending"
		ACCEPTED = "accepted", "Accepted"
		REVOKED = "revoked", "Revoked"

	token = models.CharField(max_length=64, unique=True, default=generate_invite_token)
	team = models.ForeignKey(Team, related_name="invites", on_delete=models.CASCADE)
	email = models.EmailField()
	role = models.CharField(max_length=20, choices=TeamMember.RoleChoices.choices, default=TeamMember.RoleChoices.MEMBER)
	invited_by = models.ForeignKey(User, related_name="team_invites_sent", on_delete=models.CASCADE)
	status = models.CharField(max_length=20, choices=StatusChoices.choices, default=StatusChoices.PENDING)
	created_at = models.DateTimeField(default=timezone.now)
	responded_at = models.DateTimeField(null=True, blank=True)

	class Meta:
		unique_together = ("team", "email", "status")
		indexes = [models.Index(fields=("team", "email"))]

	def __str__(self):
		return f"Invite {self.email} to {self.team}"

	def mark_accepted(self):
		self.status = self.StatusChoices.ACCEPTED
		self.responded_at = timezone.now()
		self.save(update_fields=["status", "responded_at"])
