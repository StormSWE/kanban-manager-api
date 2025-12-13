from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError as DjangoValidationError
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Team, TeamMember
from .permissions import IsTeamAdmin, IsTeamMember, IsTeamOwner
from .serializers import InviteSerializer, TeamMemberSerializer, TeamSerializer
from .services import add_team_member, remove_team_member, transfer_team_owner

User = get_user_model()


class TeamListCreateView(generics.ListCreateAPIView):
    serializer_class = TeamSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return (
            Team.objects.filter(members__user=self.request.user)
            .distinct()
            .prefetch_related("members__user")
        )

    def perform_create(self, serializer):
        team = serializer.save(created_by=self.request.user)
        add_team_member(team=team, user=self.request.user, role=TeamMember.RoleChoices.OWNER)


class TeamDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TeamSerializer

    def get_queryset(self):
        return (
            Team.objects.filter(members__user=self.request.user)
            .distinct()
            .prefetch_related("members__user")
        )

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            permission_classes = (permissions.IsAuthenticated, IsTeamMember)
        else:
            permission_classes = (permissions.IsAuthenticated, IsTeamOwner)
        return [permission() for permission in permission_classes]


class TeamMembersView(APIView):
	permission_classes = (permissions.IsAuthenticated,)

	def get_permissions(self):
		if self.request.method == "GET":
			permission_classes = (permissions.IsAuthenticated, IsTeamMember)
		else:
			permission_classes = (permissions.IsAuthenticated, IsTeamAdmin)
		return [permission() for permission in permission_classes]

	def get_team(self, request, team_id):
		team = get_object_or_404(Team, pk=team_id)
		self.check_object_permissions(request, team)
		return team

	def get(self, request, pk):
		team = self.get_team(request, pk)
		serializer = TeamMemberSerializer(
			team.members.select_related("user"),
			many=True,
			context={"request": request},
		)
		return Response(serializer.data)

	def post(self, request, pk):
		team = self.get_team(request, pk)
		if "email" in request.data:
			serializer = InviteSerializer(data=request.data, context={"team": team, "request": request})
			serializer.is_valid(raise_exception=True)
			invite = serializer.save()
			return Response({"detail": "Invite created", "token": invite.token}, status=status.HTTP_201_CREATED)

		serializer = TeamMemberSerializer(data=request.data, context={"team": team})
		serializer.is_valid(raise_exception=True)
		membership = serializer.save()
		output = TeamMemberSerializer(membership, context={"request": request}).data
		return Response(output, status=status.HTTP_201_CREATED)

	def delete(self, request, pk):
		team = self.get_team(request, pk)
		user_id = request.data.get("user_id") or request.query_params.get("user_id")
		if not user_id:
			raise ValidationError({"user_id": "This field is required."})
		user = get_object_or_404(User, pk=user_id)
		try:
			remove_team_member(team=team, user=user)
		except DjangoValidationError as exc:
			raise ValidationError(exc.message or str(exc)) from exc
		return Response(status=status.HTTP_204_NO_CONTENT)


class TransferOwnerView(APIView):
	permission_classes = (permissions.IsAuthenticated,)

	def post(self, request, pk):
		team = get_object_or_404(Team, pk=pk)
		self.check_object_permissions(request, team)
		membership = TeamMember.objects.filter(team=team, user=request.user, role=TeamMember.RoleChoices.OWNER).first()
		if not membership:
			raise PermissionDenied("Only owners can transfer ownership.")

		new_owner_id = request.data.get("new_owner_id")
		if not new_owner_id:
			raise ValidationError({"new_owner_id": "This field is required."})
		new_owner = get_object_or_404(User, pk=new_owner_id)
		try:
			updated_membership = transfer_team_owner(team=team, acting_user=request.user, new_owner=new_owner)
		except DjangoValidationError as exc:
			raise ValidationError(exc.message or str(exc)) from exc
		return Response(
			TeamMemberSerializer(updated_membership, context={"request": request}).data,
			status=status.HTTP_200_OK,
		)

	def get_permissions(self):
		permission_classes = (permissions.IsAuthenticated, IsTeamOwner)
		return [permission() for permission in permission_classes]
