import json
import google.generativeai as genai

from django.conf import settings

from .prompts import PRODUCT_ANALYSIS_PROMPT


genai.configure(api_key=settings.GEMINI_API_KEY)

model = genai.GenerativeModel("gemini-2.5-flash")


def analyze_product_with_ai(
    product_name,
    brand,
    description,
    weight,
):
    prompt = f"""
{PRODUCT_ANALYSIS_PROMPT}

Product Name:
{product_name}

Brand:
{brand}

Description:
{description}

Weight:
{weight}
"""

    response = model.generate_content(prompt)

    text = response.text.strip()

    if text.startswith("```json"):
        text = text.replace("```json", "").replace("```", "").strip()

    elif text.startswith("```"):
        text = text.replace("```", "").strip()

    return json.loads(text)