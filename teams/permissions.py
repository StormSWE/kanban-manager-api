from __future__ import annotations

from typing import Iterable

from rest_framework.permissions import BasePermission

from .models import Team, TeamMember


class BaseTeamPermission(BasePermission):
    required_roles: Iterable[str] = tuple()

    def has_object_permission(self, request, view, obj):
        team = obj if isinstance(obj, Team) else getattr(obj, "team", None)
        if team is None:
            return False
        membership = TeamMember.objects.filter(team=team, user=request.user).first()
        if not membership:
            return False
        if not self.required_roles:
            return True
        return membership.role in self.required_roles


class IsTeamMember(BaseTeamPermission):
    required_roles: Iterable[str] = tuple()


class IsTeamAdmin(BaseTeamPermission):
    required_roles = (
        TeamMember.RoleChoices.OWNER,
        TeamMember.RoleChoices.ADMIN,
    )


class IsTeamOwner(BaseTeamPermission):
    required_roles = (TeamMember.RoleChoices.OWNER,)
