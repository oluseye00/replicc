from celery import shared_task
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
import tempfile
import os
import json
import logging
import textwrap
from typing import Dict, List, Optional, Tuple
from PIL import Image, ImageDraw, ImageFont
import numpy as np

logger = logging.getLogger(__name__)


@shared_task
def generate_video_from_text(
    text_content: str,
    title: str = "Generated Video",
    user_id: Optional[int] = None,
    video_style: str = "slideshow",
    duration: int = 10,
    resolution: Tuple[int, int] = (1080, 1920),  # Vertical for TikTok/Instagram
    background_color: Tuple[int, int, int] = (20, 20, 40),
    text_color: Tuple[int, int, int] = (255, 255, 255),
    font_size: int = 60,
) -> Dict:
    """
    Generate a video from text content using MoviePy
    
    Args:
        text_content: The text to display in the video
        title: Video title
        user_id: User creating the video
        video_style: Style of video ('slideshow', 'typewriter', 'fade')
        duration: Video duration in seconds
        resolution: Video resolution (width, height)
        background_color: RGB background color
        text_color: RGB text color
        font_size: Font size for text
    
    Returns:
        Dict with video information and file path
    """
    logger.info(f"Starting video generation: {title[:50]}...")
    
    # Convert lists to tuples (Celery JSON serialization converts tuples to lists)
    if isinstance(background_color, list):
        background_color = tuple(background_color)
    if isinstance(text_color, list):
        text_color = tuple(text_color)
    if isinstance(resolution, list):
        resolution = tuple(resolution)
    
    try:
        # Import here to avoid import errors if not installed
        from moviepy.editor import (
            VideoClip, TextClip, CompositeVideoClip, 
            ColorClip, concatenate_videoclips
        )
        
        # Split text into chunks for multiple slides
        text_chunks = _split_text_into_chunks(text_content, max_chars=100)
        slide_duration = duration / len(text_chunks)
        
        clips = []
        
        if video_style == "slideshow":
            clips = _create_slideshow_clips(
                text_chunks, slide_duration, resolution, 
                background_color, text_color, font_size
            )
        elif video_style == "typewriter":
            clips = _create_typewriter_clips(
                text_chunks, slide_duration, resolution,
                background_color, text_color, font_size
            )
        elif video_style == "fade":
            clips = _create_fade_clips(
                text_chunks, slide_duration, resolution,
                background_color, text_color, font_size
            )
        else:
            # Default to slideshow
            clips = _create_slideshow_clips(
                text_chunks, slide_duration, resolution,
                background_color, text_color, font_size
            )
        
        # Concatenate all clips
        final_video = concatenate_videoclips(clips)
        
        # Generate output filename
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '_')).rstrip()
        safe_title = safe_title.replace(' ', '_')[:30]
        output_filename = f"generated_video_{safe_title}_{user_id or 'anonymous'}.mp4"
        
        # Create temporary file for processing
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as temp_file:
            temp_path = temp_file.name
        
        # Write video file
        logger.info("Rendering video...")
        final_video.write_videofile(
            temp_path,
            fps=24,
            codec='libx264',
            audio_codec='aac' if final_video.audio else None,
            temp_audiofile='temp-audio.m4a',
            remove_temp=True,
            verbose=False,
            logger=None  # Suppress moviepy logs
        )
        
        # Read the file content
        with open(temp_path, 'rb') as video_file:
            video_content = video_file.read()
        
        # Save to Django storage
        saved_path = default_storage.save(
            f"generated_videos/{output_filename}",
            ContentFile(video_content)
        )
        
        # Clean up temp file
        os.unlink(temp_path)
        
        # Close clips to free memory
        final_video.close()
        for clip in clips:
            clip.close()
        
        logger.info(f"Video generation completed: {saved_path}")
        
        return {
            "success": True,
            "video_path": saved_path,
            "video_url": default_storage.url(saved_path),
            "title": title,
            "duration": duration,
            "resolution": resolution,
            "style": video_style,
            "file_size_mb": len(video_content) / (1024 * 1024),
            "text_chunks_count": len(text_chunks),
            "user_id": user_id
        }
        
    except Exception as e:
        error_msg = f"Video generation failed: {str(e)}"
        logger.error(error_msg)
        
        return {
            "success": False,
            "error": error_msg,
            "title": title,
            "user_id": user_id
        }


@shared_task
def create_video_template(
    template_name: str,
    slides_data: List[Dict],
    user_id: Optional[int] = None,
    template_style: str = "modern",
    background_music: Optional[str] = None
) -> Dict:
    """
    Create a video from a template with multiple slides
    
    Args:
        template_name: Name of the template
        slides_data: List of slide data [{"text": "...", "duration": 3, "image": "..."}]
        user_id: User creating the video  
        template_style: Visual style template
        background_music: Path to background music file
    
    Returns:
        Dict with video information
    """
    logger.info(f"Creating video from template: {template_name}")
    
    try:
        from moviepy.editor import (
            VideoClip, TextClip, CompositeVideoClip, ImageClip,
            ColorClip, concatenate_videoclips, AudioFileClip
        )
        
        clips = []
        total_duration = 0
        
        for i, slide_data in enumerate(slides_data):
            slide_duration = slide_data.get('duration', 3)
            slide_text = slide_data.get('text', '')
            slide_image = slide_data.get('image', None)
            
            # Create slide clip
            slide_clip = _create_template_slide(
                slide_text, slide_image, slide_duration, template_style, i
            )
            clips.append(slide_clip)
            total_duration += slide_duration
        
        # Concatenate slides
        final_video = concatenate_videoclips(clips)
        
        # Add background music if provided
        if background_music and os.path.exists(background_music):
            audio_clip = AudioFileClip(background_music)
            # Loop or trim audio to match video duration
            if audio_clip.duration < total_duration:
                # Loop audio
                loops_needed = int(total_duration / audio_clip.duration) + 1
                audio_clip = audio_clip.loop(n=loops_needed)
            
            audio_clip = audio_clip.subclip(0, total_duration)
            final_video = final_video.set_audio(audio_clip)
        
        # Save video (similar to generate_video_from_text)
        safe_name = "".join(c for c in template_name if c.isalnum() or c in (' ', '_')).rstrip()
        safe_name = safe_name.replace(' ', '_')[:30]
        output_filename = f"template_video_{safe_name}_{user_id or 'anonymous'}.mp4"
        
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as temp_file:
            temp_path = temp_file.name
        
        logger.info("Rendering template video...")
        final_video.write_videofile(
            temp_path,
            fps=24,
            codec='libx264',
            verbose=False,
            logger=None
        )
        
        with open(temp_path, 'rb') as video_file:
            video_content = video_file.read()
        
        saved_path = default_storage.save(
            f"generated_videos/{output_filename}",
            ContentFile(video_content)
        )
        
        os.unlink(temp_path)
        
        final_video.close()
        for clip in clips:
            clip.close()
        
        logger.info(f"Template video created: {saved_path}")
        
        return {
            "success": True,
            "video_path": saved_path,
            "video_url": default_storage.url(saved_path),
            "template_name": template_name,
            "duration": total_duration,
            "slides_count": len(slides_data),
            "style": template_style,
            "file_size_mb": len(video_content) / (1024 * 1024),
            "user_id": user_id
        }
        
    except Exception as e:
        error_msg = f"Template video creation failed: {str(e)}"
        logger.error(error_msg)
        
        return {
            "success": False,
            "error": error_msg,
            "template_name": template_name,
            "user_id": user_id
        }


def _split_text_into_chunks(text: str, max_chars: int = 100) -> List[str]:
    """Split text into chunks suitable for video slides"""
    words = text.split()
    chunks = []
    current_chunk = []
    current_length = 0
    
    for word in words:
        word_length = len(word) + 1  # +1 for space
        
        if current_length + word_length > max_chars and current_chunk:
            chunks.append(' '.join(current_chunk))
            current_chunk = [word]
            current_length = len(word)
        else:
            current_chunk.append(word)
            current_length += word_length
    
    if current_chunk:
        chunks.append(' '.join(current_chunk))
    
    return chunks


def _create_slideshow_clips(text_chunks, slide_duration, resolution, bg_color, text_color, font_size):
    """Create simple slideshow clips"""
    from moviepy.editor import ImageClip, ColorClip, CompositeVideoClip
    import tempfile
    import os
    
    clips = []
    width, height = resolution
    
    for text in text_chunks:
        # Create background
        background = ColorClip(size=resolution, color=bg_color, duration=slide_duration)
        
        # Create text as image using PIL (more reliable than TextClip)
        text_image = _create_text_image(
            text, 
            width=int(width * 0.9), 
            height=int(height * 0.8),
            font_size=font_size,
            text_color=text_color,
            bg_color=bg_color
        )
        
        # Save text image temporarily
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
            text_image.save(tmp.name)
            temp_path = tmp.name
        
        try:
            # Create image clip from text
            text_clip = ImageClip(temp_path).set_duration(slide_duration).set_position('center')
            
            # Composite
            slide = CompositeVideoClip([background, text_clip])
            clips.append(slide)
            
        except Exception as e:
            logger.warning(f"Failed to create text clip: {e}")
            # Just use background if text fails
            clips.append(background)
        
        finally:
            # Clean up temp file
            try:
                os.unlink(temp_path)
            except:
                pass
    
    return clips


def _create_text_image(text, width, height, font_size=40, text_color=(255, 255, 255), bg_color=(30, 30, 50)):
    """Create a text image using PIL - more reliable than MoviePy TextClip"""
    from PIL import Image, ImageDraw, ImageFont
    import textwrap
    
    # Create image with background color
    img = Image.new('RGB', (width, height), color=bg_color)
    draw = ImageDraw.Draw(img)
    
    # Try to load a system font
    font = None
    font_paths = [
        '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
        '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 
        '/usr/share/fonts/truetype/ubuntu/Ubuntu-Regular.ttf',
        '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf'
    ]
    
    for font_path in font_paths:
        try:
            if os.path.exists(font_path):
                font = ImageFont.truetype(font_path, font_size)
                break
        except:
            continue
    
    # Fallback to default font if no truetype fonts work
    if font is None:
        try:
            font = ImageFont.load_default()
        except:
            # If even default fails, we'll use draw.text without font
            pass
    
    # Wrap text to fit width
    if font:
        # Estimate characters per line
        avg_char_width = font.getbbox('A')[2]
        chars_per_line = max(1, width // avg_char_width)
    else:
        chars_per_line = width // 10  # Rough estimate
    
    wrapped_text = textwrap.fill(text, width=chars_per_line)
    lines = wrapped_text.split('\n')
    
    # Calculate text positioning
    if font:
        line_height = font.getbbox('A')[3] + 5
    else:
        line_height = 20
        
    total_text_height = len(lines) * line_height
    y_start = (height - total_text_height) // 2
    
    # Draw each line
    for i, line in enumerate(lines):
        if font:
            # Get text width for centering
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]
            x = (width - text_width) // 2
            draw.text((x, y_start + i * line_height), line, font=font, fill=text_color)
        else:
            # Fallback without font
            x = width // 4  # Rough centering
            draw.text((x, y_start + i * line_height), line, fill=text_color)
    
    return img


def _create_typewriter_clips(text_chunks, slide_duration, resolution, bg_color, text_color, font_size):
    """Create typewriter effect clips"""
    # For now, same as slideshow - would implement typewriter effect
    return _create_slideshow_clips(text_chunks, slide_duration, resolution, bg_color, text_color, font_size)


def _create_fade_clips(text_chunks, slide_duration, resolution, bg_color, text_color, font_size):
    """Create fade in/out clips"""
    from moviepy.editor import ImageClip, ColorClip, CompositeVideoClip
    import tempfile
    import os
    
    clips = []
    width, height = resolution
    
    for text in text_chunks:
        background = ColorClip(size=resolution, color=bg_color, duration=slide_duration)
        
        # Create text as image using PIL
        text_image = _create_text_image(
            text, 
            width=int(width * 0.9), 
            height=int(height * 0.8),
            font_size=font_size,
            text_color=text_color,
            bg_color=bg_color
        )
        
        # Save text image temporarily
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
            text_image.save(tmp.name)
            temp_path = tmp.name
        
        try:
            # Create image clip from text with fade effects
            text_clip = ImageClip(temp_path).set_duration(slide_duration).set_position('center')
            text_clip = text_clip.fadein(0.5).fadeout(0.5)
            
            # Composite
            slide = CompositeVideoClip([background, text_clip])
            clips.append(slide)
            
        except Exception as e:
            logger.warning(f"Failed to create fade text clip: {e}")
            # Just use background if text fails
            clips.append(background)
        
        finally:
            # Clean up temp file
            try:
                os.unlink(temp_path)
            except:
                pass
    
    return clips


def _create_template_slide(text, image_path, duration, style, slide_number):
    """Create a slide for template video"""
    from moviepy.editor import ImageClip, ColorClip, CompositeVideoClip
    import tempfile
    
    # Template styles with different color schemes
    styles = {
        "modern": {
            "bg_color": (30, 30, 50),
            "text_color": (255, 255, 255),
            "accent_color": (70, 130, 180)
        },
        "minimal": {
            "bg_color": (250, 250, 250),
            "text_color": (0, 0, 0), 
            "accent_color": (100, 100, 100)
        },
        "vibrant": {
            "bg_color": (255, 50, 100),
            "text_color": (255, 255, 255),
            "accent_color": (255, 200, 50)
        }
    }
    
    style_config = styles.get(style, styles["modern"])
    
    # Create background
    background = ColorClip(
        size=(1080, 1920), 
        color=style_config["bg_color"], 
        duration=duration
    )
    
    clips = [background]
    
    # Add image if provided
    if image_path and os.path.exists(image_path):
        try:
            image_clip = ImageClip(image_path).set_duration(duration)
            # Resize to fit nicely in frame
            image_clip = image_clip.resize(height=800).set_position(('center', 200))
            clips.append(image_clip)
        except:
            logger.warning(f"Could not load image: {image_path}")
    
    # Add text using PIL instead of TextClip
    if text:
        try:
            # Create text image
            text_image = _create_text_image(
                text, 
                width=900, 
                height=400,
                font_size=50,
                text_color=style_config["text_color"],
                bg_color=style_config["bg_color"]
            )
            
            # Save text image temporarily
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                text_image.save(tmp.name)
                temp_path = tmp.name
            
            text_clip = ImageClip(temp_path).set_duration(duration).set_position(('center', 1200))
            clips.append(text_clip)
            
            # Clean up temp file
            try:
                os.unlink(temp_path)
            except:
                pass
                
        except Exception as e:
            logger.warning(f"Could not create text clip for: {text[:50]} - {e}")
    
    return CompositeVideoClip(clips)