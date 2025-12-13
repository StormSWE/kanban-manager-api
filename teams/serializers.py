from __future__ import annotations

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from .models import Team, TeamInvite, TeamMember
from .services import add_team_member, create_team_invite

User = get_user_model()


class BasicUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email", "name")


class TeamMemberSerializer(serializers.ModelSerializer):
    user = BasicUserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), source="user", write_only=True)

    class Meta:
        model = TeamMember
        fields = ("id", "user", "user_id", "role", "joined_at")
        read_only_fields = ("id", "user", "joined_at")

    def create(self, validated_data):
        team = self.context["team"]
        return add_team_member(team=team, **validated_data)


class TeamSerializer(serializers.ModelSerializer):
    created_by = BasicUserSerializer(read_only=True)
    members = TeamMemberSerializer(many=True, read_only=True)
    members_count = serializers.SerializerMethodField()

    class Meta:
        model = Team
        fields = (
            "id",
            "name",
            "description",
            "created_by",
            "created_at",
            "updated_at",
            "members",
            "members_count",
        )
        read_only_fields = ("id", "created_by", "created_at", "updated_at", "members", "members_count")

    def get_members_count(self, obj):
        return obj.members.count()


class InviteSerializer(serializers.ModelSerializer):
    role = serializers.ChoiceField(
        choices=TeamMember.RoleChoices.choices,
        default=TeamMember.RoleChoices.MEMBER,
    )

    class Meta:
        model = TeamInvite
        fields = ("email", "role")

    def create(self, validated_data):
        team = self.context["team"]
        invited_by = self.context["request"].user
        try:
            return create_team_invite(team=team, invited_by=invited_by, **validated_data)
        except DjangoValidationError as exc:
            raise serializers.ValidationError(exc.message or str(exc)) from exc
