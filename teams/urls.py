from django.urls import path

from .views import TeamDetailView, TeamListCreateView, TeamMembersView, TransferOwnerView

app_name = "teams"

urlpatterns = [
    path("", TeamListCreateView.as_view(), name="team-list"),
    path("<int:pk>/", TeamDetailView.as_view(), name="team-detail"),
    path("<int:pk>/members/", TeamMembersView.as_view(), name="team-members"),
    path("<int:pk>/transfer-owner/", TransferOwnerView.as_view(), name="team-transfer-owner"),
]
