from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import (
    EmployeeViewSet, TeamViewSet, TeamLeaderViewSet,
    TeamEmployeeViewSet, WorkArrangementViewSet
)

# Use DRF's router to generate routes automatically
router = DefaultRouter()
router.register(r'employees',
                EmployeeViewSet, basename='employee')
router.register(r'teams',
                TeamViewSet, basename='team')
router.register(r'team-leaders',
                TeamLeaderViewSet, basename='teamleader')
router.register(r'team-employees',
                TeamEmployeeViewSet, basename='teamemployee')
router.register(r'work-arrangements',
                WorkArrangementViewSet, basename='workarrangement')

# Include the generated routes in urlpatterns
urlpatterns = [
    path('', include(router.urls)),
]
