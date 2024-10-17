from django.core.management.base import BaseCommand
from employee_app.models import Employee, Team, TeamLeader, TeamEmployee, WorkArrangement

class Command(BaseCommand):
    help = 'Seeds the database with initial data if empty'

    def handle(self, *args, **options):
        # Seed Teams
        if Team.objects.count() == 0:
            team_a = Team.objects.create(name='Development')
            team_b = Team.objects.create(name='Marketing')
            self.stdout.write(self.style.SUCCESS('Created teams'))

        # Seed Employees
        if Employee.objects.count() == 0:
            team = Team.objects.first()  # Get the first team
            emp1 = Employee.objects.create(name='Alice', employee_id='E101', team=team, hourly_rate=30.0)
            emp2 = Employee.objects.create(name='Bob', employee_id='E102', team=team, hourly_rate=25.0)
            self.stdout.write(self.style.SUCCESS('Created employees'))

        # Seed Team Leaders
        if TeamLeader.objects.count() == 0:
            team_leader = TeamLeader.objects.create(employee=emp1)  # Assign Alice as Team Leader
            self.stdout.write(self.style.SUCCESS('Created team leader'))

        # Seed Work Arrangements
        if WorkArrangement.objects.count() == 0:
            WorkArrangement.objects.create(employee=emp1, percentage=100)  # Full-time for Alice
            WorkArrangement.objects.create(employee=emp2, percentage=75)   # Part-time for Bob
            self.stdout.write(self.style.SUCCESS('Created work arrangements'))

        # Seed Team Employees
        if TeamEmployee.objects.count() == 0:
            team = Team.objects.first()  # Get the first team
            TeamEmployee.objects.create(team=team, employee=emp1)  # Add Alice to the team
            TeamEmployee.objects.create(team=team, employee=emp2)  # Add Bob to the team
            self.stdout.write(self.style.SUCCESS('Created team employees'))

        self.stdout.write(self.style.SUCCESS('Seeding completed'))
