import time

from django.core.management.base import BaseCommand

from content_generation.tasks import (
    cleanup_old_files,
    generate_content_async,
    process_video_matching,
    test_task,
)


class Command(BaseCommand):
    help = "Test Celery tasks to ensure they are working properly"

    def add_arguments(self, parser):
        parser.add_argument(
            "--task",
            choices=["test", "content", "video", "cleanup", "all"],
            default="all",
            help="Which task to test (default: all)",
        )
        parser.add_argument(
            "--wait",
            action="store_true",
            help="Wait for task completion and show results",
        )

    def handle(self, *args, **options):
        task_type = options["task"]
        wait_for_result = options["wait"]

        self.stdout.write(self.style.SUCCESS("Testing Celery tasks..."))

        results = []

        if task_type in ["test", "all"]:
            self.stdout.write("📋 Running test task...")
            result = test_task.delay()
            results.append(("Test Task", result))

        if task_type in ["content", "all"]:
            self.stdout.write("🤖 Running content generation task...")
            result = generate_content_async.delay(
                "Write a short story about a robot learning to cook", user_id=1
            )
            results.append(("Content Generation", result))

        if task_type in ["video", "all"]:
            self.stdout.write("🎬 Running video processing task...")
            result = process_video_matching.delay("test_video_123")
            results.append(("Video Processing", result))

        if task_type in ["cleanup", "all"]:
            self.stdout.write("🧹 Running cleanup task...")
            result = cleanup_old_files.delay()
            results.append(("File Cleanup", result))

        self.stdout.write(f"\n✅ Submitted {len(results)} tasks")

        if wait_for_result:
            self.stdout.write("\n⏳ Waiting for results...\n")

            for task_name, result in results:
                self.stdout.write(f"Waiting for {task_name}...")
                try:
                    # Wait up to 30 seconds for each task
                    output = result.get(timeout=30)
                    self.stdout.write(self.style.SUCCESS(f"✅ {task_name}: {output}"))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"❌ {task_name} failed: {e}"))

        else:
            self.stdout.write("\nTask IDs:")
            for task_name, result in results:
                self.stdout.write(f"  {task_name}: {result.id}")

            self.stdout.write("\nTo check results later, use:")
            self.stdout.write("  celery -A repli result <task_id>")
            self.stdout.write("  python manage.py test_celery --wait")

        self.stdout.write(self.style.SUCCESS("\n🎉 Task testing completed!"))
