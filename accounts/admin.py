"""
Admin configuration for accounts app
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User, UserPreferences, VoiceProfile


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom User admin"""

    list_display = (
        "email",
        "full_name",
        "subscription_tier",
        "subscription_status",
        "monthly_usage",
        "created_at",
    )
    list_filter = (
        "subscription_tier",
        "subscription_status",
        "is_active",
        "is_staff",
        "created_at",
    )
    search_fields = ("email", "full_name", "username")
    ordering = ("-created_at",)

    fieldsets = BaseUserAdmin.fieldsets + (
        ("Profile Info", {"fields": ("full_name", "avatar", "bio", "website")}),
        (
            "Subscription",
            {
                "fields": (
                    "subscription_tier",
                    "subscription_status",
                    "stripe_customer_id",
                )
            },
        ),
        ("Usage Tracking", {"fields": ("monthly_usage", "usage_limit")}),
    )

    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ("Profile Info", {"fields": ("full_name", "email")}),
    )


@admin.register(VoiceProfile)
class VoiceProfileAdmin(admin.ModelAdmin):
    """Voice Profile admin"""

    list_display = ("name", "user", "niche", "is_default", "is_active", "created_at")
    list_filter = ("niche", "is_default", "is_active", "platforms", "created_at")
    search_fields = ("name", "user__email", "user__full_name")
    ordering = ("-created_at",)

    fieldsets = (
        (None, {"fields": ("user", "name", "niche", "is_default", "is_active")}),
        (
            "Content Analysis",
            {"fields": ("sample_posts", "voice_analysis"), "classes": ("collapse",)},
        ),
        ("Platform Settings", {"fields": ("platforms",)}),
    )

    readonly_fields = ("voice_analysis",)


@admin.register(UserPreferences)
class UserPreferencesAdmin(admin.ModelAdmin):
    """User Preferences admin"""

    list_display = (
        "user",
        "preferred_content_length",
        "creativity_level",
        "auto_match_videos",
    )
    list_filter = (
        "preferred_content_length",
        "include_hashtags",
        "include_emojis",
        "auto_match_videos",
    )
    search_fields = ("user__email", "user__full_name")

    fieldsets = (
        (
            "Content Preferences",
            {
                "fields": (
                    "preferred_content_length",
                    "default_platforms",
                    "creativity_level",
                    "include_hashtags",
                    "include_emojis",
                )
            },
        ),
        (
            "Video Preferences",
            {"fields": ("auto_match_videos", "video_style_preference")},
        ),
        ("Notifications", {"fields": ("email_notifications", "marketing_emails")}),
    )
