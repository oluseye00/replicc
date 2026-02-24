"""
Serializers for content generation app
"""
from rest_framework import serializers

from .models import (
    AIPrompt,
    ContentFeedback,
    ContentGeneration,
    ContentTemplate,
    SavedContent,
)


class ContentGenerationSerializer(serializers.ModelSerializer):
    """Serializer for ContentGeneration model"""

    class Meta:
        model = ContentGeneration
        fields = [
            "id",
            "user",
            "voice_profile",
            "topic",
            "additional_context",
            "target_platforms",
            "creativity_level",
            "include_hashtags",
            "include_emojis",
            "content_length",
            "content_ideas",
            "selected_idea",
            "tiktok_script",
            "instagram_caption",
            "linkedin_post",
            "twitter_thread",
            "youtube_description",
            "status",
            "generation_time_seconds",
            "tokens_used",
            "created_at",
            "updated_at",
            "completed_at",
            "has_platform_content",
        ]
        read_only_fields = [
            "id",
            "user",
            "status",
            "generation_time_seconds",
            "tokens_used",
            "created_at",
            "updated_at",
            "completed_at",
            "has_platform_content",
        ]


class ContentTemplateSerializer(serializers.ModelSerializer):
    """Serializer for ContentTemplate model"""

    class Meta:
        model = ContentTemplate
        fields = [
            "id",
            "name",
            "template_type",
            "platform",
            "prompt_template",
            "example_output",
            "is_active",
            "is_premium",
            "usage_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "usage_count", "created_at", "updated_at"]


class SavedContentSerializer(serializers.ModelSerializer):
    """Serializer for SavedContent model"""

    content_generation = ContentGenerationSerializer(read_only=True)
    content_generation_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = SavedContent
        fields = [
            "id",
            "user",
            "content_generation",
            "content_generation_id",
            "saved_platforms",
            "notes",
            "tags",
            "is_favorite",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "user", "created_at", "updated_at"]


class ContentFeedbackSerializer(serializers.ModelSerializer):
    """Serializer for ContentFeedback model"""

    content_generation_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = ContentFeedback
        fields = [
            "id",
            "user",
            "content_generation_id",
            "overall_rating",
            "creativity_rating",
            "relevance_rating",
            "voice_match_rating",
            "comments",
            "improvement_suggestions",
            "platforms_used",
            "content_modified",
            "created_at",
        ]
        read_only_fields = ["id", "user", "created_at"]


class AIPromptSerializer(serializers.ModelSerializer):
    """Serializer for AIPrompt model"""

    class Meta:
        model = AIPrompt
        fields = [
            "id",
            "name",
            "prompt_type",
            "system_prompt",
            "user_prompt_template",
            "is_active",
            "version",
            "usage_count",
            "average_rating",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "usage_count",
            "average_rating",
            "created_at",
            "updated_at",
        ]
