from decimal import Decimal
from django.db import IntegrityError
from django.forms import ValidationError
from django.test import TestCase

from employee_app.models import (
    Employee, Team, TeamLeader, TeamEmployee, WorkArrangement
)
from employee_app.serializers import (
    EmployeeSerializer, TeamSerializer, WorkArrangementSerializer,
    TeamLeaderSerializer, TeamEmployeeSerializer
)

class TeamModelTest(TestCase):
    def test_create_team(self):
        #Create a team instance
        team = Team.objects.create(
            name = "Developer"
        )
        #Check if team name is correct
        self.assertEqual(team.name, "Developer")
        #Check if string representation of the team
        self.assertEqual(str(team), "Developer")
        #Ensure the team was saved to the database
        self.assertIsNotNone(team.id)

class EmployeeModelTest(TestCase):
    def setUp(self):
        self.team = Team.objects.create(
            name = "Marketing"
        )
        self.employee = Employee.objects.create(
            name = 'John Doe',
            employee_id = 'E17006840',
            team = self.team,
            hourly_rate = 25.00,
            is_team_leader = False
        )
        WorkArrangement.objects.create(
            employee = self.employee,
            percentage = 100
        )
    
    def test_calculate_full_time_monthly_pay(self):
        expected_salary = self.employee.hourly_rate * 160
        self.assertEqual(self.employee.calculate_monthly_pay(), expected_salary)
    
    def test_calculate_part_time_monthly_pay(self):
        WorkArrangement.objects.filter(employee=self.employee).delete()
        WorkArrangement.objects.create(
            employee = self.employee,
            percentage = 75
        )
        expected_salary = self.employee.hourly_rate * 160 * 0.75
        self.assertEqual(self.employee.calculate_monthly_pay(), expected_salary)

    def test_calculate_leader_monthly_pay(self):
        self.employee.is_team_leader = True
        self.employee.save()
        expected_salary = self.employee.hourly_rate * 160 * 1.10
        self.assertEqual(self.employee.calculate_monthly_pay(), expected_salary)

    def test_calculate_monthly_pay_multiple_work_arrangement(self):
        WorkArrangement.objects.filter(employee=self.employee).delete()
        WorkArrangement.objects.create(
            employee = self.employee,
            percentage = 50
        )
        WorkArrangement.objects.create(
            employee = self.employee,
            percentage = 30
        )
        total_working_percentage = sum(arrangement.percentage for arrangement in self.employee.work_arrangements.all())
        expected_salary = self.employee.hourly_rate * 160 * (total_working_percentage/100)
        self.assertEqual(self.employee.calculate_monthly_pay(),expected_salary)

    def test_work_arrangement_exceed_limit(self):
        arrangement = WorkArrangement(employee=self.employee, percentage=30)
        with self.assertRaises(ValidationError):
            arrangement.save()

    def test_create_employee_without_team(self):
        with self.assertRaises(IntegrityError):
            new_employee = Employee.objects.create(
                name='Jane Doe', 
                employee_id='E17006841', 
                hourly_rate=20.00,
                is_team_leader = False
            )

            

    def test_employee_str(self):
        expected_str = "John Doe (E17006840)" 
        self.assertEqual(str(self.employee), expected_str)

class TeamLeaderModelTest(TestCase):
    def setUp(self):
        team = Team.objects.create(
            name = "Development"
        )
        self.employee = Employee.objects.create(
            name = 'John Doe',
            employee_id = 'E17006840',
            team = team,
            hourly_rate = 25.00,
            is_team_leader = True
        )
        self.leader = TeamLeader.objects.create(
            employee = self.employee
        )
        self.assertIsNotNone(self.id)
        self.assertTrue(self.employee.is_team_leader)

    # Test one to one relationship constraint
    def test_employee_cannot_be_assigned_twice_as_leader(self):
        with self.assertRaises(IntegrityError):
            TeamLeader.objects.create(employee=self.employee) 
    
    def test_deleting_team_leader_does_not_delete_employee(self):
        """Ensure that deleting the team leader does not delete the employee."""
        # Verify both employee and team leader exist
        self.assertEqual(Employee.objects.count(), 1)
        self.assertEqual(TeamLeader.objects.count(), 1)

        # Delete the team leader
        self.leader.delete()

        # Verify that the employee still exists
        self.assertEqual(Employee.objects.count(), 1)  # Employee is still in the DB
        self.assertEqual(TeamLeader.objects.count(), 0)  # TeamLeader is deleted

    def test_deleting_employee_deletes_team_leader(self):
        """Ensure that deleting the employee also deletes the team leader."""
        # Verify both employee and team leader exist
        self.assertEqual(Employee.objects.count(), 1)
        self.assertEqual(TeamLeader.objects.count(), 1)

        # Delete the employee
        self.employee.delete()

        # Verify both the employee and the team leader are deleted
        self.assertEqual(Employee.objects.count(), 0)
        self.assertEqual(TeamLeader.objects.count(), 0)

    def test_team_leader_str(self):
        expected_str = "Leader: John Doe - Development"
        self.assertEqual(str(self.leader), expected_str)
    
    def test_employee_without_leader_has_no_leader_info(self):
        new_employee = Employee.objects.create(
            name='Jane Doe', 
            employee_id='E17006841', 
            team=self.employee.team, 
            hourly_rate=20.00,
            is_team_leader = False
        )
        with self.assertRaises(TeamLeader.DoesNotExist):
            new_employee.leader_info


class TeamEmployeeModelTest(TestCase):
    def setUp(self):
        self.team = Team.objects.create(
            name = "Development"
        )
        self.employee = Employee.objects.create(
            name='John Doe', 
            employee_id='E17006840', 
            team=self.team, 
            hourly_rate=20.00,
            is_team_leader = False
        )
    
    def test_create_team_employee(self):
        """Ensure that a TeamEmployee instance can be created successfully."""
        team_employee = TeamEmployee.objects.create(team=self.team, employee=self.employee)
        self.assertIsNotNone(team_employee.id)  # Ensure the TeamEmployee was created
        self.assertEqual(team_employee.team, self.team)  # Check if the team is assigned correctly
        self.assertEqual(team_employee.employee, self.employee)  # Check if the employee is assigned correctly


    def test_delete_team_employee_does_not_delete_team_or_employee(self):
        team_employee = TeamEmployee.objects.create(team=self.team, employee=self.employee)
        self.assertEqual(Employee.objects.count(),1)
        self.assertEqual(Team.objects.count(), 1)
        self.assertEqual(TeamEmployee.objects.count(), 1)

        team_employee.delete()

        self.assertEqual(Employee.objects.count(),1)
        self.assertEqual(Team.objects.count(), 1)
        self.assertEqual(TeamEmployee.objects.count(), 0)

    def test_delete_team_delete_team_employee(self):
        team_employee = TeamEmployee.objects.create(team=self.team, employee=self.employee)  # Create association

        self.assertEqual(Team.objects.count(), 1)

        self.team.delete()

        self.assertEqual(TeamEmployee.objects.count(), 0)

    def test_delete_employee_delete_team_employee(self):
        team_employee = TeamEmployee.objects.create(team=self.team, employee=self.employee)  # Create association

        self.assertEqual(Employee.objects.count(), 1)

        self.employee.delete()

        self.assertEqual(TeamEmployee.objects.count(), 0)

    def test_team_employee_str(self):
        team_employee = TeamEmployee.objects.create(team=self.team, employee=self.employee)  # Create association

        expected_str = "John Doe in Development"
        self.assertEqual(str(team_employee), expected_str)


class WorkArrangementTest(TestCase):
    def setUp(self):
        team = Team.objects.create(
            name = "Engineering"
        )
        self.employee = Employee.objects.create(
            name='John Doe', 
            employee_id='E17006840', 
            team=team, 
            hourly_rate=20.00,
            is_team_leader = False
        )
        self.FULL_TIME_HOURS = 40
        
    
    def test_single_valid_work_arrangement_creation(self):
        """Test creating a single valid work arrangement (100%)."""
        work_arrangement = WorkArrangement.objects.create(
            employee = self.employee,
            percentage = 100
        )

        self.assertIsNotNone(work_arrangement.id)
        self.assertEqual(work_arrangement.employee, self.employee)

    def test_multiple_valid_work_arrangement_creation(self):
        """Test creating a multiple valid work arrangement (100%)."""
        WorkArrangement.objects.create(
            employee = self.employee,
            percentage = 30
        )
        work_arrangement = WorkArrangement(employee = self.employee, percentage = 60)
        try:
            work_arrangement.save()
        except ValidationError:
            self.fail("Valid arrangements raised ValidationError unexpectedly.")

    def test_weekly_hours_calculation(self):

        work_arrangement = WorkArrangement.objects.create(
            employee = self.employee,
            percentage = 40
        )

        expected_weekly_hours = 40 * (work_arrangement.percentage/ 100)
        self.assertEqual(work_arrangement.percentage/ 100 * self.FULL_TIME_HOURS, expected_weekly_hours)

    def test_invalid_percentage_work_arrangement_creation(self):
        with self.assertRaises(IntegrityError):
            work_arrangement = WorkArrangement.objects.create(
                employee = self.employee,
                percentage = -10
            )
    
    def test_work_percentage_exceed_limit(self):
        WorkArrangement.objects.create(employee = self.employee, percentage = 90)
        work_arrangement = WorkArrangement(employee = self.employee,percentage = 30)
        
        with self.assertRaises(ValidationError):
            work_arrangement.save()


    def test_work_arrangement_str(self):
        work_arrangement = WorkArrangement.objects.create(
            employee = self.employee,
            percentage = 100
        )
        expected_str = "John Doe: Full-Time "
            
class TeamSerializerTest(TestCase):
    def test_team_serializer(self):
        team = Team.objects.create(name= "Development")
        serializer = TeamSerializer(team)
        expected_data = {'id':team.id, 'name':team.name}
        self.assertEqual(serializer.data, expected_data)

class WorkArrangementSerializerTest(TestCase):
    def setUp(self):
        self.team = Team.objects.create(name= "Development")
        self.employee = Employee.objects.create(
            name = "John Doe",
            employee_id = "E17006840",
            team = self.team,
            hourly_rate = 20,
            is_team_leader = False
        )
    
    def test_work_arrangement_serialization(self):
        work_arrangement = WorkArrangement.objects.create(
            employee = self.employee,
            percentage = 100
        )
        serializer = WorkArrangementSerializer(work_arrangement)
        expected_data = {
            'id': work_arrangement.id,
            'employee': self.employee.id,
            'percentage': 100,
            'weekly_hours': work_arrangement.weekly_hours()
        }
        self.assertEqual(serializer.data, expected_data)
    
    def test_work_arrangement_validation(self):
        with self.assertRaises(ValidationError):
            WorkArrangement.objects.create(
                employee = self.employee,
                percentage = 120
            )
    
    def test_weekly_hours_calculation(self):
        work_arrangement = WorkArrangement.objects.create(
            employee = self.employee,
            percentage = 50
        )
        serializer = WorkArrangementSerializer(work_arrangement)
        expected_weekly_hours = 40.0 * (50 / 100)
        self.assertEqual(serializer.data['weekly_hours'], expected_weekly_hours)
        

class EmployeeSerializerTestI(TestCase):
    def setUp(self):
        self.team = Team.objects.create(
            name = "Development"
        )
        self.employee = Employee.objects.create(
            name = "John Doe",
            employee_id = "E17006840",
            team = self.team,
            hourly_rate = 20,
            is_team_leader = False
        )
        self.work_arrangement = WorkArrangement.objects.create(
            employee = self.employee,
            percentage = 80
        )
        
    def test_employee_serialization(self):
        serializer = EmployeeSerializer(self.employee)
        expected_data = {
            'id': self.employee.id,
            'name': self.employee.name,
            'employee_id': self.employee.employee_id,
            'team': self.team.id,
            'team_name': self.team.name,
            'hourly_rate': "20.00",
            'is_team_leader': self.employee.is_team_leader,
            'work_arrangements': [WorkArrangementSerializer(self.work_arrangement).data],
            'monthly_pay': self.employee.calculate_monthly_pay()
            }
        self.assertEqual(serializer.data, expected_data)

class TeamLeaderSerializerTest(TestCase):
    def setUp(self):
        self.team = Team.objects.create(
            name = 'Development'
        )
        self.employee = Employee.objects.create(
            name = "John Doe",
            employee_id = "E17006840",
            team = self.team,
            hourly_rate = 20,
            is_team_leader = True
        )
        self.team_leader = TeamLeader.objects.create(
            employee = self.employee
        )
    
    def team_leader_serialization(self):
        serializer = TeamEmployeeSerializer(self.team_leader)
        expected_data = {
            'id': self.team_leader.id,
            'employee': self.employee.id,
            'employee_details': EmployeeSerializer(self.employee).data
        }
        self.assertEqual(serializer.data, expected_data)

class TeamEmployeeSerializerTest(TestCase):
    def setUp(self):
        self.team = Team.objects.create(
            name = 'Development'
        )
        self.employee = Employee.objects.create(
            name = "John Doe",
            employee_id = "E17006840",
            team = self.team,
            hourly_rate = 20,
            is_team_leader = True,
        )
        self.team_employee = TeamEmployee.objects.create(
            employee = self.employee,
            team = self.team
        )

    def test_team_employee_serialization(self):
        serializer = TeamEmployeeSerializer(self.team_employee)
        expected_data = {
            'id': self.team_employee.id,
            'team': self.team.id,
            'employee': self.employee.id,
            'team_name': self.team.name,
            'employee_name': self.employee.name
        }
        self.assertEqual(serializer.data, expected_data)

        