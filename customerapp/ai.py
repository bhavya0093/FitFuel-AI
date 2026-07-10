from google import genai
import os

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY") or "DUMMY_KEY"
)


def generate_nutrition_advice(
    profile,
    calories,
    protein,
    meals
):

    prompt = f"""
You are an expert nutrition coach.

User Goal:
{profile.goal}

Diet Type:
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

Give personalized nutrition advice.

Rules:

- Maximum 80 words
- Friendly
- Motivating
- Plain text only
- No markdown
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return response.text