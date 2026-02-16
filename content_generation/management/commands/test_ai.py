from django.core.management.base import BaseCommand
from content_generation.tasks import generate_content_async
from django.conf import settings
import time
import json


class Command(BaseCommand):
    help = 'Test AI content generation with Anthropic Claude API'

    def add_arguments(self, parser):
        parser.add_argument(
            'prompt',
            nargs='?',
            default="Write a short creative story about a robot learning to paint.",
            help='The prompt to send to Claude (default: robot painting story)'
        )
        parser.add_argument(
            '--max-tokens',
            type=int,
            default=500,
            help='Maximum tokens to generate (default: 500)'
        )
        parser.add_argument(
            '--sync',
            action='store_true',
            help='Wait for the task to complete and show results'
        )
        parser.add_argument(
            '--user-id',
            type=int,
            help='User ID to associate with the generation'
        )
        parser.add_argument(
            '--model',
            choices=['claude-3-haiku-20240307', 'claude-3-sonnet-20240229', 'claude-3-opus-20240229'],
            default='claude-3-haiku-20240307',
            help='Claude model to use (default: haiku - fastest/cheapest)'
        )

    def handle(self, *args, **options):
        prompt = options['prompt']
        max_tokens = options['max_tokens']
        user_id = options.get('user_id')
        model = options['model']
        wait_for_result = options['sync']

        # Check if API key is configured
        if not settings.ANTHROPIC_API_KEY:
            self.stdout.write(
                self.style.ERROR('❌ ANTHROPIC_API_KEY not configured in settings!')
            )
            self.stdout.write('Please add your API key to the .env file:')
            self.stdout.write('ANTHROPIC_API_KEY=sk-ant-api03-...')
            return

        self.stdout.write(
            self.style.SUCCESS('🤖 Testing AI Content Generation with Claude')
        )
        self.stdout.write(f'📝 Prompt: "{prompt}"')
        self.stdout.write(f'🤖 Model: {model}')
        self.stdout.write(f'🔧 Max tokens: {max_tokens}')
        if user_id:
            self.stdout.write(f'👤 User ID: {user_id}')

        # Submit the task
        self.stdout.write('\n⏳ Submitting task to Celery...')
        
        try:
            result = generate_content_async.delay(
                prompt=prompt,
                user_id=user_id,
                max_tokens=max_tokens,
                model=model
            )
            
            self.stdout.write(f'✅ Task submitted with ID: {result.id}')
            
            if wait_for_result:
                self.stdout.write('\n⌛ Waiting for Claude to generate content...')
                
                try:
                    # Wait up to 60 seconds for the AI generation
                    response = result.get(timeout=60)
                    
                    if response['success']:
                        self.stdout.write(
                            self.style.SUCCESS('\n🎉 Content generation successful!')
                        )
                        
                        # Display the results nicely
                        content = response['content']
                        
                        self.stdout.write('\n' + '='*60)
                        self.stdout.write('📖 GENERATED CONTENT:')
                        self.stdout.write('='*60)
                        self.stdout.write(content)
                        self.stdout.write('='*60)
                        
                        # Show metadata
                        self.stdout.write(f'\n📊 Model: {response["model"]}')
                        self.stdout.write(f'🔢 Tokens used: {response["tokens_used"]}')
                        self.stdout.write(f'📏 Content length: {len(content)} characters')
                        
                    else:
                        self.stdout.write(
                            self.style.ERROR(f'\n❌ Content generation failed: {response["error"]}')
                        )
                        
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'\n❌ Task failed or timed out: {e}')
                    )
                    self.stdout.write('Check Celery logs: tail -f logs/celery_worker.log')
            
            else:
                self.stdout.write('\n💡 To check the result later, run:')
                self.stdout.write(f'   celery -A repli result {result.id}')
                self.stdout.write('\nOr run with --sync to wait for completion:')
                self.stdout.write('   python manage.py test_ai --sync')

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Failed to submit task: {e}')
            )
            self.stdout.write('Make sure Celery worker is running: ./celery_status.sh')

        self.stdout.write(
            self.style.SUCCESS('\n🚀 AI testing completed!')
        )