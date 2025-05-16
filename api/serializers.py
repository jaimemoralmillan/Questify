import math
from rest_framework import serializers
from django.contrib.auth.models import User # Import User model
from .models import Task, UserProfile # Import UserProfile

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']

class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True) # Nested UserSerializer
    level = serializers.SerializerMethodField() # Added level field
    xp_at_current_level_start = serializers.SerializerMethodField()
    xp_for_next_level = serializers.SerializerMethodField()
    xp_progress_in_current_level = serializers.SerializerMethodField()
    xp_needed_for_level_up = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = [
            'id',
            'user',
            'total_xp',
            'level',
            'xp_at_current_level_start',
            'xp_for_next_level',
            'xp_progress_in_current_level',
            'xp_needed_for_level_up'
        ] # Added XP progress fields

    def get_level(self, obj):
        return math.floor(obj.total_xp / 100) + 1

    def get_xp_at_current_level_start(self, obj):
        level = self.get_level(obj)
        return (level - 1) * 100

    def get_xp_for_next_level(self, obj):
        level = self.get_level(obj)
        return level * 100

    def get_xp_progress_in_current_level(self, obj):
        xp_at_start = self.get_xp_at_current_level_start(obj)
        return obj.total_xp - xp_at_start

    def get_xp_needed_for_level_up(self, obj):
        # Assuming each level requires 100 XP
        return 100

class TaskSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True) # User will be set in the view
    # Alternatively, to show more user detail (read-only):
    # user = UserSerializer(read_only=True)

    class Meta:
        model  = Task
        fields = ['id', 'user', 'title', 'description', 'completed', 'xp_value']
        # To make user field writable if you were not setting it in view:
        # read_only_fields = ('user',)