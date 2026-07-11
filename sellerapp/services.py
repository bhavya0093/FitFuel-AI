import json
import os
from google import genai
from django.conf import settings
from .prompts import PRODUCT_ANALYSIS_PROMPT

# Initialize the new Google GenAI Client
client = genai.Client(api_key=getattr(settings, 'GEMINI_API_KEY', None) or os.getenv("GEMINI_API_KEY") or "DUMMY_KEY")

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

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    text = response.text.strip()

    if text.startswith("```json"):
        text = text.replace("```json", "").replace("```", "").strip()

    elif text.startswith("```"):
        text = text.replace("```", "").strip()

    data = json.loads(text)

    if isinstance(data.get("ai_tags"), list):

        data["ai_tags"] = ", ".join(data["ai_tags"])

    return data    