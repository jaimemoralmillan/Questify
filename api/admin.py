from django.contrib import admin
from .models import Task, UserProfile # Import Task and UserProfile

# Register your models here.
admin.site.register(Task)
admin.site.register(UserProfile)
