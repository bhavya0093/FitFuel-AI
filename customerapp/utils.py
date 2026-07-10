from .models import *
from django.db import transaction

from datetime import timedelta
from django.utils import timezone


def update_streak(customer):

    game, created = UserGamification.objects.get_or_create(
        customer=customer
    )

    today = timezone.now().date()

    streak = 0

    while True:

        check_day = today - timedelta(days=streak)

        exists = DailyMealLog.objects.filter(
            customer=customer,
            consumed=True,
            log_date=check_day
        ).exists()

        if exists:

            streak += 1

        else:

            break

    game.current_streak = streak

    if streak > game.longest_streak:

        game.longest_streak = streak

    game.save()

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

    update_streak(customer)

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
    
    # ==========================
    # 7 Day Streak
    # ==========================

    if game.current_streak >= 7:

        unlock_achievement(

            customer,

            "7 Day Streak",

            "Logged meals for 7 consecutive days.",

            "🔥",

            100

        )
    # ==========================
    # 30 Day Streak
    # ==========================

    if game.current_streak >= 30:

        unlock_achievement(

            customer,

            "30 Day Streak",

            "Maintained a 30 day nutrition streak.",

            "🏆",

            500

        )