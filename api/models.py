from django.db import models
from django.contrib.auth.models import User # Import User model

class Task(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks') # Link to User
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)  # Field added to Task model
    completed = models.BooleanField(default=False)
    xp_value = models.IntegerField(default=10) # XP awarded for completing the task

    def __str__(self):
        return self.title

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    total_xp = models.IntegerField(default=0)

    def __str__(self):
        return f'{self.user.username}\'s Profile'