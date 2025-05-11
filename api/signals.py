from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import UserProfile

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Signal handler to create a UserProfile when a new User is created.
    """
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Signal handler to save the UserProfile when the User is saved.
    (This might be useful if UserProfile had fields that depend on User fields other than the relation itself,
    or if you wanted to ensure it's saved for some other reason. For a simple profile like ours,
    it's often not strictly necessary if create_user_profile handles the creation.)
    """
    # Check if the user has a profile. This handles cases where a user might have been created
    # before this signal was in place, or if the profile was somehow deleted.
    # Using hasattr is a bit safer than trying a direct access which might raise DoesNotExist.
    if hasattr(instance, 'profile'):
        instance.profile.save()
    else:
        # If the profile doesn't exist (e.g., for users created before this signal was active
        # or if it was deleted), create it. This makes the save_user_profile more robust.
        UserProfile.objects.create(user=instance)
