from .models import UserProfile, Achievement, UserAchievement, Task
from django.db.models import F

# Helper function to get or create UserAchievement
def award_achievement(user_profile, achievement):
    ua, created = UserAchievement.objects.get_or_create(
        user_profile=user_profile,
        achievement=achievement
    )
    if created:
        # Award XP for the achievement itself, if any
        if achievement.xp_reward > 0:
            user_profile.total_xp = F('total_xp') + achievement.xp_reward
            # Note: We save user_profile outside this function after all checks,
            # or ensure this F expression is handled correctly if saved multiple times.
            # For simplicity, let's assume user_profile.save() is called after all achievements are awarded in a batch.
        return achievement # Return the achievement that was newly awarded
    return None # Not newly awarded

def check_and_award_achievements(user_profile):
    """
    Checks all achievement criteria for the given user and awards them if met.
    Returns a list of newly unlocked Achievement objects.
    """
    newly_unlocked_achievements = []
    # initial_xp = user_profile.total_xp # Not strictly needed here anymore
    xp_gained_from_achievements_this_run = 0

    # Fetch all possible achievements to check against
    all_achievements = Achievement.objects.all()

    for ach in all_achievements:
        # Skip if already unlocked
        if user_profile.unlocked_achievements.filter(id=ach.id).exists():
            continue

        unlocked_now = False
        if ach.criteria_type == 'TASKS_COMPLETED':
            completed_tasks_count = Task.objects.filter(user=user_profile.user, completed=True).count()
            if completed_tasks_count >= ach.criteria_value:
                unlocked_now = True
        
        elif ach.criteria_type == 'LEVEL_REACHED':
            # Calculate current level based on total_xp (including any XP from prior achievements in this same run)
            # Assuming 100 XP per level, level = floor(total_xp / 100) + 1
            # We use user_profile.total_xp directly here, as it will be updated by F expressions before save if other achievements grant XP.
            current_level_check_xp = user_profile.total_xp + xp_gained_from_achievements_this_run
            current_level = (current_level_check_xp // 100) + 1
            if current_level >= ach.criteria_value:
                unlocked_now = True
        
        # Add more criteria types here as needed
        # elif ach.criteria_type == 'SPECIFIC_TASK_COMPLETED':
        #     if Task.objects.filter(user=user_profile.user, id=ach.criteria_value, completed=True).exists():
        #         unlocked_now = True

        if unlocked_now:
            awarded_achievement = award_achievement(user_profile, ach)
            if awarded_achievement:
                newly_unlocked_achievements.append(awarded_achievement)
                if awarded_achievement.xp_reward > 0:
                    xp_gained_from_achievements_this_run += awarded_achievement.xp_reward
    
    # If any achievement awarded XP, the user_profile.total_xp F() expression needs to be resolved by a save.
    if xp_gained_from_achievements_this_run > 0:
        user_profile.save() # This will apply the F() expressions and save the new total_xp
        user_profile.refresh_from_db() # Refresh to get the updated total_xp

        # Re-check level-based achievements if XP was gained, as a new level might have been reached
        # This is a simplified loop; a more complex system might need to iterate until no new achievements are awarded.
        # We iterate over a copy of newly_unlocked_achievements in case it's modified
        current_newly_unlocked_count = len(newly_unlocked_achievements)

        for ach_check_again in all_achievements: # Check all achievements again
            if ach_check_again.criteria_type == 'LEVEL_REACHED' and not user_profile.unlocked_achievements.filter(id=ach_check_again.id).exists():
                current_level_after_xp_gain = (user_profile.total_xp // 100) + 1 # Use the now updated total_xp
                if current_level_after_xp_gain >= ach_check_again.criteria_value:
                    second_pass_awarded_achievement = award_achievement(user_profile, ach_check_again)
                    if second_pass_awarded_achievement:
                        # Avoid adding duplicates if it was somehow processed already (shouldn't happen with .exists() check)
                        if not any(a.id == second_pass_awarded_achievement.id for a in newly_unlocked_achievements):
                            newly_unlocked_achievements.append(second_pass_awarded_achievement)
                        
                        if second_pass_awarded_achievement.xp_reward > 0:
                            # If this second-pass achievement also grants XP, we must save and refresh again.
                            # This could lead to further level ups. A loop might be needed for complex scenarios.
                            # For now, we'll do one more save if XP was granted in the second pass.
                            user_profile.total_xp = F('total_xp') + second_pass_awarded_achievement.xp_reward
                            user_profile.save()
                            user_profile.refresh_from_db()
                            # A full recursive or iterative solution would re-run the entire check_and_award_achievements
                            # or loop the achievement checks until no new XP or achievements are granted in a pass.
                            # This simplified version handles one level of cascading XP gain for level achievements.

    return newly_unlocked_achievements