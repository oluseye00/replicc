"""
Views for content generation app
"""
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.shortcuts import get_object_or_404
from django.db.models import Q

from .models import (
    ContentGeneration, 
    ContentTemplate, 
    SavedContent, 
    ContentFeedback,
    AIPrompt
)
from .serializers import (
    ContentGenerationSerializer,
    ContentTemplateSerializer,
    SavedContentSerializer,
    ContentFeedbackSerializer,
    AIPromptSerializer
)


class ContentGenerationListCreateView(generics.ListCreateAPIView):
    """List user's content generations or create a new one"""
    serializer_class = ContentGenerationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return ContentGeneration.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ContentGenerationDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a specific content generation"""
    serializer_class = ContentGenerationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return ContentGeneration.objects.filter(user=self.request.user)


class ContentTemplateListView(generics.ListAPIView):
    """List available content templates"""
    serializer_class = ContentTemplateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = ContentTemplate.objects.filter(is_active=True)
        
        # Filter by platform if specified
        platform = self.request.query_params.get('platform', None)
        if platform:
            queryset = queryset.filter(platform=platform)
        
        # Filter by template type if specified
        template_type = self.request.query_params.get('type', None)
        if template_type:
            queryset = queryset.filter(template_type=template_type)
        
        return queryset


class SavedContentListCreateView(generics.ListCreateAPIView):
    """List user's saved content or save new content"""
    serializer_class = SavedContentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return SavedContent.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class SavedContentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete saved content"""
    serializer_class = SavedContentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return SavedContent.objects.filter(user=self.request.user)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def generate_content_ideas(request):
    """Generate content ideas based on topic and parameters"""
    topic = request.data.get('topic')
    if not topic:
        return Response(
            {'error': 'Topic is required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # TODO: Implement AI content idea generation
    # This would call your AI service to generate ideas
    
    sample_ideas = [
        f"5 surprising facts about {topic}",
        f"Common mistakes people make with {topic}",
        f"My personal experience with {topic}",
        f"Behind the scenes of {topic}",
        f"Future predictions for {topic}"
    ]
    
    return Response({'content_ideas': sample_ideas})


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def generate_platform_content(request, generation_id):
    """Generate platform-specific content for an existing content generation"""
    generation = get_object_or_404(
        ContentGeneration, 
        id=generation_id, 
        user=request.user
    )
    
    platform = request.data.get('platform')
    if not platform:
        return Response(
            {'error': 'Platform is required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # TODO: Implement AI platform-specific content generation
    # This would call your AI service with platform-specific prompts
    
    sample_content = {
        'tiktok': f"🎬 {generation.selected_idea}\n\n#fyp #viral #{generation.topic.lower()}",
        'instagram': f"✨ {generation.selected_idea}\n\n.\n.\n.\n#instagram #{generation.topic.lower()}",
        'linkedin': f"Thoughts on {generation.topic}:\n\n{generation.selected_idea}\n\nWhat's your experience?",
        'twitter': [
            f"Thread about {generation.topic} 🧵 1/3",
            f"{generation.selected_idea} 2/3",
            "What do you think? Let me know in the replies! 3/3"
        ],
        'youtube': f"{generation.selected_idea}\n\nIn this video, I explore {generation.topic}..."
    }
    
    content = sample_content.get(platform, f"Generated content for {platform}")
    
    # Update the generation object with the new content
    if platform == 'tiktok':
        generation.tiktok_script = content
    elif platform == 'instagram':
        generation.instagram_caption = content
    elif platform == 'linkedin':
        generation.linkedin_post = content
    elif platform == 'twitter':
        generation.twitter_thread = content
    elif platform == 'youtube':
        generation.youtube_description = content
    
    generation.save()
    
    return Response({
        'platform': platform,
        'content': content,
        'generation_id': str(generation.id)
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_stats(request):
    """Get user's content generation statistics"""
    user_generations = ContentGeneration.objects.filter(user=request.user)
    
    stats = {
        'total_generations': user_generations.count(),
        'completed_generations': user_generations.filter(status='completed').count(),
        'pending_generations': user_generations.filter(status='pending').count(),
        'failed_generations': user_generations.filter(status='failed').count(),
        'total_saved_content': SavedContent.objects.filter(user=request.user).count(),
        'total_tokens_used': sum(gen.tokens_used for gen in user_generations),
        'favorite_platforms': []  # TODO: Calculate from saved content
    }
    
    return Response(stats)