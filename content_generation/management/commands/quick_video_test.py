import os
import tempfile

from django.conf import settings
from django.core.management.base import BaseCommand
from PIL import Image, ImageDraw, ImageFont


class Command(BaseCommand):
    help = "Quick test of video generation dependencies and basic functionality"

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("🧪 Quick Video Generation Test"))

        # Test 1: Check dependencies
        self.stdout.write("\n📦 Testing Dependencies:")

        try:
            import moviepy.editor as mp

            self.stdout.write("✅ MoviePy imported successfully")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ MoviePy failed: {e}"))
            return

        try:
            import cv2

            self.stdout.write("✅ OpenCV imported successfully")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ OpenCV failed: {e}"))
            return

        try:
            from PIL import Image, ImageDraw, ImageFont

            self.stdout.write("✅ PIL imported successfully")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ PIL failed: {e}"))
            return

        # Test 2: Create a simple test image
        self.stdout.write("\n🖼️  Testing Image Generation:")

        try:
            # Create a simple test image
            img = Image.new("RGB", (400, 300), color="darkblue")
            draw = ImageDraw.Draw(img)

            # Add text (use default font since custom fonts might not be available)
            text = "Test Video Frame"
            bbox = draw.textbbox((0, 0), text)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]

            x = (400 - text_width) // 2
            y = (300 - text_height) // 2
            draw.text((x, y), text, fill="white")

            # Save test image
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                img.save(tmp.name)
                test_image_path = tmp.name

            self.stdout.write(f"✅ Test image created: {test_image_path}")

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Image creation failed: {e}"))
            return

        # Test 3: Create a very simple video
        self.stdout.write("\n🎬 Testing Basic Video Creation:")

        try:
            from moviepy.editor import ImageClip

            # Create a simple 2-second video from the test image
            clip = ImageClip(test_image_path).set_duration(2)

            with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
                test_video_path = tmp.name

            self.stdout.write("⏳ Rendering test video (this should be quick)...")

            clip.write_videofile(
                test_video_path,
                fps=1,  # Very low FPS for speed
                codec="libx264",
                verbose=False,
                logger=None,
            )

            clip.close()

            # Check if video was created
            if os.path.exists(test_video_path) and os.path.getsize(test_video_path) > 0:
                file_size = os.path.getsize(test_video_path) / 1024  # KB
                self.stdout.write(f"✅ Test video created: {test_video_path}")
                self.stdout.write(f"📄 File size: {file_size:.1f} KB")
            else:
                self.stdout.write(
                    self.style.ERROR("❌ Video file was not created or is empty")
                )

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Video creation failed: {e}"))
            # Print detailed error for debugging
            import traceback

            self.stdout.write("\nDetailed error:")
            self.stdout.write(traceback.format_exc())

        # Test 4: Test text processing
        self.stdout.write("\n📝 Testing Text Processing:")

        try:
            from content_generation.video_tasks import _split_text_into_chunks

            test_text = "This is a test of the text chunking functionality that splits long text into smaller pieces suitable for video slides."
            chunks = _split_text_into_chunks(test_text, max_chars=30)

            self.stdout.write(f"✅ Text split into {len(chunks)} chunks:")
            for i, chunk in enumerate(chunks, 1):
                self.stdout.write(f'  {i}. "{chunk}"')

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Text processing failed: {e}"))

        # Clean up test files
        try:
            if "test_image_path" in locals():
                os.unlink(test_image_path)
            if "test_video_path" in locals() and os.path.exists(test_video_path):
                os.unlink(test_video_path)
        except:
            pass

        # Test 5: Check Celery task registration
        self.stdout.write("\n🔧 Testing Celery Integration:")

        try:
            from content_generation.video_tasks import generate_video_from_text

            self.stdout.write(f"✅ Video task found: {generate_video_from_text}")

            # Check if we can create a task (don't run it)
            task_signature = generate_video_from_text.s("Test")
            self.stdout.write(f"✅ Task signature created: {task_signature}")

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Celery integration failed: {e}"))

        self.stdout.write(self.style.SUCCESS("\n🎉 Quick test completed!"))
        self.stdout.write("\n💡 If all tests pass, video generation should work.")
        self.stdout.write(
            "   The full video generation may take 30-120 seconds depending on content."
        )
        self.stdout.write("\n🚀 To test full video generation:")
        self.stdout.write(
            '   python manage.py test_video --sync --duration=3 "Short test"'
        )
