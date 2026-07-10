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

def check_user_achievements(customer):

    # ==========================
    # First Meal
    # ==========================

    meal_count = DailyMealLog.objects.filter(
        customer=customer,
        consumed=True
    ).count()

    if meal_count >= 1:

        unlock_achievement(
            customer,
            "First Meal",
            "Completed your first healthy meal.",
            "🍽",
            20
        )

    # ==========================
    # Protein Champion
    # ==========================

    high_protein = DailyMealLog.objects.filter(
        customer=customer,
        protein__gte=25
    ).count()

    if high_protein >= 10:

        unlock_achievement(
            customer,
            "Protein Champion",
            "Completed 10 high protein meals.",
            "💪",
            50
        )

    # ==========================
    # First Review
    # ==========================

    review_count = ProductReview.objects.filter(
        customer=customer
    ).count()

    if review_count >= 1:

        unlock_achievement(
            customer,
            "Reviewer",
            "Submitted your first review.",
            "⭐",
            20
        )

    # ==========================
    # First Order
    # ==========================

    order_count = Order.objects.filter(
        customer=customer
    ).count()

    if order_count >= 1:

        unlock_achievement(
            customer,
            "First Order",
            "Placed your first order.",
            "🛒",
            30
        )