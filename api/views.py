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
        instance = serializer.instance
        was_completed = instance.completed # Get current 'completed' status before saving
        
        serializer.save() # This updates the instance in place
        
        # Check if the 'completed' field was changed from False to True in this update
        if serializer.instance.completed and not was_completed:
            user_profile, created = UserProfile.objects.get_or_create(user=self.request.user)
            # Use the xp_value from the task instance (it's the current value after save)
            user_profile.total_xp += serializer.instance.xp_value 
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