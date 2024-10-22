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
        fields = ['id', 'employee', 'percentage', 'weekly_hours']

    def get_weekly_hours(self, obj):
        return obj.weekly_hours()  # Calls the model method to calculate weekly hours


class EmployeeSerializer(serializers.ModelSerializer):
    """Serializer for Employee model."""
    
    team_name = serializers.ReadOnlyField(source='team.name')  # Get team name as read-only
    work_arrangements = WorkArrangementSerializer(many=True, read_only=True)  # Nested serializer for arrangements
    monthly_pay = serializers.SerializerMethodField()  # Read-only calculated pay

    class Meta:
        model = Employee
        fields = [
            'id', 'name', 'employee_id', 'team', 'team_name', 
            'hourly_rate', 'is_team_leader', 'work_arrangements', 'monthly_pay'
        ]

    def get_monthly_pay(self, obj):
        # Assuming a standard of 160 working hours per month (40h/week * 4 weeks)
        return obj.calculate_monthly_pay()


class TeamLeaderSerializer(serializers.ModelSerializer):
    """Serializer for TeamLeader model."""
    
    employee_details = EmployeeSerializer(source='employee', read_only=True)  # Nested employee details

    class Meta:
        model = TeamLeader
        fields = ['id', 'employee', 'employee_details']


class TeamEmployeeSerializer(serializers.ModelSerializer):
    """Serializer for TeamEmployee model."""
    
    employee_name = serializers.ReadOnlyField(source='employee.name')  # Read-only employee name
    team_name = serializers.ReadOnlyField(source='team.name')  # Read-only team name

    class Meta:
        model = TeamEmployee
        fields = ['id', 'team', 'employee', 'team_name', 'employee_name']
