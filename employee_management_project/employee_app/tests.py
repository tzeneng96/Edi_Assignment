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
        """Create a team instance"""
        team = Team.objects.create(
            name="Developer"
        )
        # Check if team name is correct
        self.assertEqual(team.name, "Developer")
        # Check if string representation of the team
        self.assertEqual(str(team), "Developer")
        # Ensure the team was saved to the database
        self.assertIsNotNone(team.id)


class EmployeeModelTest(TestCase):
    def setUp(self):
        """Create team, work arrangement and employee instance"""
        self.team = Team.objects.create(
            name="Marketing"
        )
        self.employee = Employee.objects.create(
            name='John Doe',
            employee_id='E17006840',
            hourly_rate=25.00,
            is_team_leader=False
        )
        WorkArrangement.objects.create(
            employee=self.employee,
            percentage=100
        )

    def test_calculate_full_time_monthly_pay(self):
        """Calculate employee monthly pay, full time weekly is 40 hrs"""
        expected_salary = self.employee.hourly_rate * 160
        self.assertEqual(self.employee.calculate_monthly_pay(),
                         expected_salary)

    def test_calculate_part_time_monthly_pay(self):
        """Calculate employee part time monthly pay,
           single work arrangement with valid percentage"""
        # Delete current full time work arrangement
        WorkArrangement.objects.filter(employee=self.employee).delete()
        WorkArrangement.objects.create(
            employee=self.employee,
            percentage=75
        )
        # 75/100 (percentage) * 4 * 40 (full time)
        expected_salary = self.employee.hourly_rate * 160 * 0.75
        self.assertEqual(self.employee.calculate_monthly_pay(),
                         expected_salary)

    def test_calculate_leader_monthly_pay(self):
        """Calculate monthly pay for a full time leader"""
        # Change the current employee to leader
        self.employee.is_team_leader = True
        # Save the change before calculate the monthly payment
        self.employee.save()
        # 10% bonus for leader
        expected_salary = self.employee.hourly_rate * 160 * 1.10
        self.assertEqual(self.employee.calculate_monthly_pay(),
                         expected_salary)

    def test_calculate_monthly_pay_multiple_work_arrangement(self):
        """Calculate monthly payment for a part time employee with
           multiple valid work arrangement"""
        # Delete current full time work arrangement
        WorkArrangement.objects.filter(employee=self.employee).delete()
        # Create 2 valid work arrangements, altogether 80% work arrangement
        WorkArrangement.objects.create(
            employee=self.employee,
            percentage=50
        )
        WorkArrangement.objects.create(
            employee=self.employee,
            percentage=30
        )
        # Loop through all work arrangement percentage
        total_working_percentage = sum(
            arrangement.percentage
            for arrangement in self.employee.work_arrangements.all()
        )
        expected_salary = (
            self.employee.hourly_rate * 160 * (total_working_percentage / 100)
        )
        
        self.assertEqual(self.employee.calculate_monthly_pay(),
                         Decimal(expected_salary))

    def test_work_arrangement_exceed_limit(self):
        """Add work arrangements to a full time worker,
        130% will throw validation error when saving"""
        arrangement = WorkArrangement(employee=self.employee, percentage=30)
        with self.assertRaises(ValidationError):
            arrangement.save()

    def test_employee_str(self):
        # Check if string represent an employee
        expected_str = "John Doe (E17006840)"
        self.assertEqual(str(self.employee), expected_str)


class TeamLeaderModelTest(TestCase):
    # Create instance for team employee and leader
    def setUp(self):
        self.employee = Employee.objects.create(
            name='John Doe',
            employee_id='E17006840',
            hourly_rate=25.00,
            is_team_leader=True
        )
        self.leader = TeamLeader.objects.create(
            employee=self.employee
        )
        # Ensure team leader is created with ID
        self.assertIsNotNone(self.id)
        # Ensure created employee is a team leader
        self.assertTrue(self.employee.is_team_leader)

    # Test one to one relationship constraint, an employee cant
    # be add as leader twice (multiple records as leader)
    def test_employee_cannot_be_assigned_twice_as_leader(self):
        with self.assertRaises(IntegrityError):
            TeamLeader.objects.create(employee=self.employee)

    def test_deleting_team_leader_does_not_delete_employee(self):
        """Ensure that deleting the team leader
        does not delete the employee."""
        # Verify both employee and team leader exist
        self.assertEqual(Employee.objects.count(), 1)
        self.assertEqual(TeamLeader.objects.count(), 1)

        # Delete the team leader
        self.leader.delete()

        # Verify that the employee still exists
        # Employee is still in the DB
        self.assertEqual(Employee.objects.count(), 1)
        # TeamLeader is deleted
        self.assertEqual(TeamLeader.objects.count(), 0)

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
        expected_str = "Leader: John Doe - True"
        self.assertEqual(str(self.leader), expected_str)

    def test_employee_without_leader_has_no_leader_info(self):
        new_employee = Employee.objects.create(
            name='Jane Doe',
            employee_id='E17006841',
            hourly_rate=20.00,
            is_team_leader=False
        )
        with self.assertRaises(TeamLeader.DoesNotExist):
            new_employee.leader_info


class TeamEmployeeModelTest(TestCase):
    # Create employee and team instance
    def setUp(self):
        self.team = Team.objects.create(
            name="Development"
        )
        self.employee = Employee.objects.create(
            name='John Doe',
            employee_id='E17006840',
            hourly_rate=20.00,
            is_team_leader=False
        )

    def test_create_team_employee(self):
        """Ensure that a TeamEmployee instance can be created successfully."""
        team_employee = TeamEmployee.objects.create(team=self.team,
                                                    employee=self.employee)
        # Ensure the TeamEmployee was created
        self.assertIsNotNone(team_employee.id)
        # Check if the team is assigned correctly
        self.assertEqual(team_employee.team, self.team)
        # Check if the employee is assigned correctly
        self.assertEqual(team_employee.employee, self.employee)

    def test_delete_team_employee_does_not_delete_team_or_employee(self):
        """Ensure that delete team employee
        does not delete team and employee"""
        team_employee = TeamEmployee.objects.create(team=self.team,
                                                    employee=self.employee)
        # Verify Employee,Team, TeamEmployee is exist
        self.assertEqual(Employee.objects.count(), 1)
        self.assertEqual(Team.objects.count(), 1)
        self.assertEqual(TeamEmployee.objects.count(), 1)

        team_employee.delete()  # Delete team temployee
        # Employee still in DB
        self.assertEqual(Employee.objects.count(), 1)
        # Team still in DB
        self.assertEqual(Team.objects.count(), 1)
        # TeamEmployee is deleted
        self.assertEqual(TeamEmployee.objects.count(), 0)

    def test_delete_team_delete_team_employee(self):
        """Ensure delete Team delete TeamEmployee"""
        # Create association
        TeamEmployee.objects.create(team=self.team,
                                    employee=self.employee)
        # Verify Team and Team Employee is exist
        self.assertEqual(Team.objects.count(), 1)
        self.assertEqual(TeamEmployee.objects.count(), 1)

        self.team.delete()  # Delete team

        self.assertEqual(Team.objects.count(), 0)  # Team is deleted
        # TeamEmployee is deleted
        self.assertEqual(TeamEmployee.objects.count(), 0)

    def test_delete_employee_delete_team_employee(self):
        """Ensure delete Employee delete TeamEmployee"""
        # Create association
        TeamEmployee.objects.create(team=self.team,
                                    employee=self.employee)

        # Verify TeamEmployee and Employee is exist
        self.assertEqual(TeamEmployee.objects.count(), 1)
        self.assertEqual(Employee.objects.count(), 1)
        # Delete employee
        self.employee.delete()
        # Employee is deleted
        self.assertEqual(Employee.objects.count(), 0)
        # TeamEmployee is deleted
        self.assertEqual(TeamEmployee.objects.count(), 0)

    def test_team_employee_str(self):
        """Check if string represent team employee"""
        # Create association
        team_employee = TeamEmployee.objects.create(team=self.team,
                                                    employee=self.employee)
        expected_str = "John Doe in Development"
        self.assertEqual(str(team_employee), expected_str)


class WorkArrangementTest(TestCase):
    # Create instance for employee and team
    def setUp(self):
        Team.objects.create(
            name="Engineering"
        )
        self.employee = Employee.objects.create(
            name='John Doe',
            employee_id='E17006840',
            hourly_rate=20.00,
            is_team_leader=False
        )
        self.FULL_TIME_HOURS = 40

    def test_single_valid_work_arrangement_creation(self):
        """Test creating a single valid work arrangement (100%)."""
        work_arrangement = WorkArrangement.objects.create(
            employee=self.employee,
            percentage=100
        )
        # Ensure work arrangement is created
        self.assertIsNotNone(work_arrangement.id)
        self.assertEqual(work_arrangement.employee, self.employee)

    def test_multiple_valid_work_arrangement_creation(self):
        """Test creating a multiple valid work arrangement (90%)."""
        WorkArrangement.objects.create(
            employee=self.employee,
            percentage=30
        )
        # Create another work arrangement instance
        work_arrangement = WorkArrangement(employee=self.employee,
                                           percentage=60)
        try:
            # New work arrangement should be saved, else throw validation error
            work_arrangement.save()
        except ValidationError:
            self.fail("Valid arrangements raised" +
                      ValidationError + "unexpectedly.")

    def test_weekly_hours_calculation(self):
        """Test calculate weekly working hours for an employee"""
        work_arrangement = WorkArrangement.objects.create(
            employee=self.employee,
            percentage=40
        )
        # Assuming 40 hours full time a week
        expected_weekly_hours = 40 * (work_arrangement.percentage / 100)
        self.assertEqual(work_arrangement.percentage / 100 *
                         self.FULL_TIME_HOURS, expected_weekly_hours)

    def test_invalid_percentage_work_arrangement_creation(self):
        """Test create work arrangement with invalid
          percentage (negative value)"""
        with self.assertRaises(IntegrityError):
            WorkArrangement.objects.create(
                employee=self.employee,
                percentage=-10
            )

    def test_work_percentage_exceed_limit(self):
        """Test create work arrangement with
        invalid percentage (greater than 100)"""
        WorkArrangement.objects.create(employee=self.employee, percentage=90)
        work_arrangement = WorkArrangement(employee=self.employee,
                                           percentage=30)
        # Save second work arrangement which
        # total up > 100 throw validation error
        with self.assertRaises(ValidationError):
            work_arrangement.save()

    def test_work_arrangement_str(self):
        # Check if string represent work arrangement
        work_arrangement = WorkArrangement.objects.create(
            employee=self.employee,
            percentage=100
        )
        expected_str = "John Doe: Full-Time"
        self.assertEqual(str(work_arrangement), expected_str)


class TeamSerializerTest(TestCase):
    """Test to verify the serializer correctly
    serializes a valid Team instance"""
    def test_team_serializer(self):
        team = Team.objects.create(name="Development")
        serializer = TeamSerializer(team)
        expected_data = {'id': team.id, 'name': team.name}
        self.assertEqual(serializer.data, expected_data)

    """Test to ensure the serializer catches a missing name as invalid"""
    def test_team_serializer_missing_name(self):
        invalid_data = {'name': ''}
        serializer = TeamSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('name', serializer.errors)


class WorkArrangementSerializerTest(TestCase):
    """Test suite to verify WorkArrangement serializer behavior."""
    def setUp(self):
        # Create instance for employee and team
        self.team = Team.objects.create(name="Development")
        self.employee = Employee.objects.create(
            name="John Doe",
            employee_id="E17006840",
            hourly_rate=20,
            is_team_leader=False
        )

    def test_work_arrangement_serialization(self):
        # Test to verify the serializer correctly
        # serializes a valid WorkArrangement instance
        work_arrangement = WorkArrangement.objects.create(
            employee=self.employee,
            percentage=100
        )
        serializer = WorkArrangementSerializer(work_arrangement)
        expected_data = {
            'id': work_arrangement.id,
            'employee': self.employee.id,
            'percentage': 100,
            'weekly_hours': work_arrangement.weekly_hours()
        }
        # Verify that the serialized data matches the expected output
        self.assertEqual(serializer.data, expected_data)

    def test_work_arrangement_validation(self):
        # Test to ensure validation error is raised
        # for invalid percentage (>100)
        with self.assertRaises(ValidationError):
            WorkArrangement.objects.create(
                employee=self.employee,
                percentage=120
            )

    def test_weekly_hours_calculation(self):
        # Test to verify correct weekly hours calculation based on percentage
        work_arrangement = WorkArrangement.objects.create(
            employee=self.employee,
            percentage=50
        )
        serializer = WorkArrangementSerializer(work_arrangement)
        expected_weekly_hours = 40.0 * (50 / 100)
        self.assertEqual(serializer.data['weekly_hours'],
                         expected_weekly_hours)


class EmployeeSerializerTestI(TestCase):
    """Test suite to verify Employee serializer behavior."""
    def setUp(self):
        # Create instances for team, employee and work arrangement
        self.team = Team.objects.create(
            name="Development"
        )
        self.employee = Employee.objects.create(
            name="John Doe",
            employee_id="E17006840",
            hourly_rate=20,
            is_team_leader=False
        )
        self.work_arrangement = WorkArrangement.objects.create(
            employee=self.employee,
            percentage=80
        )

    def test_employee_serialization(self):
        # Test to ensure the Employee serializer outputs correct data.
        serializer = EmployeeSerializer(self.employee)

        expected_teams = [
            {
                'id': team_employee.team.id,
                'name': team_employee.team.name
            }
            for team_employee in self.employee.team_membership.all()
        ]
        expected_data = {
            'id': self.employee.id,
            'name': self.employee.name,
            'employee_id': self.employee.employee_id,
            'teams': expected_teams,
            'hourly_rate': "20.00",
            'is_team_leader': self.employee.is_team_leader,
            'work_arrangements':
            [WorkArrangementSerializer(self.work_arrangement).data],
            'monthly_pay': self.employee.calculate_monthly_pay()
        }
        self.assertEqual(serializer.data, expected_data)


class TeamLeaderSerializerTest(TestCase):
    """Test suite to verify Team Leader serializer behavior."""
    def setUp(self):
        self.team = Team.objects.create(
            name='Development'
        )
        self.employee = Employee.objects.create(
            name="John Doe",
            employee_id="E17006840",
            hourly_rate=20,
            is_team_leader=True
        )
        self.team_leader = TeamLeader.objects.create(
            employee=self.employee
        )

    def team_leader_serialization(self):
        # Test to ensure Team Employee Serializer outputs correct data
        serializer = TeamLeaderSerializer(self.team_leader)
        expected_data = {
            'id': self.team_leader.id,
            'employee': self.employee.id,
            'employee_details': EmployeeSerializer(self.employee).data
        }
        self.assertEqual(serializer.data, expected_data)


class TeamEmployeeSerializerTest(TestCase):
    """Test suite to verify Team Employee Serializer behavior"""
    def setUp(self):
        self.team = Team.objects.create(
            name='Development'
        )
        self.employee = Employee.objects.create(
            name="John Doe",
            employee_id="E17006840",
            hourly_rate=20,
            is_team_leader=True,
        )
        self.team_employee = TeamEmployee.objects.create(
            employee=self.employee,
            team=self.team
        )

    def test_team_employee_serialization(self):
        # Test to ensure Team Employee Serializer outputs correct data
        serializer = TeamEmployeeSerializer(self.team_employee)
        expected_data = {
            'id': self.team_employee.id,
            'team': self.team.id,
            'employee': self.employee.id,
            'team_name': self.team_employee.team.name,
            'employee_name': self.employee.name
        }
        self.assertEqual(serializer.data, expected_data)
