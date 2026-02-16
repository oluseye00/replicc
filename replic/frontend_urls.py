"""
URL patterns for the frontend web interface
"""
from django.urls import path
from . import frontend_views

app_name = 'frontend'

urlpatterns = [
    # Main pages
    path('', frontend_views.index, name='index'),
    path('dashboard/', frontend_views.dashboard, name='dashboard'),
    path('create/', frontend_views.create_content, name='create'),
    
    # Authentication
    path('login/', frontend_views.login_view, name='login'),
    path('register/', frontend_views.register_view, name='register'),
    
    # Content management
    path('videos/', frontend_views.videos_view, name='videos'),
    path('content/', frontend_views.content_library_view, name='content_library'),
    
    # Info pages
    path('pricing/', frontend_views.pricing_view, name='pricing'),
    path('help/', frontend_views.help_view, name='help'),
]