"""
Management command to create an admin user on Koyeb
Usage: python manage.py create_admin --username admin --email admin@example.com --password YourPassword123!
"""
from django.core.management.base import BaseCommand
from accounts.models import User


class Command(BaseCommand):
    help = 'Create a superuser/admin account'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            help='Username for the admin user',
            default='admin'
        )
        parser.add_argument(
            '--email',
            type=str,
            help='Email for the admin user',
            default='admin@example.com'
        )
        parser.add_argument(
            '--password',
            type=str,
            help='Password for the admin user',
            default=None
        )

    def handle(self, *args, **options):
        username = options['username']
        email = options['email']
        password = options['password']

        # Check if user already exists
        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.WARNING(f'User "{username}" already exists. Skipping creation.')
            )
            return

        # Prompt for password if not provided
        if not password:
            from getpass import getpass
            password = getpass(f'Password for {username}: ')
            password_confirm = getpass('Password (again): ')
            if password != password_confirm:
                self.stdout.write(
                    self.style.ERROR('Passwords do not match. Aborting.')
                )
                return

        # Create superuser
        try:
            user = User.objects.create_superuser(
                username=username,
                email=email,
                password=password,
                role='ADMIN'
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully created admin user "{username}" with email "{email}"'
                )
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating admin user: {str(e)}')
            )

