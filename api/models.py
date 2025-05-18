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

class Achievement(models.Model):
    CRITERIA_TYPE_CHOICES = [
        ('TASKS_COMPLETED', 'Tasks Completed'),
        ('LEVEL_REACHED', 'Level Reached'),
        ('XP_EARNED', 'XP Earned'),
        # Add more choices as needed, e.g.:
        # ('LOGIN_STREAK', 'Login Streak'),
        # ('TASK_STREAK', 'Task Streak'),
        # ('SPECIFIC_TASK_COMPLETED', 'Specific Task Completed'),
    ]

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    icon = models.CharField(max_length=50, blank=True, null=True) # e.g., 'star', 'trophy', 'checkmark-circle'
    criteria_type = models.CharField(
        max_length=50,
        choices=CRITERIA_TYPE_CHOICES, # Add choices here
        default='TASKS_COMPLETED' # Optional: set a default
    )
    criteria_value = models.IntegerField()
    xp_reward = models.IntegerField(default=0) # XP awarded for unlocking this achievement

    def __str__(self):
        return self.name

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    total_xp = models.IntegerField(default=0)
    unlocked_achievements = models.ManyToManyField(Achievement, through='UserAchievement', related_name='achieved_by')

    def __str__(self):
        return f'{self.user.username}\'s Profile'

class UserAchievement(models.Model):
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE)
    unlocked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user_profile', 'achievement') # Ensure a user can only unlock an achievement once

    def __str__(self):
        return f'{self.user_profile.user.username} unlocked {self.achievement.name}'