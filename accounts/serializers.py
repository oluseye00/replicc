"""
Serializers for accounts app
"""
from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, VoiceProfile, UserPreferences


class UserSerializer(serializers.ModelSerializer):
    """User serializer for profile management"""
    
    usage_percentage = serializers.ReadOnlyField()
    can_generate_content = serializers.ReadOnlyField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'full_name', 'avatar', 'bio', 'website',
            'subscription_tier', 'subscription_status', 'monthly_usage', 'usage_limit',
            'usage_percentage', 'can_generate_content', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'subscription_tier', 'subscription_status', 'monthly_usage',
            'usage_limit', 'created_at', 'updated_at'
        ]


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['email', 'username', 'full_name', 'password', 'password_confirm']
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        
        # Create default voice profile and preferences
        VoiceProfile.objects.create(
            user=user,
            name="Default Voice",
            is_default=True
        )
        UserPreferences.objects.create(user=user)
        
        return user


class UserLoginSerializer(serializers.Serializer):
    """Serializer for user login"""
    
    email = serializers.EmailField()
    password = serializers.CharField()
    
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            user = authenticate(username=email, password=password)
            if not user:
                raise serializers.ValidationError('Invalid credentials')
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled')
            attrs['user'] = user
        else:
            raise serializers.ValidationError('Must include email and password')
        
        return attrs


class VoiceProfileSerializer(serializers.ModelSerializer):
    """Voice Profile serializer"""
    
    class Meta:
        model = VoiceProfile
        fields = [
            'id', 'name', 'sample_posts', 'voice_analysis', 'platforms',
            'niche', 'is_default', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'voice_analysis', 'created_at', 'updated_at']
    
    def validate_sample_posts(self, value):
        """Validate sample posts"""
        if not isinstance(value, list):
            raise serializers.ValidationError("Sample posts must be a list")
        
        if len(value) < 3:
            raise serializers.ValidationError("Please provide at least 3 sample posts")
        
        if len(value) > 20:
            raise serializers.ValidationError("Maximum 20 sample posts allowed")
        
        # Check each post length
        for post in value:
            if not isinstance(post, str):
                raise serializers.ValidationError("Each sample post must be a string")
            if len(post) < 10:
                raise serializers.ValidationError("Each sample post must be at least 10 characters")
            if len(post) > 2000:
                raise serializers.ValidationError("Each sample post must be less than 2000 characters")
        
        return value
    
    def create(self, validated_data):
        """Create voice profile and trigger AI analysis"""
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class UserPreferencesSerializer(serializers.ModelSerializer):
    """User Preferences serializer"""
    
    class Meta:
        model = UserPreferences
        fields = [
            'preferred_content_length', 'default_platforms', 'creativity_level',
            'include_hashtags', 'include_emojis', 'email_notifications',
            'marketing_emails', 'auto_match_videos', 'video_style_preference'
        ]
    
    def validate_creativity_level(self, value):
        """Validate creativity level is between 1-10"""
        if value < 1 or value > 10:
            raise serializers.ValidationError("Creativity level must be between 1 and 10")
        return value
    
    def validate_default_platforms(self, value):
        """Validate default platforms"""
        if not isinstance(value, list):
            raise serializers.ValidationError("Default platforms must be a list")
        
        valid_platforms = ['tiktok', 'instagram', 'linkedin', 'twitter', 'youtube']
        for platform in value:
            if platform not in valid_platforms:
                raise serializers.ValidationError(f"Invalid platform: {platform}")
        
        return value


class PasswordChangeSerializer(serializers.Serializer):
    """Serializer for changing password"""
    
    old_password = serializers.CharField()
    new_password = serializers.CharField(min_length=8)
    new_password_confirm = serializers.CharField()
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("New passwords don't match")
        return attrs
    
    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect")
        return value