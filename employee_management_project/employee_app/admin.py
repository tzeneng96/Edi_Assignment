# Register your models here.
from django.contrib import admin
from .models import Employee, Team, TeamEmployee, TeamLeader, WorkArrangement

admin.site.register(Employee)
admin.site.register(Team)
admin.site.register(TeamEmployee)
admin.site.register(TeamLeader)
admin.site.register(WorkArrangement)
