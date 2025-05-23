from django.contrib.auth.models import User
from rest_framework import viewsets, permissions, status, mixins # Import status and mixins
from rest_framework.decorators import action
from rest_framework.response import Response # Import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import Task, UserProfile, Achievement, UserAchievement # Import Achievement, UserAchievement
from .serializers import TaskSerializer, UserProfileSerializer, AchievementSerializer, UserCreateSerializer # Import AchievementSerializer
from django.shortcuts import get_object_or_404
# Import the achievement utility functions (we will recreate this file next)
from .achievement_utils import check_and_award_achievements

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer # Default serializer

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def register(self, request):
        serializer = UserCreateSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # UserProfile.objects.create(user=user) # Elimina o comenta esta línea
            return Response({'message': 'User created successfully. Profile will be created by signal.'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        user_profile = UserProfile.objects.get(user=request.user)
        serializer = UserProfileSerializer(user_profile)
        return Response(serializer.data)

class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        This view should return a list of all the tasks
        for the currently authenticated user.
        """
        user = self.request.user
        if user.is_authenticated:
            tasks = Task.objects.filter(user=user)
            return tasks
        return Task.objects.none()

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

        newly_unlocked_achievements_data = []

        # Check if the task was just completed in this update
        if serializer.instance.completed and not was_completed:
            # Award XP to the user
            user_profile, created = UserProfile.objects.get_or_create(user=self.request.user)
            
            task_xp_value = serializer.instance.xp_value
            if task_xp_value is None: # Should not happen if model field has a default
                task_xp_value = 0
            
            user_profile.total_xp += task_xp_value
            user_profile.save()
            
            # Check for achievements after XP update
            # This function will return a list of newly unlocked Achievement objects
            newly_unlocked = check_and_award_achievements(user_profile) 
            if newly_unlocked:
                newly_unlocked_achievements_data = AchievementSerializer(newly_unlocked, many=True).data
        
        # We need to return a custom response that includes the task and any new achievements
        # The default perform_update just returns serializer.data (which is the task)
        # So, we override the entire update method or ensure perform_update can modify the response.
        # For simplicity, we will adjust the response in the update method itself.

        # This part is tricky because perform_update doesn't directly return a Response.
        # The actual Response is built by the UpdateModelMixin.update method.
        # To inject newly_unlocked_achievements, we'd typically override the update method.

    # Override the actual update method from UpdateModelMixin
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        
        # --- Custom logic from perform_update starts here ---
        was_completed = instance.completed
        self.perform_save(serializer) # Replaces serializer.save() and calls perform_update internally if needed by mixin structure, but we are doing it directly
        # For this custom implementation, we call our logic directly:

        newly_unlocked_achievements_data = []
        user_profile_updated = False

        if serializer.instance.completed and not was_completed:
            user_profile, created = UserProfile.objects.get_or_create(user=self.request.user)
            task_xp_value = serializer.instance.xp_value if serializer.instance.xp_value is not None else 0
            user_profile.total_xp += task_xp_value
            user_profile.save()
            user_profile_updated = True
            
            newly_unlocked = check_and_award_achievements(user_profile) 
            if newly_unlocked:
                newly_unlocked_achievements_data = AchievementSerializer(newly_unlocked, many=True).data
        
        # If only description/title changed, but task was already complete, still check achievements
        # (e.g. if an achievement was for editing a task, though not our current criteria)
        # For now, we only care if it *became* complete.
        # If user_profile was updated due to XP gain, and no achievements were unlocked by that XP gain,
        # but the user might have met other criteria not directly tied to this task completion (e.g. login streak - not implemented)
        # we might still want to run check_and_award_achievements. 
        # However, our current check_and_award_achievements is tied to XP/Level and task count.
        # So, if XP didn't change, and task count didn't change (task wasn't completed), no need to re-check.

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        return Response({
            'task': serializer.data,
            'newly_unlocked_achievements': newly_unlocked_achievements_data
        })

    def perform_save(self, serializer):
        # Helper for the overridden update method, can be used by create too if needed.
        serializer.save()


class UserProfileViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin):
    """
    API endpoint that allows users to be viewed and updated.
    """
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        This view should return the profile of the currently authenticated user.
        """
        user = self.request.user
        return UserProfile.objects.filter(user=user)

    @action(detail=False, methods=['patch'], url_path='update-profile')
    def update_profile(self, request):
        user_profile = get_object_or_404(UserProfile, user=request.user)
        data = {}
        if 'selected_theme_id' in request.data:
            data['selected_theme_id'] = request.data['selected_theme_id']
        if 'selected_avatar_id' in request.data:
            data['selected_avatar_id'] = request.data['selected_avatar_id']
        
        if not data: # If neither theme nor avatar id is provided
            return Response({'error': 'No data provided for update.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = UserProfileSerializer(user_profile, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AchievementViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Achievement.objects.all()
    serializer_class = AchievementSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get'], url_path='my-achievements')
    def my_achievements(self, request):
        user_profile = get_object_or_404(UserProfile, user=request.user)
        # Access through the related_name 'unlocked_achievements' from UserProfile model
        achievements = user_profile.unlocked_achievements.all()
        serializer = AchievementSerializer(achievements, many=True)
        return Response(serializer.data)