from django.urls import path
from .views import ProjectActivityListView

app_name = "activity"

urlpatterns = [
    path("projects/<int:project_pk>/", ProjectActivityListView.as_view(), name="project-activity"),
]
