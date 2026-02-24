"""
URL Configuration for Content Generation app
"""
from django.urls import path

from . import views

app_name = "content_generation"

urlpatterns = [
    # Content Generation CRUD
    path(
        "", views.ContentGenerationListCreateView.as_view(), name="content-list-create"
    ),
    path(
        "<uuid:pk>/", views.ContentGenerationDetailView.as_view(), name="content-detail"
    ),
    # Content Templates
    path("templates/", views.ContentTemplateListView.as_view(), name="template-list"),
    # Saved Content
    path(
        "saved/", views.SavedContentListCreateView.as_view(), name="saved-list-create"
    ),
    path(
        "saved/<uuid:pk>/", views.SavedContentDetailView.as_view(), name="saved-detail"
    ),
    # AI Generation Endpoints
    path("generate/ideas/", views.generate_content_ideas, name="generate-ideas"),
    path(
        "<uuid:generation_id>/generate/<str:platform>/",
        views.generate_platform_content,
        name="generate-platform",
    ),
    # User Statistics
    path("stats/", views.user_stats, name="user-stats"),
]
