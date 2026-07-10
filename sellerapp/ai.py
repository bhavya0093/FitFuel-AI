def generate_nutrition_advice(
    profile,
    calories,
    protein,
    meals
    prompt = f"""
    You are an expert nutrition coach.

    User Goal:
    {profile.goal}

    Diet:
    {profile.diet_type}

    Daily Calories Goal:
    {profile.daily_calories}

    Calories Consumed:
    {calories}

    Protein Goal:
    {profile.protein_goal}

    Protein Consumed:
    {protein}

    Meals Completed:
    {meals}

    Generate a personalized nutrition advice.

    Rules:

    Maximum 80 words.

    Friendly.

    Motivating.

    Do not use markdown.

    Only plain text.
    """
):