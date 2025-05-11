from rest_framework import viewsets, permissions
from .models import Task, UserProfile
from .serializers import TaskSerializer, UserProfileSerializer
from django.shortcuts import get_object_or_404

class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        This view should return a list of all the tasks
        for the currently authenticated user.
        """
        user = self.request.user
        return Task.objects.filter(user=user)

    def perform_create(self, serializer):
        """
        Automatically set the user of the task to the logged-in user.
        """
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        """
        If the task is being marked as completed, award XP to the user.
        """
        instance = serializer.instance # Task instance before save
        was_completed = instance.completed

        # Save the updated task instance
        serializer.save() # This updates the instance in place

        # Check if the task was just completed in this update
        if serializer.instance.completed and not was_completed:
            # Award XP to the user
            user_profile, created = UserProfile.objects.get_or_create(user=self.request.user)
            
            task_xp_value = serializer.instance.xp_value
            if task_xp_value is None: # Should not happen if model field has a default
                task_xp_value = 0
            
            user_profile.total_xp += task_xp_value
            user_profile.save()

class UserProfileViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows users to be viewed.
    """
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        This view should return the profile of the currently authenticated user.
        """
        user = self.request.user
        return UserProfile.objects.filter(user=user)