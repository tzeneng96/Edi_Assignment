# Create your views here.
from rest_framework import viewsets
from .models import Employee, Team, TeamLeader, TeamEmployee, WorkArrangement
from .serializers import (
    EmployeeSerializer, TeamSerializer, TeamLeaderSerializer,
    TeamEmployeeSerializer, WorkArrangementSerializer
)


class EmployeeViewSet(viewsets.ModelViewSet):
    """Viewset to handle CRUD operations for employee instances"""
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer


class TeamViewSet(viewsets.ModelViewSet):
    """Viewset to handle CRUD operations for team instances"""
    queryset = Team.objects.all()
    serializer_class = TeamSerializer


class TeamLeaderViewSet(viewsets.ModelViewSet):
    """Viewset to handle CRUD operations for team leader instances"""
    queryset = TeamLeader.objects.all()
    serializer_class = TeamLeaderSerializer


class TeamEmployeeViewSet(viewsets.ModelViewSet):
    """Viewset to handle CRUD operations for team employee instances"""
    queryset = TeamEmployee.objects.all()
    serializer_class = TeamEmployeeSerializer


class WorkArrangementViewSet(viewsets.ModelViewSet):
    """Viewset to handle CRUD operations for work management instances"""
    queryset = WorkArrangement.objects.all()
    serializer_class = WorkArrangementSerializer
