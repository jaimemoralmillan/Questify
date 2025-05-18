from django.contrib import admin
from .models import Task, UserProfile, Achievement, UserAchievement # Add Achievement, UserAchievement

# Register your models here.
admin.site.register(Task)
admin.site.register(UserProfile)
admin.site.register(Achievement)
admin.site.register(UserAchievement)
