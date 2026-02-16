"""
Models for video matching system
"""
from django.db import models
from django.conf import settings
import uuid


class VideoAsset(models.Model):
    """User-uploaded video assets for matching with content"""
    
    MOOD_CHOICES = [
        ('energetic', 'Energetic'),
        ('calm', 'Calm'),
        ('serious', 'Serious'),
        ('playful', 'Playful'),
        ('inspirational', 'Inspirational'),
        ('dramatic', 'Dramatic'),
        ('minimal', 'Minimal'),
        ('vibrant', 'Vibrant'),
    ]
    
    PACE_CHOICES = [
        ('slow', 'Slow (0-30 cuts/min)'),
        ('medium', 'Medium (30-60 cuts/min)'),
        ('fast', 'Fast (60+ cuts/min)'),
    ]
    
    STYLE_CHOICES = [
        ('lifestyle', 'Lifestyle'),
        ('tutorial', 'Tutorial/Educational'),
        ('product_demo', 'Product Demo'),
        ('talking_head', 'Talking Head'),
        ('b_roll', 'B-Roll/Cinematic'),
        ('animation', 'Animation/Motion Graphics'),
        ('screen_record', 'Screen Recording'),
        ('testimonial', 'Testimonial'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='video_assets'
    )
    
    # File info
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to='videos/')
    thumbnail = models.ImageField(upload_to='video_thumbnails/', null=True, blank=True)
    
    # Video properties (auto-detected)
    duration_seconds = models.FloatField(null=True, blank=True)
    resolution_width = models.IntegerField(null=True, blank=True)
    resolution_height = models.IntegerField(null=True, blank=True)
    fps = models.FloatField(null=True, blank=True)
    file_size_mb = models.FloatField(null=True, blank=True)
    
    # Style/Tone Analysis (AI-generated)
    mood = models.CharField(max_length=20, choices=MOOD_CHOICES, blank=True)
    pace = models.CharField(max_length=10, choices=PACE_CHOICES, blank=True)
    style = models.CharField(max_length=20, choices=STYLE_CHOICES, blank=True)
    
    # Detailed AI analysis
    visual_analysis = models.JSONField(default=dict, help_text="AI analysis of visual elements")
    audio_analysis = models.JSONField(default=dict, help_text="AI analysis of audio elements")
    scene_analysis = models.JSONField(default=dict, help_text="Scene-by-scene breakdown")
    
    # Tags and categorization
    tags = models.JSONField(default=list)  # ["corporate", "outdoors", "product", etc.]
    suitable_platforms = models.JSONField(default=list)  # ["tiktok", "instagram", etc.]
    
    # Usage tracking
    times_matched = models.IntegerField(default=0)
    last_used = models.DateTimeField(null=True, blank=True)
    
    # Processing status
    is_processed = models.BooleanField(default=False)
    processing_error = models.TextField(blank=True)
    
    # Timestamps
    uploaded_at = models.DateTimeField(auto_now_add=True)
    analyzed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.title}"
    
    @property
    def aspect_ratio(self):
        """Calculate aspect ratio"""
        if self.resolution_width and self.resolution_height:
            return round(self.resolution_width / self.resolution_height, 2)
        return None
    
    @property
    def is_vertical(self):
        """Check if video is vertical (good for TikTok/Instagram)"""
        return self.aspect_ratio and self.aspect_ratio < 1
    
    @property
    def is_square(self):
        """Check if video is square (good for Instagram)"""
        return self.aspect_ratio and 0.9 <= self.aspect_ratio <= 1.1


class ContentVideoMatch(models.Model):
    """Matches between generated content and video assets"""
    
    MATCH_QUALITY = [
        ('excellent', 'Excellent (90-100%)'),
        ('good', 'Good (70-89%)'),
        ('fair', 'Fair (50-69%)'),
        ('poor', 'Poor (0-49%)'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    content_generation = models.ForeignKey(
        'content_generation.ContentGeneration',
        on_delete=models.CASCADE,
        related_name='video_matches'
    )
    video_asset = models.ForeignKey(
        VideoAsset,
        on_delete=models.CASCADE,
        related_name='content_matches'
    )
    
    # Match analysis
    match_score = models.FloatField()  # 0.0 to 1.0
    match_quality = models.CharField(max_length=20, choices=MATCH_QUALITY)
    
    # Why they match (AI reasoning)
    match_reasoning = models.TextField(help_text="AI explanation of why this is a good match")
    
    # Detailed match breakdown
    tone_match_score = models.FloatField(default=0.0)  # How well tones align
    pace_match_score = models.FloatField(default=0.0)  # Content pace vs video pace
    style_match_score = models.FloatField(default=0.0)  # Content style vs video style
    platform_match_score = models.FloatField(default=0.0)  # Platform compatibility
    
    # Specific recommendations
    recommended_platforms = models.JSONField(default=list)
    timing_suggestions = models.JSONField(default=dict)  # When to show text, CTAs, etc.
    editing_suggestions = models.JSONField(default=list)  # How to combine content + video
    
    # User interaction
    user_rating = models.IntegerField(null=True, blank=True)  # 1-5 rating from user
    is_used = models.BooleanField(default=False)
    used_platforms = models.JSONField(default=list)  # Where user actually used it
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    used_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ['content_generation', 'video_asset']
        ordering = ['-match_score']
    
    def __str__(self):
        return f"Match: {self.content_generation.topic[:30]} + {self.video_asset.title[:30]} ({self.match_score:.2f})"


class VideoAnalysisPrompt(models.Model):
    """Prompts for AI video analysis"""
    
    ANALYSIS_TYPES = [
        ('visual_mood', 'Visual Mood Analysis'),
        ('audio_tone', 'Audio Tone Analysis'),
        ('pace_detection', 'Pace Detection'),
        ('style_classification', 'Style Classification'),
        ('scene_breakdown', 'Scene Breakdown'),
        ('content_matching', 'Content Matching'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    analysis_type = models.CharField(max_length=30, choices=ANALYSIS_TYPES)
    
    # Prompt content
    system_prompt = models.TextField()
    user_prompt_template = models.TextField()
    
    # Settings
    is_active = models.BooleanField(default=True)
    version = models.CharField(max_length=10, default='1.0')
    
    # Performance tracking
    usage_count = models.IntegerField(default=0)
    average_accuracy = models.FloatField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['analysis_type', '-version']
    
    def __str__(self):
        return f"{self.analysis_type} - {self.name} v{self.version}"


class MatchingRule(models.Model):
    """Rules for matching content types with video styles"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    description = models.TextField()
    
    # Content criteria
    content_type = models.JSONField(default=list)  # ["educational", "entertaining"]
    content_tone = models.JSONField(default=list)  # ["professional", "casual"]
    target_platforms = models.JSONField(default=list)  # ["tiktok", "linkedin"]
    
    # Video criteria
    preferred_video_styles = models.JSONField(default=list)
    preferred_moods = models.JSONField(default=list)
    preferred_pace = models.JSONField(default=list)
    
    # Matching logic
    weight_tone = models.FloatField(default=0.3)  # How important is tone matching
    weight_pace = models.FloatField(default=0.2)  # How important is pace matching
    weight_style = models.FloatField(default=0.3)  # How important is style matching
    weight_platform = models.FloatField(default=0.2)  # How important is platform matching
    
    # Settings
    is_active = models.BooleanField(default=True)
    min_match_score = models.FloatField(default=0.5)  # Minimum score to suggest
    
    # Usage tracking
    times_applied = models.IntegerField(default=0)
    success_rate = models.FloatField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name


class VideoProcessingQueue(models.Model):
    """Queue for video processing tasks"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('retrying', 'Retrying'),
    ]
    
    TASK_TYPES = [
        ('thumbnail_generation', 'Thumbnail Generation'),
        ('video_analysis', 'Video Analysis'),
        ('audio_extraction', 'Audio Extraction'),
        ('scene_detection', 'Scene Detection'),
        ('content_matching', 'Content Matching'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    video_asset = models.ForeignKey(
        VideoAsset,
        on_delete=models.CASCADE,
        related_name='processing_tasks'
    )
    
    # Task info
    task_type = models.CharField(max_length=30, choices=TASK_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Processing details
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    processing_time_seconds = models.FloatField(null=True, blank=True)
    
    # Results and errors
    result_data = models.JSONField(default=dict)
    error_message = models.TextField(blank=True)
    retry_count = models.IntegerField(default=0)
    max_retries = models.IntegerField(default=3)
    
    # Priority
    priority = models.IntegerField(default=5)  # 1 = highest, 10 = lowest
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['priority', 'created_at']
    
    def __str__(self):
        return f"{self.video_asset.title} - {self.task_type} ({self.status})"