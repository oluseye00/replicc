"""
Video analysis and matching services
"""
import cv2
import numpy as np
from moviepy.editor import VideoFileClip
from PIL import Image
import json
from typing import Dict, List, Tuple, Optional
from django.conf import settings
from .models import VideoAsset, ContentVideoMatch, MatchingRule
import anthropic


class VideoAnalyzer:
    """Analyze video content for style, tone, and characteristics"""
    
    def __init__(self):
        self.anthropic_client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    
    def analyze_video(self, video_asset: VideoAsset) -> Dict:
        """Complete video analysis pipeline"""
        try:
            results = {}
            
            # 1. Extract basic video properties
            results['properties'] = self._extract_video_properties(video_asset)
            
            # 2. Generate thumbnail
            results['thumbnail'] = self._generate_thumbnail(video_asset)
            
            # 3. Analyze visual elements
            results['visual'] = self._analyze_visual_elements(video_asset)
            
            # 4. Analyze audio (if present)
            results['audio'] = self._analyze_audio_elements(video_asset)
            
            # 5. Detect scenes and pace
            results['scenes'] = self._analyze_scenes_and_pace(video_asset)
            
            # 6. AI-powered style/mood analysis
            results['ai_analysis'] = self._ai_style_analysis(video_asset, results)
            
            # Update the video asset with results
            video_asset.visual_analysis = results['visual']
            video_asset.audio_analysis = results['audio']
            video_asset.scene_analysis = results['scenes']
            video_asset.is_processed = True
            video_asset.save()
            
            return results
            
        except Exception as e:
            video_asset.processing_error = str(e)
            video_asset.save()
            raise
    
    def _extract_video_properties(self, video_asset: VideoAsset) -> Dict:
        """Extract basic video properties using moviepy"""
        try:
            with VideoFileClip(video_asset.file.path) as clip:
                return {
                    'duration': clip.duration,
                    'fps': clip.fps,
                    'size': clip.size,
                    'aspect_ratio': clip.w / clip.h if clip.h > 0 else 1,
                    'has_audio': clip.audio is not None,
                }
        except Exception as e:
            return {'error': str(e)}
    
    def _generate_thumbnail(self, video_asset: VideoAsset) -> str:
        """Generate thumbnail at 25% of video duration"""
        try:
            with VideoFileClip(video_asset.file.path) as clip:
                # Take frame at 25% of duration
                thumbnail_time = clip.duration * 0.25
                frame = clip.get_frame(thumbnail_time)
                
                # Convert to PIL Image and save
                thumbnail_image = Image.fromarray(frame)
                thumbnail_path = f"video_thumbnails/{video_asset.id}_thumb.jpg"
                
                # Save thumbnail (you'd implement the actual file saving logic)
                # thumbnail_image.save(f"media/{thumbnail_path}")
                
                return thumbnail_path
        except Exception as e:
            return f"Error generating thumbnail: {str(e)}"
    
    def _analyze_visual_elements(self, video_asset: VideoAsset) -> Dict:
        """Analyze visual elements using OpenCV"""
        try:
            cap = cv2.VideoCapture(video_asset.file.path)
            
            # Sample frames throughout video
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = int(cap.get(cv2.CAP_PROP_FPS))
            duration = frame_count / fps
            
            # Analyze 10 frames evenly distributed
            sample_frames = []
            for i in range(10):
                frame_pos = int((i / 9) * frame_count) if i < 9 else frame_count - 1
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_pos)
                ret, frame = cap.read()
                if ret:
                    sample_frames.append(frame)
            
            cap.release()
            
            # Analyze frames
            brightness_values = []
            color_diversity = []
            motion_estimates = []
            
            for i, frame in enumerate(sample_frames):
                # Brightness analysis
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                brightness = np.mean(gray)
                brightness_values.append(brightness)
                
                # Color analysis
                colors = cv2.split(frame)
                color_std = [np.std(channel) for channel in colors]
                color_diversity.append(np.mean(color_std))
                
                # Motion estimation (compare with next frame)
                if i < len(sample_frames) - 1:
                    next_frame = sample_frames[i + 1]
                    diff = cv2.absdiff(frame, next_frame)
                    motion = np.mean(diff)
                    motion_estimates.append(motion)
            
            return {
                'avg_brightness': np.mean(brightness_values),
                'brightness_variation': np.std(brightness_values),
                'avg_color_diversity': np.mean(color_diversity),
                'estimated_motion': np.mean(motion_estimates) if motion_estimates else 0,
                'visual_complexity': np.mean(color_diversity),
                'lighting_quality': 'good' if np.mean(brightness_values) > 50 else 'poor'
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def _analyze_audio_elements(self, video_asset: VideoAsset) -> Dict:
        """Analyze audio characteristics"""
        try:
            with VideoFileClip(video_asset.file.path) as clip:
                if not clip.audio:
                    return {'has_audio': False}
                
                # Extract audio
                audio = clip.audio
                
                # Basic audio analysis
                # You could use librosa for more advanced analysis
                return {
                    'has_audio': True,
                    'duration': audio.duration,
                    'estimated_volume': 'medium',  # Would need librosa for real analysis
                    'audio_type': 'mixed',  # music, speech, silence, etc.
                }
        except Exception as e:
            return {'error': str(e)}
    
    def _analyze_scenes_and_pace(self, video_asset: VideoAsset) -> Dict:
        """Analyze scene changes and video pace"""
        try:
            cap = cv2.VideoCapture(video_asset.file.path)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = int(cap.get(cv2.CAP_PROP_FPS))
            
            # Detect scene changes by comparing consecutive frames
            scene_changes = []
            prev_frame = None
            
            # Check every 30th frame to speed up processing
            for i in range(0, frame_count, 30):
                cap.set(cv2.CAP_PROP_POS_FRAMES, i)
                ret, frame = cap.read()
                
                if ret and prev_frame is not None:
                    # Calculate difference between frames
                    diff = cv2.absdiff(frame, prev_frame)
                    diff_mean = np.mean(diff)
                    
                    # If difference is significant, it's likely a scene change
                    if diff_mean > 50:  # Threshold for scene change
                        scene_changes.append(i / fps)  # Convert to time
                
                prev_frame = frame
            
            cap.release()
            
            # Calculate pace
            duration = frame_count / fps
            cuts_per_minute = (len(scene_changes) / duration) * 60 if duration > 0 else 0
            
            if cuts_per_minute < 30:
                pace = 'slow'
            elif cuts_per_minute < 60:
                pace = 'medium'
            else:
                pace = 'fast'
            
            return {
                'scene_changes': scene_changes,
                'cuts_per_minute': cuts_per_minute,
                'estimated_pace': pace,
                'total_scenes': len(scene_changes) + 1,
                'avg_scene_duration': duration / (len(scene_changes) + 1) if scene_changes else duration
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def _ai_style_analysis(self, video_asset: VideoAsset, analysis_results: Dict) -> Dict:
        """Use AI to analyze style and mood based on video characteristics"""
        
        # Create a description of the video based on technical analysis
        video_description = self._create_video_description(analysis_results)
        
        system_prompt = """You are a video analysis expert. Analyze the following video characteristics and classify the video's style, mood, and tone.

Return your analysis as JSON with these fields:
- mood: energetic, calm, serious, playful, inspirational, dramatic, minimal, or vibrant
- style: lifestyle, tutorial, product_demo, talking_head, b_roll, animation, screen_record, or testimonial  
- tone: professional, casual, friendly, authoritative, creative, or conversational
- energy_level: low, medium, or high
- suitable_for: array of content types this video would work well with
- platform_recommendations: array of social platforms this video format suits
- content_matching_notes: brief explanation of what type of content would pair well

Be specific and concise in your analysis."""

        user_prompt = f"""Analyze this video based on its technical characteristics:

Duration: {analysis_results.get('properties', {}).get('duration', 'unknown')} seconds
Aspect Ratio: {analysis_results.get('properties', {}).get('aspect_ratio', 'unknown')}
Has Audio: {analysis_results.get('audio', {}).get('has_audio', False)}
Pace: {analysis_results.get('scenes', {}).get('estimated_pace', 'unknown')} ({analysis_results.get('scenes', {}).get('cuts_per_minute', 0)} cuts/min)
Visual Complexity: {analysis_results.get('visual', {}).get('visual_complexity', 'unknown')}
Brightness: {analysis_results.get('visual', {}).get('avg_brightness', 'unknown')}
Motion Level: {analysis_results.get('visual', {}).get('estimated_motion', 'unknown')}
Lighting Quality: {analysis_results.get('visual', {}).get('lighting_quality', 'unknown')}

Video Title: {video_asset.title}
Description: {video_asset.description}

Please provide your analysis in JSON format."""

        try:
            response = self.anthropic_client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=1000,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}]
            )
            
            # Parse AI response
            ai_analysis = json.loads(response.content[0].text)
            
            # Update video asset with AI analysis
            video_asset.mood = ai_analysis.get('mood', '')
            video_asset.pace = analysis_results.get('scenes', {}).get('estimated_pace', '')
            video_asset.style = ai_analysis.get('style', '')
            video_asset.suitable_platforms = ai_analysis.get('platform_recommendations', [])
            video_asset.tags = ai_analysis.get('suitable_for', [])
            video_asset.save()
            
            return ai_analysis
            
        except Exception as e:
            return {'error': f'AI analysis failed: {str(e)}'}
    
    def _create_video_description(self, analysis_results: Dict) -> str:
        """Create a text description of video characteristics for AI analysis"""
        description_parts = []
        
        # Add technical details
        props = analysis_results.get('properties', {})
        if props.get('duration'):
            description_parts.append(f"Duration: {props['duration']:.1f} seconds")
        
        visual = analysis_results.get('visual', {})
        if visual.get('avg_brightness'):
            brightness = 'bright' if visual['avg_brightness'] > 100 else 'dim'
            description_parts.append(f"Lighting: {brightness}")
        
        scenes = analysis_results.get('scenes', {})
        if scenes.get('cuts_per_minute'):
            description_parts.append(f"Editing pace: {scenes['cuts_per_minute']:.1f} cuts per minute")
        
        return ". ".join(description_parts)


class ContentVideoMatcher:
    """Match generated content with suitable videos"""
    
    def __init__(self):
        self.anthropic_client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    
    def find_matches(self, content_generation, limit: int = 5) -> List[ContentVideoMatch]:
        """Find the best video matches for generated content"""
        
        user = content_generation.user
        available_videos = VideoAsset.objects.filter(
            user=user,
            is_processed=True
        )
        
        matches = []
        
        for video in available_videos:
            match_score = self._calculate_match_score(content_generation, video)
            
            if match_score > 0.3:  # Minimum threshold
                match = ContentVideoMatch.objects.create(
                    content_generation=content_generation,
                    video_asset=video,
                    match_score=match_score,
                    match_quality=self._get_match_quality(match_score),
                    match_reasoning=self._generate_match_reasoning(content_generation, video, match_score)
                )
                matches.append(match)
        
        # Return top matches
        return sorted(matches, key=lambda x: x.match_score, reverse=True)[:limit]
    
    def _calculate_match_score(self, content_generation, video_asset: VideoAsset) -> float:
        """Calculate how well content matches with video"""
        
        score_components = {}
        
        # 1. Platform compatibility (30%)
        platform_score = self._calculate_platform_score(content_generation, video_asset)
        score_components['platform'] = platform_score * 0.3
        
        # 2. Tone/mood alignment (30%)
        tone_score = self._calculate_tone_score(content_generation, video_asset)
        score_components['tone'] = tone_score * 0.3
        
        # 3. Content style match (25%)
        style_score = self._calculate_style_score(content_generation, video_asset)
        score_components['style'] = style_score * 0.25
        
        # 4. Technical compatibility (15%)
        technical_score = self._calculate_technical_score(content_generation, video_asset)
        score_components['technical'] = technical_score * 0.15
        
        total_score = sum(score_components.values())
        
        return min(total_score, 1.0)  # Cap at 1.0
    
    def _calculate_platform_score(self, content_generation, video_asset: VideoAsset) -> float:
        """Score based on platform compatibility"""
        target_platforms = set(content_generation.target_platforms)
        suitable_platforms = set(video_asset.suitable_platforms)
        
        if not target_platforms or not suitable_platforms:
            return 0.5  # Neutral score if no platform data
        
        overlap = len(target_platforms.intersection(suitable_platforms))
        total_target = len(target_platforms)
        
        return overlap / total_target if total_target > 0 else 0
    
    def _calculate_tone_score(self, content_generation, video_asset: VideoAsset) -> float:
        """Score based on tone alignment"""
        
        # Map content characteristics to video moods
        tone_mapping = {
            'educational': ['serious', 'minimal'],
            'entertaining': ['playful', 'energetic', 'vibrant'],
            'professional': ['serious', 'minimal', 'calm'],
            'inspirational': ['inspirational', 'calm', 'dramatic'],
            'casual': ['playful', 'vibrant', 'energetic'],
        }
        
        # Infer content tone from topic/context (simplified)
        content_tone = self._infer_content_tone(content_generation)
        video_mood = video_asset.mood
        
        if not content_tone or not video_mood:
            return 0.5  # Neutral score
        
        compatible_moods = tone_mapping.get(content_tone, [])
        
        if video_mood in compatible_moods:
            return 1.0
        elif video_mood in ['minimal', 'calm']:  # These are generally versatile
            return 0.7
        else:
            return 0.3
    
    def _calculate_style_score(self, content_generation, video_asset: VideoAsset) -> float:
        """Score based on content style compatibility"""
        
        # This would be more sophisticated in practice
        video_style = video_asset.style
        
        # Map content types to preferred video styles
        style_preferences = {
            'tutorial': ['tutorial', 'screen_record', 'talking_head'],
            'product': ['product_demo', 'lifestyle', 'b_roll'],
            'story': ['lifestyle', 'b_roll', 'testimonial'],
            'educational': ['tutorial', 'talking_head', 'screen_record'],
        }
        
        content_type = self._infer_content_type(content_generation)
        preferred_styles = style_preferences.get(content_type, [])
        
        if video_style in preferred_styles:
            return 1.0
        elif video_style in ['b_roll', 'lifestyle']:  # Versatile styles
            return 0.8
        else:
            return 0.4
    
    def _calculate_technical_score(self, content_generation, video_asset: VideoAsset) -> float:
        """Score based on technical compatibility"""
        score = 1.0
        
        # Prefer vertical videos for TikTok/Instagram
        if 'tiktok' in content_generation.target_platforms or 'instagram' in content_generation.target_platforms:
            if video_asset.is_vertical:
                score *= 1.0
            elif video_asset.is_square:
                score *= 0.8
            else:
                score *= 0.6
        
        # Video quality factors
        if video_asset.processing_error:
            score *= 0.5
        
        return score
    
    def _infer_content_tone(self, content_generation) -> str:
        """Infer content tone from topic and context"""
        topic = content_generation.topic.lower()
        
        # Simple keyword-based inference (would be more sophisticated in practice)
        if any(word in topic for word in ['tutorial', 'how to', 'learn', 'guide']):
            return 'educational'
        elif any(word in topic for word in ['business', 'professional', 'corporate']):
            return 'professional'
        elif any(word in topic for word in ['fun', 'funny', 'entertainment', 'meme']):
            return 'entertaining'
        elif any(word in topic for word in ['inspire', 'motivate', 'success', 'goal']):
            return 'inspirational'
        else:
            return 'casual'
    
    def _infer_content_type(self, content_generation) -> str:
        """Infer content type from topic and context"""
        topic = content_generation.topic.lower()
        
        if any(word in topic for word in ['tutorial', 'how to', 'step by step']):
            return 'tutorial'
        elif any(word in topic for word in ['product', 'review', 'demo', 'unbox']):
            return 'product'
        elif any(word in topic for word in ['story', 'experience', 'journey']):
            return 'story'
        elif any(word in topic for word in ['learn', 'education', 'explain', 'understand']):
            return 'educational'
        else:
            return 'general'
    
    def _get_match_quality(self, score: float) -> str:
        """Convert numeric score to quality rating"""
        if score >= 0.9:
            return 'excellent'
        elif score >= 0.7:
            return 'good'
        elif score >= 0.5:
            return 'fair'
        else:
            return 'poor'
    
    def _generate_match_reasoning(self, content_generation, video_asset: VideoAsset, score: float) -> str:
        """Generate AI explanation of why content and video match"""
        
        system_prompt = """You are an expert in content creation and video marketing. Explain why a specific video asset matches well (or doesn't match well) with generated content. Be concise and actionable."""
        
        user_prompt = f"""Content Topic: {content_generation.topic}
Content Platforms: {', '.join(content_generation.target_platforms)}
Content Context: {content_generation.additional_context}

Video Style: {video_asset.style}
Video Mood: {video_asset.mood}  
Video Pace: {video_asset.pace}
Video Duration: {video_asset.duration_seconds}s
Video Aspect Ratio: {video_asset.aspect_ratio}

Match Score: {score:.2f}/1.0

Explain in 2-3 sentences why this video does or doesn't match well with the content, and give one specific tip for how to use them together effectively."""

        try:
            response = self.anthropic_client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=200,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}]
            )
            
            return response.content[0].text
            
        except Exception as e:
            return f"This video has a {score:.0%} compatibility match based on style and platform alignment."