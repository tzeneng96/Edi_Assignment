from django.shortcuts import render
from rest_framework.permissions import AllowAny

# Create your views here.
from rest_framework import viewsets
from .models import Employee, Team, TeamLeader, TeamEmployee, WorkArrangement
from .serializers import (
    EmployeeSerializer, TeamSerializer, TeamLeaderSerializer, 
    TeamEmployeeSerializer, WorkArrangementSerializer
)

class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer

class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer

class TeamLeaderViewSet(viewsets.ModelViewSet):
    queryset = TeamLeader.objects.all()
    serializer_class = TeamLeaderSerializer

class TeamEmployeeViewSet(viewsets.ModelViewSet):
    queryset = TeamEmployee.objects.all()
    serializer_class = TeamEmployeeSerializer

class WorkArrangementViewSet(viewsets.ModelViewSet):
    queryset = WorkArrangement.objects.all()
    serializer_class = WorkArrangementSerializer
