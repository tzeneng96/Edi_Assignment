from rest_framework import serializers
from .models import Employee, Team, TeamLeader, TeamEmployee, WorkArrangement


class TeamSerializer(serializers.ModelSerializer):
    """Serializer for Team model."""
    class Meta:
        model = Team
        fields = ['id', 'name']


class WorkArrangementSerializer(serializers.ModelSerializer):
    """Serializer for WorkArrangement model."""
    weekly_hours = serializers.SerializerMethodField()

    class Meta:
        model = WorkArrangement
        fields = ['id', 'employee', 'team', 'percentage', 'weekly_hours']

    def get_weekly_hours(self, obj):
        # Calls the model method to calculate weekly hours
        return obj.weekly_hours()


class EmployeeSerializer(serializers.ModelSerializer):
    """Serializer for Employee model."""
    # Method field to get teams
    teams = serializers.SerializerMethodField()
    # Nested serializer for arrangements
    work_arrangements = WorkArrangementSerializer(many=True,
                                                  read_only=True)
    # Read-only calculated pay
    monthly_pay = serializers.SerializerMethodField()

    class Meta:
        model = Employee
        fields = [
            'id', 'name', 'employee_id', 'teams',
            'hourly_rate', 'is_team_leader', 'work_arrangements', 'monthly_pay'
        ]

    def get_monthly_pay(self, obj):
        # Assuming a standard of 160 working hours per month
        # (40h/week * 4 weeks)
        return obj.calculate_monthly_pay()

    def get_teams(self, obj):
        # Get all teams associated with the employee through TeamEmployee
        return [
            {
                'id': team_employee.team.id,
                'name': team_employee.team.name
            }
            for team_employee in obj.team_membership.all()
        ]


class TeamLeaderSerializer(serializers.ModelSerializer):
    """Serializer for TeamLeader model."""
    # Nested employee details
    employee_details = EmployeeSerializer(source='employee',
                                          read_only=True)

    class Meta:
        model = TeamLeader
        fields = ['id', 'employee', 'employee_details']


class TeamEmployeeSerializer(serializers.ModelSerializer):
    """Serializer for TeamEmployee model."""
    # Read-only employee name
    employee_name = serializers.ReadOnlyField(source='employee.name')
    # Read-only team name
    team_name = serializers.ReadOnlyField(source='team.name')

    class Meta:
        model = TeamEmployee
        fields = ['id', 'team', 'employee', 'team_name', 'employee_name']
