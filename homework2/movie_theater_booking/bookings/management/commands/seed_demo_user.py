import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    """Create or update the grader's demo user from an environment secret."""

    help = "Create or update the demo user using DEMO_PASSWORD."

    def handle(self, *args, **options):
        password = os.environ.get("DEMO_PASSWORD")
        if not password:
            raise CommandError("DEMO_PASSWORD environment variable is required.")

        user, created = get_user_model().objects.get_or_create(username="demo")
        user.set_password(password)
        user.save(update_fields=["password"])

        action = "Created" if created else "Updated"
        self.stdout.write(self.style.SUCCESS(f"{action} demo user."))
