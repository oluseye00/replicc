"""
User models for Repli platform
"""
import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom User model with additional fields for Repli"""

    SUBSCRIPTION_TIERS = [
        ("free", "Free"),
        ("starter", "Starter"),
        ("creator", "Creator"),
        ("team", "Team"),
    ]

    SUBSCRIPTION_STATUS = [
        ("active", "Active"),
        ("inactive", "Inactive"),
        ("cancelled", "Cancelled"),
        ("past_due", "Past Due"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    full_name = models.CharField(max_length=255, blank=True)
    avatar = models.ImageField(upload_to="avatars/", null=True, blank=True)
    bio = models.TextField(blank=True, max_length=500)
    website = models.URLField(blank=True)

    # Subscription Info
    subscription_tier = models.CharField(
        max_length=20, choices=SUBSCRIPTION_TIERS, default="free"
    )
    subscription_status = models.CharField(
        max_length=20, choices=SUBSCRIPTION_STATUS, default="inactive"
    )
    stripe_customer_id = models.CharField(max_length=255, blank=True, null=True)

    # Usage Tracking
    monthly_usage = models.IntegerField(default=0)
    usage_limit = models.IntegerField(default=10)  # Free tier gets 10 generations

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.email or self.username

    @property
    def can_generate_content(self):
        """Check if user can generate more content based on their plan"""
        return self.monthly_usage < self.usage_limit

    @property
    def usage_percentage(self):
        """Calculate usage percentage"""
        if self.usage_limit == 0:
            return 0
        return (self.monthly_usage / self.usage_limit) * 100

    def reset_monthly_usage(self):
        """Reset monthly usage counter (called by Celery task)"""
        self.monthly_usage = 0
        self.save(update_fields=["monthly_usage"])


class VoiceProfile(models.Model):
    """User's voice profile based on sample content"""

    PLATFORMS = [
        ("tiktok", "TikTok"),
        ("instagram", "Instagram"),
        ("linkedin", "LinkedIn"),
        ("twitter", "Twitter/X"),
        ("youtube", "YouTube"),
    ]

    NICHES = [
        ("lifestyle", "Lifestyle"),
        ("business", "Business"),
        ("tech", "Technology"),
        ("fitness", "Fitness"),
        ("food", "Food"),
        ("travel", "Travel"),
        ("fashion", "Fashion"),
        ("education", "Education"),
        ("entertainment", "Entertainment"),
        ("other", "Other"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="voice_profiles"
    )
    name = models.CharField(max_length=100)  # e.g., "Business Voice", "Casual Voice"

    # Sample content for voice analysis
    sample_posts = models.JSONField(default=list)  # Array of sample posts

    # AI-analyzed voice characteristics
    voice_analysis = models.JSONField(default=dict)  # Tone, style, etc.

    # Target platforms for this voice
    platforms = models.JSONField(default=list)  # Array of platform choices
    niche = models.CharField(max_length=50, choices=NICHES, blank=True)

    # Settings
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.email} - {self.name}"

    def save(self, *args, **kwargs):
        # Ensure only one default voice profile per user
        if self.is_default:
            VoiceProfile.objects.filter(user=self.user, is_default=True).exclude(
                pk=self.pk
            ).update(is_default=False)
        super().save(*args, **kwargs)


class UserPreferences(models.Model):
    """User preferences and settings"""

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="preferences"
    )

    # Content Preferences
    preferred_content_length = models.CharField(
        max_length=20,
        choices=[
            ("short", "Short (Twitter-style)"),
            ("medium", "Medium (Instagram-style)"),
            ("long", "Long-form (LinkedIn-style)"),
        ],
        default="medium",
    )

    # Platform Preferences
    default_platforms = models.JSONField(default=list)  # ["tiktok", "instagram"]

    # AI Preferences
    creativity_level = models.IntegerField(default=7)  # 1-10 scale
    include_hashtags = models.BooleanField(default=True)
    include_emojis = models.BooleanField(default=True)

    # Notification Preferences
    email_notifications = models.BooleanField(default=True)
    marketing_emails = models.BooleanField(default=False)

    # Video Matching Preferences
    auto_match_videos = models.BooleanField(default=True)
    video_style_preference = models.CharField(
        max_length=20,
        choices=[
            ("dynamic", "Dynamic/Fast-paced"),
            ("calm", "Calm/Slow-paced"),
            ("mixed", "Mixed"),
        ],
        default="mixed",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Preferences for {self.user.email}"
