from .models import *
from django.db import transaction


def unlock_achievement(
    customer,
    title,
    description,
    badge,
    xp_reward=20
):
    # Achievement already unlocked?
    exists = UserAchievement.objects.filter(
        customer=customer,
        title=title
    ).exists()

    if exists:
        return

    # Create Achievement
    UserAchievement.objects.create(
        customer=customer,
        title=title,
        description=description,
        badge=badge
    )

    # Create Notification
    Notification.objects.create(
        customer=customer,
        title="Achievement Unlocked",
        message=f"{badge} {title}"
    )

    # Get or Create Gamification Profile
    game, created = UserGamification.objects.get_or_create(
        customer=customer
    )

    # Add XP
    game.xp += xp_reward

    # Update Level
    game.level = (game.xp // 100) + 1

    # Save
    game.save()