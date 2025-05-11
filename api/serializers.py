from rest_framework import serializers
from django.contrib.auth.models import User # Import User model
from .models import Task, UserProfile # Import UserProfile

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']

class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True) # Nested UserSerializer
    class Meta:
        model = UserProfile
        fields = ['id', 'user', 'total_xp']

class TaskSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True) # User will be set in the view
    # Alternatively, to show more user detail (read-only):
    # user = UserSerializer(read_only=True)

    class Meta:
        model  = Task
        fields = ['id', 'user', 'title', 'completed', 'xp_value']
        # To make user field writable if you were not setting it in view:
        # read_only_fields = ('user',)