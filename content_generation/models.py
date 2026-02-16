"""
Models for content generation
"""
from django.db import models
from django.conf import settings
import uuid


class ContentGeneration(models.Model):
    """Main model for content generations"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='content_generations'
    )
    voice_profile = models.ForeignKey(
        'accounts.VoiceProfile', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    
    # Input
    topic = models.TextField(help_text="The topic or subject for content generation")
    additional_context = models.TextField(blank=True, help_text="Additional context or requirements")
    target_platforms = models.JSONField(default=list)  # ["tiktok", "instagram", etc.]
    
    # AI Generation Settings
    creativity_level = models.IntegerField(default=7)  # 1-10 scale
    include_hashtags = models.BooleanField(default=True)
    include_emojis = models.BooleanField(default=True)
    content_length = models.CharField(
        max_length=20,
        choices=[
            ('short', 'Short'),
            ('medium', 'Medium'),
            ('long', 'Long'),
        ],
        default='medium'
    )
    
    # Generated Content
    content_ideas = models.JSONField(default=list)  # Array of content ideas generated
    selected_idea = models.TextField(blank=True)  # The idea user selected
    
    # Platform-specific content
    tiktok_script = models.TextField(blank=True)
    instagram_caption = models.TextField(blank=True)
    linkedin_post = models.TextField(blank=True)
    twitter_thread = models.JSONField(default=list)  # Array of tweets
    youtube_description = models.TextField(blank=True)
    
    # Metadata
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    generation_time_seconds = models.FloatField(null=True, blank=True)
    tokens_used = models.IntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.topic[:50]}"
    
    @property
    def has_platform_content(self):
        """Check if any platform-specific content exists"""
        return any([
            self.tiktok_script,
            self.instagram_caption,
            self.linkedin_post,
            self.twitter_thread,
            self.youtube_description,
        ])


class ContentTemplate(models.Model):
    """Templates for different types of content"""
    
    TEMPLATE_TYPES = [
        ('educational', 'Educational'),
        ('entertaining', 'Entertaining'),
        ('promotional', 'Promotional'),
        ('inspirational', 'Inspirational'),
        ('tutorial', 'Tutorial'),
        ('story', 'Story/Narrative'),
        ('news', 'News/Update'),
        ('question', 'Question/Poll'),
    ]
    
    PLATFORMS = [
        ('tiktok', 'TikTok'),
        ('instagram', 'Instagram'),
        ('linkedin', 'LinkedIn'),
        ('twitter', 'Twitter/X'),
        ('youtube', 'YouTube'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    template_type = models.CharField(max_length=20, choices=TEMPLATE_TYPES)
    platform = models.CharField(max_length=20, choices=PLATFORMS)
    
    # Template Content
    prompt_template = models.TextField(
        help_text="Template with placeholders like {topic}, {tone}, etc."
    )
    example_output = models.TextField(
        blank=True,
        help_text="Example of what this template produces"
    )
    
    # Settings
    is_active = models.BooleanField(default=True)
    is_premium = models.BooleanField(default=False)  # Only for paid users
    
    # Usage tracking
    usage_count = models.IntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['platform', 'template_type', 'name']
    
    def __str__(self):
        return f"{self.platform} - {self.template_type} - {self.name}"


class SavedContent(models.Model):
    """User's saved/favorite generated content"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='saved_content'
    )
    content_generation = models.ForeignKey(
        ContentGeneration, 
        on_delete=models.CASCADE,
        related_name='saves'
    )
    
    # What content was saved
    saved_platforms = models.JSONField(default=list)  # ["tiktok", "instagram"]
    notes = models.TextField(blank=True)
    
    # Organization
    tags = models.JSONField(default=list)  # ["funny", "product launch", etc.]
    is_favorite = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'content_generation']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email} saved content from {self.content_generation.created_at}"


class ContentFeedback(models.Model):
    """User feedback on generated content"""
    
    RATING_CHOICES = [
        (1, '1 - Poor'),
        (2, '2 - Below Average'),
        (3, '3 - Average'),
        (4, '4 - Good'),
        (5, '5 - Excellent'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='content_feedback'
    )
    content_generation = models.OneToOneField(
        ContentGeneration, 
        on_delete=models.CASCADE,
        related_name='feedback'
    )
    
    # Ratings (1-5 scale)
    overall_rating = models.IntegerField(choices=RATING_CHOICES)
    creativity_rating = models.IntegerField(choices=RATING_CHOICES, null=True, blank=True)
    relevance_rating = models.IntegerField(choices=RATING_CHOICES, null=True, blank=True)
    voice_match_rating = models.IntegerField(choices=RATING_CHOICES, null=True, blank=True)
    
    # Text feedback
    comments = models.TextField(blank=True)
    improvement_suggestions = models.TextField(blank=True)
    
    # What did they use?
    platforms_used = models.JSONField(default=list)
    content_modified = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Feedback from {self.user.email} - {self.overall_rating}/5"


class AIPrompt(models.Model):
    """Store and version AI prompts for content generation"""
    
    PROMPT_TYPES = [
        ('content_ideas', 'Content Ideas Generation'),
        ('tiktok_script', 'TikTok Script'),
        ('instagram_caption', 'Instagram Caption'),
        ('linkedin_post', 'LinkedIn Post'),
        ('twitter_thread', 'Twitter Thread'),
        ('youtube_description', 'YouTube Description'),
        ('voice_analysis', 'Voice Profile Analysis'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    prompt_type = models.CharField(max_length=30, choices=PROMPT_TYPES)
    
    # Prompt Content
    system_prompt = models.TextField(
        help_text="System message that sets the AI's role and behavior"
    )
    user_prompt_template = models.TextField(
        help_text="Template for user message with placeholders"
    )
    
    # Settings
    is_active = models.BooleanField(default=True)
    version = models.CharField(max_length=10, default='1.0')
    
    # Performance tracking
    usage_count = models.IntegerField(default=0)
    average_rating = models.FloatField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['prompt_type', '-version']
    
    def __str__(self):
        return f"{self.prompt_type} - {self.name} v{self.version}"