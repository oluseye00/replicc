"""
URL patterns for accounts app
"""
from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Authentication
    path('register/', views.UserRegistrationView.as_view(), name='register'),
    path('login/', views.UserLoginView.as_view(), name='login'),
    
    # Profile Management
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('preferences/', views.UserPreferencesView.as_view(), name='preferences'),
    path('change-password/', views.change_password, name='change-password'),
    path('stats/', views.user_stats, name='user-stats'),
    
    # Voice Profiles
    path('voice-profiles/', views.VoiceProfileListCreateView.as_view(), name='voice-profiles'),
    path('voice-profiles/<uuid:pk>/', views.VoiceProfileDetailView.as_view(), name='voice-profile-detail'),
    path('voice-profiles/<uuid:profile_id>/set-default/', views.set_default_voice_profile, name='set-default-voice-profile'),
]