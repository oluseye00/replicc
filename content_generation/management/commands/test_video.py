import json
import time

from django.conf import settings
from django.core.management.base import BaseCommand

from content_generation.video_tasks import (
    create_video_template,
    generate_video_from_text,
)


class Command(BaseCommand):
    help = "Test video generation capabilities"

    def add_arguments(self, parser):
        parser.add_argument(
            "text",
            nargs="?",
            default="Welcome to AI-powered video generation! This is a test of our automated video creation system. It can take any text and turn it into an engaging video.",
            help="Text content to generate video from",
        )
        parser.add_argument(
            "--style",
            choices=["slideshow", "typewriter", "fade"],
            default="slideshow",
            help="Video style (default: slideshow)",
        )
        parser.add_argument(
            "--duration",
            type=int,
            default=10,
            help="Video duration in seconds (default: 10)",
        )
        parser.add_argument(
            "--resolution",
            choices=["vertical", "horizontal", "square"],
            default="vertical",
            help="Video aspect ratio (default: vertical for TikTok/Instagram)",
        )
        parser.add_argument(
            "--title",
            default="Test Generated Video",
            help="Video title (default: Test Generated Video)",
        )
        parser.add_argument(
            "--sync",
            action="store_true",
            help="Wait for video generation to complete and show results",
        )
        parser.add_argument(
            "--template",
            action="store_true",
            help="Test template-based video creation instead",
        )
        parser.add_argument(
            "--user-id",
            type=int,
            default=1,
            help="User ID for video generation (default: 1)",
        )

    def handle(self, *args, **options):
        text = options["text"]
        style = options["style"]
        duration = options["duration"]
        resolution_type = options["resolution"]
        title = options["title"]
        user_id = options["user_id"]
        wait_for_result = options["sync"]
        use_template = options["template"]

        # Map resolution types
        resolution_map = {
            "vertical": (1080, 1920),  # TikTok/Instagram Stories
            "horizontal": (1920, 1080),  # YouTube/Facebook
            "square": (1080, 1080),  # Instagram Posts
        }
        resolution = resolution_map[resolution_type]

        self.stdout.write(self.style.SUCCESS("🎬 Testing Video Generation"))
        self.stdout.write(f'📝 Text: "{text[:100]}{"..." if len(text) > 100 else ""}"')
        self.stdout.write(f"🎨 Style: {style}")
        self.stdout.write(f"⏱️  Duration: {duration} seconds")
        self.stdout.write(
            f"📐 Resolution: {resolution[0]}x{resolution[1]} ({resolution_type})"
        )
        self.stdout.write(f"🏷️  Title: {title}")
        self.stdout.write(f"👤 User ID: {user_id}")

        if use_template:
            self._test_template_video(text, title, user_id, wait_for_result)
        else:
            self._test_text_video(
                text, title, user_id, style, duration, resolution, wait_for_result
            )

    def _test_text_video(
        self, text, title, user_id, style, duration, resolution, wait_for_result
    ):
        """Test simple text-to-video generation"""

        self.stdout.write("\n⏳ Submitting video generation task to Celery...")

        try:
            result = generate_video_from_text.delay(
                text_content=text,
                title=title,
                user_id=user_id,
                video_style=style,
                duration=duration,
                resolution=resolution,
                background_color=(30, 30, 50),  # Dark blue
                text_color=(255, 255, 255),  # White
                font_size=60,
            )

            self.stdout.write(f"✅ Task submitted with ID: {result.id}")

            if wait_for_result:
                self.stdout.write(
                    "\n⌛ Generating video (this may take 30-60 seconds)..."
                )

                try:
                    # Wait up to 3 minutes for video generation
                    response = result.get(timeout=180)

                    if response["success"]:
                        self.stdout.write(
                            self.style.SUCCESS("\n🎉 Video generation successful!")
                        )

                        # Display the results
                        self.stdout.write("\n" + "=" * 60)
                        self.stdout.write("🎬 GENERATED VIDEO DETAILS:")
                        self.stdout.write("=" * 60)
                        self.stdout.write(f'📂 File path: {response["video_path"]}')
                        if response.get("video_url"):
                            self.stdout.write(f'🌐 Video URL: {response["video_url"]}')
                        self.stdout.write(
                            f'⏱️  Duration: {response["duration"]} seconds'
                        )
                        self.stdout.write(
                            f'📐 Resolution: {response["resolution"][0]}x{response["resolution"][1]}'
                        )
                        self.stdout.write(f'🎨 Style: {response["style"]}')
                        self.stdout.write(
                            f'💾 File size: {response["file_size_mb"]:.2f} MB'
                        )
                        self.stdout.write(
                            f'📄 Text chunks: {response["text_chunks_count"]}'
                        )
                        self.stdout.write("=" * 60)

                    else:
                        self.stdout.write(
                            self.style.ERROR(
                                f'\n❌ Video generation failed: {response["error"]}'
                            )
                        )

                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f"\n❌ Task failed or timed out: {e}")
                    )
                    self.stdout.write("💡 Possible issues:")
                    self.stdout.write("   - MoviePy/OpenCV dependencies missing")
                    self.stdout.write("   - FFmpeg not installed")
                    self.stdout.write("   - Insufficient disk space")
                    self.stdout.write("   - Text too long for processing")
                    self.stdout.write(
                        "\nCheck Celery logs: tail -f logs/celery_worker.log"
                    )

            else:
                self.stdout.write("\n💡 To check the result later, run:")
                self.stdout.write(f"   celery -A repli result {result.id}")
                self.stdout.write("\nOr run with --sync to wait for completion:")
                self.stdout.write("   python manage.py test_video --sync")

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Failed to submit task: {e}"))
            self.stdout.write("Make sure Celery worker is running: ./celery_status.sh")

    def _test_template_video(self, text, title, user_id, wait_for_result):
        """Test template-based video creation"""

        self.stdout.write("\n🎭 Testing template-based video creation...")

        # Create sample slides
        slides_data = [
            {"text": "Welcome to Template Videos!", "duration": 3},
            {"text": text[:80] + ("..." if len(text) > 80 else ""), "duration": 4},
            {"text": "Created with AI-powered video generation", "duration": 3},
        ]

        try:
            result = create_video_template.delay(
                template_name=title,
                slides_data=slides_data,
                user_id=user_id,
                template_style="modern",
            )

            self.stdout.write(f"✅ Template task submitted with ID: {result.id}")

            if wait_for_result:
                self.stdout.write("\n⌛ Creating template video...")

                try:
                    response = result.get(timeout=180)

                    if response["success"]:
                        self.stdout.write(
                            self.style.SUCCESS(
                                "\n🎉 Template video creation successful!"
                            )
                        )

                        self.stdout.write("\n" + "=" * 60)
                        self.stdout.write("🎭 TEMPLATE VIDEO DETAILS:")
                        self.stdout.write("=" * 60)
                        self.stdout.write(f'📂 File path: {response["video_path"]}')
                        self.stdout.write(
                            f'⏱️  Duration: {response["duration"]} seconds'
                        )
                        self.stdout.write(f'📄 Slides: {response["slides_count"]}')
                        self.stdout.write(f'🎨 Style: {response["style"]}')
                        self.stdout.write(
                            f'💾 File size: {response["file_size_mb"]:.2f} MB'
                        )
                        self.stdout.write("=" * 60)

                    else:
                        self.stdout.write(
                            self.style.ERROR(
                                f'\n❌ Template video failed: {response["error"]}'
                            )
                        )

                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f"\n❌ Template task failed: {e}")
                    )

            else:
                self.stdout.write(f"\nCheck result: celery -A repli result {result.id}")

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Failed to submit template task: {e}")
            )

        self.stdout.write(self.style.SUCCESS("\n🚀 Video testing completed!"))
