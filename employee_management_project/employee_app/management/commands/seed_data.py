from django.core.management.base import BaseCommand
from django.core.management import call_command
import psycopg2
from employee_app.models import (Employee, Team,
                                 TeamLeader, TeamEmployee, WorkArrangement)
from django.contrib.auth import get_user_model
from django.conf import settings


class Command(BaseCommand):
    help = 'Seeds the database with initial data if empty'

    def handle(self, *args, **options):
        db_name = settings.DATABASES['default']['NAME']

        # Step 1: Create the database if it doesn't exist
        try:
            conn = psycopg2.connect(
                dbname='postgres',
                user=settings.DATABASES['default']['USER'],
                password=settings.DATABASES['default']['PASSWORD'],
                host=settings.DATABASES['default']['HOST'],
                port=settings.DATABASES['default']['PORT'],
            )
            conn.autocommit = True
            cursor = conn.cursor()

            cursor.execute(
                "SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s",
                (db_name, )
            )
            exists = cursor.fetchone()

            if not exists:
                cursor.execute(f'CREATE DATABASE {db_name};')
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Database {db_name} created successfully.'
                    )
                )
        except psycopg2.Error as e:
            self.stdout.write(self.style.ERROR
                              (f'Error creating database: {e}'))
        finally:
            cursor.close()
            conn.close()

        # Step 2: Make migrations
        self.stdout.write(self.style.SUCCESS('Making migrations...'))
        call_command('makemigrations')

        # Step 3: Migrate to apply migrations
        self.stdout.write(self.style.SUCCESS('Applying migrations...'))
        call_command('migrate')

        # Seed superuser
        User = get_user_model()
        if not User.objects.filter(is_superuser=True).exists():
            User.objects.create_superuser('admin',
                                          'admin@example.com', 'password123')
            self.stdout.write(
                self.style.SUCCESS(
                    'Superuser created successfully.'
                )
            )
        else:
            self.stdout.write(self.style.WARNING('Superuser already exists.'))

        # Seed other models as necessary...
        self.seed_initial_data()

    def seed_initial_data(self):
        # Your existing seeding logic for Teams, Employees, etc.
        if Team.objects.count() == 0:
            Team.objects.create(name='Development')
            Team.objects.create(name='Marketing')
            self.stdout.write(self.style.SUCCESS('Created teams'))

        if Employee.objects.count() == 0:
            team = Team.objects.first()  # Get the first team
            emp1 = Employee.objects.create(
                name='Alice',
                employee_id='E101',
                hourly_rate=30.0
            )
            emp2 = Employee.objects.create(
                name='Bob',
                employee_id='E102',
                hourly_rate=25.0
            )
            self.stdout.write(self.style.SUCCESS('Created employees'))

        if TeamLeader.objects.count() == 0:
            # Get the first employee
            emp1 = Employee.objects.first()
            # Assign the first employee as Team Leader
            TeamLeader.objects.create(employee=emp1)
            self.stdout.write(self.style.SUCCESS('Created team leader'))

        if WorkArrangement.objects.count() == 0:
            emp1 = Employee.objects.first()  # Get the first employee
            emp2 = Employee.objects.last()   # Get the last employee
            # Full-time for Alice
            WorkArrangement.objects.create(employee=emp1, percentage=100)
            # Part-time for Bob
            WorkArrangement.objects.create(employee=emp2, percentage=75)
            self.stdout.write(self.style.SUCCESS('Created work arrangements'))

        if TeamEmployee.objects.count() == 0:
            team = Team.objects.first()  # Get the first team
            emp1 = Employee.objects.first()  # Get the first employee
            emp2 = Employee.objects.last()   # Get the last employee
            # Add Alice to the team
            TeamEmployee.objects.create(team=team, employee=emp1)
            # Add Bob to the team
            TeamEmployee.objects.create(team=team, employee=emp2)
            self.stdout.write(self.style.SUCCESS('Created team employees'))
