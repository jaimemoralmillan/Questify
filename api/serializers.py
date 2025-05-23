import math
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from .models import Task, UserProfile, Achievement, UserAchievement # Import Achievement and UserAchievement

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']

# --- Achievement Serializer ---
class AchievementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Achievement
        fields = ['name', 'description', 'icon', 'xp_reward']

class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True, label="Confirm password")

    class Meta:
        model = User
        fields = ('username', 'password', 'password2') # Removed email, first_name, last_name

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        # No longer need to validate email if it's not a user input
        return attrs

    def create(self, validated_data):
        # Generate a dummy email as the User model requires it.
        # This email won't be used for any practical purpose in this simplified registration.
        dummy_email = f"{validated_data['username']}@example.com"

        user = User.objects.create_user(
            username=validated_data['username'],
            email=dummy_email, # Use dummy email
            # first_name and last_name are not provided
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True) # Nested UserSerializer
    level = serializers.SerializerMethodField() # Added level field
    xp_at_current_level_start = serializers.SerializerMethodField()
    xp_for_next_level = serializers.SerializerMethodField()
    xp_progress_in_current_level = serializers.SerializerMethodField()
    xp_needed_for_level_up = serializers.SerializerMethodField()
    unlocked_achievements = serializers.SerializerMethodField() # Add this line

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
            'xp_needed_for_level_up',
            'unlocked_achievements',  # Add this line
            'selected_theme_id', # Add this line for the selected theme
            'selected_avatar_id' # Add this line for the selected avatar
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

    def get_unlocked_achievements(self, obj):
        # Assuming obj is a UserProfile instance
        # We access the related UserAchievement instances through the UserProfile model's M2M field 'unlocked_achievements'
        # which refers to the Achievement model directly.
        achievements = obj.unlocked_achievements.all() # This gets all Achievement instances linked to the UserProfile
        return AchievementSerializer(achievements, many=True).data

class TaskSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True) # User will be set in the view
    # Alternatively, to show more user detail (read-only):
    # user = UserSerializer(read_only=True)

    class Meta:
        model = Task
        fields = ['id', 'user', 'title', 'description', 'completed', 'xp_value', 'duration', 'difficulty']
        read_only_fields = ['user'] # User is set based on the authenticated request user

    def create(self, validated_data):
        # user will be added in the view based on request.user
        return Task.objects.create(**validated_data)