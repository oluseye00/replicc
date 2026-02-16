"""
Views for accounts app
"""
from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, login
from drf_spectacular.utils import extend_schema
from .models import User, VoiceProfile, UserPreferences
from .serializers import (
    UserSerializer, UserRegistrationSerializer, UserLoginSerializer,
    VoiceProfileSerializer, UserPreferencesSerializer, PasswordChangeSerializer
)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """Get and update user profile"""
    
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user


class UserRegistrationView(generics.CreateAPIView):
    """User registration endpoint"""
    
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]
    
    @extend_schema(
        summary="Register a new user",
        description="Create a new user account with email and password",
    )
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'user': UserSerializer(user).data,
                'tokens': {
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                }
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(generics.GenericAPIView):
    """User login endpoint"""
    
    serializer_class = UserLoginSerializer
    permission_classes = [permissions.AllowAny]
    
    @extend_schema(
        summary="Login user",
        description="Authenticate user and return JWT tokens",
    )
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'user': UserSerializer(user).data,
                'tokens': {
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                }
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VoiceProfileListCreateView(generics.ListCreateAPIView):
    """List and create voice profiles"""
    
    serializer_class = VoiceProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return VoiceProfile.objects.filter(user=self.request.user, is_active=True)
    
    @extend_schema(
        summary="Create voice profile",
        description="Create a new voice profile based on sample content",
    )
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            voice_profile = serializer.save()
            
            # TODO: Trigger AI analysis of sample posts
            # This would be handled by a Celery task
            # analyze_voice_profile.delay(voice_profile.id)
            
            return Response(
                VoiceProfileSerializer(voice_profile).data,
                status=status.HTTP_201_CREATED
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VoiceProfileDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, delete voice profile"""
    
    serializer_class = VoiceProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return VoiceProfile.objects.filter(user=self.request.user)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # Prevent deletion of the last voice profile
        user_profiles_count = VoiceProfile.objects.filter(
            user=request.user, is_active=True
        ).count()
        
        if user_profiles_count <= 1:
            return Response(
                {'error': 'You must have at least one voice profile'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # If deleting default profile, set another as default
        if instance.is_default:
            other_profile = VoiceProfile.objects.filter(
                user=request.user, is_active=True
            ).exclude(pk=instance.pk).first()
            
            if other_profile:
                other_profile.is_default = True
                other_profile.save()
        
        instance.is_active = False
        instance.save()
        
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserPreferencesView(generics.RetrieveUpdateAPIView):
    """Get and update user preferences"""
    
    serializer_class = UserPreferencesSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        preferences, created = UserPreferences.objects.get_or_create(
            user=self.request.user
        )
        return preferences


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
@extend_schema(
    summary="Change password",
    description="Change user password",
    request=PasswordChangeSerializer,
)
def change_password(request):
    """Change user password"""
    serializer = PasswordChangeSerializer(
        data=request.data,
        context={'request': request}
    )
    
    if serializer.is_valid():
        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        return Response({'message': 'Password changed successfully'})
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
@extend_schema(
    summary="Get user statistics",
    description="Get user usage statistics and limits",
)
def user_stats(request):
    """Get user statistics"""
    user = request.user
    
    # Get voice profiles count
    voice_profiles_count = VoiceProfile.objects.filter(
        user=user, is_active=True
    ).count()
    
    # TODO: Get content generations count for this month
    # This would come from the content_generation app
    
    stats = {
        'subscription_tier': user.subscription_tier,
        'monthly_usage': user.monthly_usage,
        'usage_limit': user.usage_limit,
        'usage_percentage': user.usage_percentage,
        'can_generate_content': user.can_generate_content,
        'voice_profiles_count': voice_profiles_count,
        # 'content_generations_count': content_generations_count,
    }
    
    return Response(stats)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
@extend_schema(
    summary="Set default voice profile",
    description="Set a voice profile as the default one",
)
def set_default_voice_profile(request, profile_id):
    """Set default voice profile"""
    try:
        voice_profile = VoiceProfile.objects.get(
            id=profile_id,
            user=request.user,
            is_active=True
        )
        
        # Remove default from other profiles
        VoiceProfile.objects.filter(
            user=request.user,
            is_default=True
        ).update(is_default=False)
        
        # Set as default
        voice_profile.is_default = True
        voice_profile.save()
        
        return Response({'message': 'Default voice profile updated'})
        
    except VoiceProfile.DoesNotExist:
        return Response(
            {'error': 'Voice profile not found'},
            status=status.HTTP_404_NOT_FOUND
        )