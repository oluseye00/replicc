from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
import time
import logging
from anthropic import Anthropic

# Import video generation tasks to register them with Celery
from .video_tasks import generate_video_from_text, create_video_template

logger = logging.getLogger(__name__)


@shared_task
def test_task():
    """Simple test task to verify Celery is working"""
    logger.info("Test task executed successfully!")
    return "Test task completed"


@shared_task
def generate_content_async(prompt, user_id=None, max_tokens=1000, model="claude-3-haiku-20240307"):
    """
    Async task for content generation using Anthropic Claude API
    
    Available models:
    - claude-3-haiku-20240307 (fastest, cheapest)
    - claude-3-sonnet-20240229 (balanced)
    - claude-3-opus-20240229 (most capable, slowest)
    """
    logger.info(f"Starting content generation for prompt: {prompt[:50]}...")
    
    try:
        # Initialize Anthropic client
        if not settings.ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY not configured")
            
        client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        
        # Make API call to Claude
        logger.info(f"Calling Anthropic API with model: {model}")
        response = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            messages=[{
                "role": "user", 
                "content": prompt
            }]
        )
        
        generated_content = response.content[0].text
        
        logger.info(f"Content generation completed. Generated {len(generated_content)} characters.")
        
        return {
            "success": True,
            "content": generated_content,
            "prompt": prompt,
            "user_id": user_id,
            "model": model,
            "tokens_used": response.usage.input_tokens + response.usage.output_tokens
        }
        
    except Exception as e:
        error_msg = f"Content generation failed: {str(e)}"
        logger.error(error_msg)
        
        return {
            "success": False,
            "error": error_msg,
            "prompt": prompt,
            "user_id": user_id
        }


@shared_task
def process_video_matching(video_id):
    """
    Async task for video matching processing
    """
    logger.info(f"Starting video matching for video ID: {video_id}")
    
    # Simulate video processing
    time.sleep(5)
    
    # Here you would do actual video processing
    result = f"Video {video_id} processed successfully"
    
    logger.info(f"Video matching completed for {video_id}")
    return result


@shared_task
def send_notification_email(recipient, subject, message):
    """
    Async task for sending notification emails
    """
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [recipient],
            fail_silently=False,
        )
        logger.info(f"Notification email sent to {recipient}")
        return f"Email sent to {recipient}"
    except Exception as e:
        logger.error(f"Failed to send email to {recipient}: {str(e)}")
        raise


@shared_task
def cleanup_old_files():
    """
    Periodic task to clean up old uploaded files
    """
    logger.info("Starting file cleanup task")
    
    # Here you would implement file cleanup logic
    # For example, delete files older than 30 days
    
    logger.info("File cleanup completed")
    return "File cleanup completed"