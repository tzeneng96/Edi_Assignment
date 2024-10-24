from decimal import Decimal
from django.db import models
from django.forms import ValidationError

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
    hourly_rate = models.DecimalField(max_digits=6, decimal_places=2)
    is_team_leader = models.BooleanField(default=False)

    def calculate_monthly_pay(self):
        """Calculate monthly pay with a 10% bonus if
        the employee is a team leader."""
        total_pay = Decimal('0.00')
        for arrangement in self.work_arrangements.all():
            # Monthly hours based on percentage
            hours_worked = 40 * (arrangement.percentage / Decimal('100')) * 4
            pay = Decimal(self.hourly_rate) * hours_worked
            if self.is_team_leader:
                pay *= Decimal('1.10')  # 10% bonus for team leaders

            total_pay += pay

        return total_pay

    def __str__(self):
        return f"{self.name} ({self.employee_id})"


class TeamLeader(models.Model):
    """Represents a team leader, who is also an employee."""
    employee = models.OneToOneField(Employee, related_name='leader_info',
                                    on_delete=models.CASCADE)

    def __str__(self):
        return f"Leader: {self.employee.name} - {self.employee.is_team_leader}"


class TeamEmployee(models.Model):
    """Represents employees belonging to a specific team."""
    team = models.ForeignKey(Team, related_name='team_employees',
                             on_delete=models.CASCADE)
    employee = models.ForeignKey(Employee, related_name='team_membership',
                                 on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.employee.name} in {self.team.name}"


class WorkArrangement(models.Model):
    """Represents the work arrangement of
    an employee(full-time or part-time)."""
    FULL_TIME_HOURS = 40

    employee = models.ForeignKey(Employee, related_name='work_arrangements',
                                 on_delete=models.CASCADE)
    team = models.ForeignKey(Team, related_name='work_arrangements',
                             on_delete=models.PROTECT, default=7)
    # e.g., 75% for part-time
    percentage = models.PositiveIntegerField(default=100)

    def weekly_hours(self):
        """Calculate weekly hours based on the percentage of full-time work."""
        return (self.percentage / 100) * self.FULL_TIME_HOURS

    def save(self, *args, **kwargs):
        # Exclude the current arrangement if it's being updated
        other_arrangement = self.employee.work_arrangements.exclude(pk=self.pk)

        # Sum percentages of other work arrangements
        total_percentage = sum(arrangement.percentage for
                               arrangement in other_arrangement)

        # Add the percentage of the current (new or updated) arrangement
        total_percentage += self.percentage

        if total_percentage > 100:
            raise ValidationError("Total work percentage cannot exceed 100%.")
        super().save(*args, **kwargs)

    def __str__(self):
        if self.percentage == 100:
            arrangement_type = "Full-Time"
        else:
            arrangement_type = f"Part-Time ({self.percentage}%)"
        return f"{self.employee.name}: {arrangement_type}"
