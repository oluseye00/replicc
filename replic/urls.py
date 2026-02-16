"""
URL Configuration for Repli
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from . import views, icon_views

urlpatterns = [
    # Mobile App Routes
    path('', views.mobile_index, name='mobile_home'),
    path('app/', views.mobile_app, name='mobile_app'),
    path('onboarding/', views.mobile_onboarding, name='mobile_onboarding'),
    path('create/', views.mobile_create, name='mobile_create'),
    path('library/', views.mobile_library, name='mobile_library'),
    path('profile/', views.mobile_profile, name='mobile_profile'),
    path('simulator/', views.mobile_simulator, name='mobile_simulator'),
    path('mobile-api/', views.mobile_api, name='mobile_api'),
    
    # Dynamic mobile icons
    path('static/mobile/icons/<str:size>', icon_views.mobile_icon, name='mobile_icon'),
    path('static/mobile/icons/<str:icon_type>', icon_views.shortcut_icon, name='shortcut_icon'),
    
    # Admin
    path('admin/', admin.site.urls),
    
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # Authentication
    path('api/auth/', include('dj_rest_auth.urls')),
    path('api/auth/registration/', include('dj_rest_auth.registration.urls')),
    
    # App URLs
    path('api/accounts/', include('accounts.urls')),
    path('api/content/', include('content_generation.urls')),
    path('api/video/', include('video_matching.urls')),
    # path('api/payments/', include('payments.urls')),  # Not yet implemented
    # path('api/analytics/', include('analytics.urls')),  # Not yet implemented
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Add debug toolbar URLs in development
if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns