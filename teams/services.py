from __future__ import annotations

from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction

from .models import Team, TeamInvite, TeamMember

User = get_user_model()


def add_team_member(*, team, user, role: str = TeamMember.RoleChoices.MEMBER):
    membership, created = TeamMember.objects.get_or_create(
        team=team,
        user=user,
        defaults={"role": role},
    )
    if not created and membership.role != role:
        membership.role = role
        membership.save(update_fields=["role"])
    return membership


def remove_team_member(*, team, user) -> None:
    try:
        membership = TeamMember.objects.get(team=team, user=user)
    except TeamMember.DoesNotExist as exc:
        raise ValidationError("User is not a member of this team.") from exc

    if membership.role == TeamMember.RoleChoices.OWNER:
        owners = TeamMember.objects.filter(team=team, role=TeamMember.RoleChoices.OWNER).count()
        if owners <= 1:
            raise ValidationError("Cannot remove the last team owner.")

    membership.delete()


def transfer_team_owner(*, team, acting_user, new_owner):
    try:
        acting_membership = TeamMember.objects.get(team=team, user=acting_user)
    except TeamMember.DoesNotExist as exc:
        raise PermissionDenied("You are not part of this team.") from exc

    if acting_membership.role != TeamMember.RoleChoices.OWNER:
        raise PermissionDenied("Only owners can transfer ownership.")

    new_membership, _ = TeamMember.objects.get_or_create(team=team, user=new_owner)
    with transaction.atomic():
        TeamMember.objects.filter(team=team, role=TeamMember.RoleChoices.OWNER).exclude(user=new_owner).update(
            role=TeamMember.RoleChoices.ADMIN,
        )
        new_membership.role = TeamMember.RoleChoices.OWNER
        new_membership.save(update_fields=["role"])
        team.created_by = new_owner
        team.save(update_fields=["created_by"])
    return new_membership


def create_team_invite(*, team, email: str, invited_by, role: str):
    if TeamMember.objects.filter(team=team, user__email=email).exists():
        raise ValidationError("User already belongs to this team.")

    invite, created = TeamInvite.objects.get_or_create(
        team=team,
        email=email,
        status=TeamInvite.StatusChoices.PENDING,
        defaults={"role": role, "invited_by": invited_by},
    )
    if not created:
        invite.role = role
        invite.invited_by = invited_by
        invite.save(update_fields=["role", "invited_by"])
    return invite
