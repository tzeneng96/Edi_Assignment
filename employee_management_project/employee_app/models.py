from decimal import Decimal
from django.db import models

# Create your models here.
class Team(models.Model):
    """Represents a team in the company."""
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Employee(models.Model):
    """Represents an employee in the company."""
    name = models.CharField(max_length=100)
    employee_id = models.CharField(max_length=10, unique=True)
    team = models.ForeignKey(Team, related_name='employees', on_delete=models.CASCADE)
    hourly_rate = models.DecimalField(max_digits=6, decimal_places=2)
    is_team_leader = models.BooleanField(default=False)

    def calculate_monthly_pay(self, hours_worked):
        """Calculate monthly pay with a 10% bonus if the employee is a team leader."""
        total_pay = Decimal('0.00')
        for arrangement in self.work_arrangements.all():
            hours_worked = 40 * (arrangement.percentage / Decimal('100')) * 4  # Monthly hours based on percentage
            pay = self.hourly_rate * hours_worked
            
            if self.is_team_leader:
                pay *= Decimal('1.10')  # 10% bonus for team leaders

            total_pay += pay

        return total_pay

    def __str__(self):
        return f"{self.name} ({self.employee_id})"


class TeamLeader(models.Model):
    """Represents a team leader, who is also an employee."""
    employee = models.OneToOneField(Employee, related_name='leader_info', on_delete=models.CASCADE)

    def __str__(self):
        return f"Leader: {self.employee.name} - {self.employee.team.name}"


class TeamEmployee(models.Model):
    """Represents employees belonging to a specific team."""
    team = models.ForeignKey(Team, related_name='team_employees', on_delete=models.CASCADE)
    employee = models.ForeignKey(Employee, related_name='team_membership', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.employee.name} in {self.team.name}"


class WorkArrangement(models.Model):
    """Represents the work arrangement of an employee (full-time or part-time)."""
    FULL_TIME_HOURS = 40

    employee = models.ForeignKey(Employee, related_name='work_arrangements', on_delete=models.CASCADE)
    percentage = models.PositiveIntegerField(default=100)  # e.g., 75% for part-time

    def weekly_hours(self):
        """Calculate weekly hours based on the percentage of full-time work."""
        return (self.percentage / 100) * self.FULL_TIME_HOURS

    def __str__(self):
        arrangement_type = "Full-Time" if self.percentage == 100 else f"Part-Time ({self.percentage}%)"
        return f"{self.employee.name}: {arrangement_type}"
