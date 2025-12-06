from django.core.management.base import BaseCommand
import os

class Command(BaseCommand):
    help = 'Creates or updates the admin superuser and ensures is_admin is True.'

    def handle(self, *args, **options):
        from bingo_app.models import User
        username = 'angel'
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')
        email = 'angel@example.com'

        if not password:
            self.stdout.write(self.style.ERROR('DJANGO_SUPERUSER_PASSWORD environment variable not set.'))
            return

        # Get or create the user
        user, created = User.objects.get_or_create(username=username)

        if created:
            self.stdout.write(f'Creating account for {username}')
            user.email = email
            user.set_password(password)
        
        # Ensure all admin/superuser flags are set, even for existing user
        user.is_superuser = True
        user.is_staff = True
        user.is_admin = True
        user.save()

        if created:
            self.stdout.write('Superuser created successfully and set as admin.')
        else:
            self.stdout.write(f'User {username} already exists. Updated privileges.')
