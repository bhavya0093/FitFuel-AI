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


def generate_seller_insights_with_ai(metrics_data):
    prompt = f"""
You are the lead business analyst and AI consultant for a premium health and nutrition marketplace named "FitFuel AI".
Your task is to analyze the seller's performance metrics and provide actionable, premium business intelligence insights.

Analyze the following metrics:
- Total Customers: {metrics_data.get('total_customers')}
- Total Products: {metrics_data.get('total_products')}
- Total Orders: {metrics_data.get('total_orders')}
- Total Revenue: INR {metrics_data.get('total_revenue'):.2f}
- Average Order Value: INR {metrics_data.get('average_order_value'):.2f}
- Average Product Rating: {metrics_data.get('average_rating'):.1f}
- AI-Recommended Products Count: {metrics_data.get('ai_products')}
- Low Stock Products Count: {metrics_data.get('low_stock_count')}
- Top Selling Products: {metrics_data.get('top_selling_products')}

Based on these metrics, generate exactly 4-5 high-impact insights.
For each insight, specify:
1. `type`: The theme/accent category of the card. Must be one of:
   - "positive" (for revenue growth, success, achievements)
   - "trending" (for popular categories, market shifts, product popularity)
   - "ai" (for Gemini recommendation performance, automated gains, AI metrics)
   - "warning" (for stock warnings, declining sales, immediate action items)
   - "info" (for average basket size, user behavior patterns, general suggestions)
2. `icon`: A single relevant emoji (e.g. 📈, 🥗, 🤖, ⚠, 💰, 🏆, etc.).
3. `title`: A short header (3-5 words).
4. `text`: A concise, professional recommendation (1-2 sentences max) tailored specifically to the metrics. Do not use generic statements; reference their actual numbers, growth potential, or stock situation.

Return the result STRICTLY as a valid JSON array of objects. Do not include any markdown wrappers (like ```json) or comments outside the JSON.
Example format:
[
  {{
    "type": "warning",
    "icon": "⚠",
    "title": "Restock Hot Products",
    "text": "You have 3 items running low on stock. Restock high-protein oats immediately to capture ongoing demand."
  }}
]
"""

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        text = response.text.strip()
        if text.startswith("```json"):
            text = text.replace("```json", "").replace("```", "").strip()
        elif text.startswith("```"):
            text = text.replace("```", "").strip()
        return json.loads(text)
    except Exception as e:
        # Fallback insights if API call fails
        return [
            {
                "type": "positive",
                "icon": "📈",
                "title": "Revenue Performance",
                "text": f"Your current total revenue is ₹{metrics_data.get('total_revenue'):.2f} across {metrics_data.get('total_orders')} orders."
            },
            {
                "type": "info",
                "icon": "💰",
                "title": "Order Value",
                "text": f"Your average order value stands at ₹{metrics_data.get('average_order_value'):.2f}. Optimize checkout to boost this further."
            },
            {
                "type": "warning",
                "icon": "⚠",
                "title": "Stock Alert",
                "text": f"You have {metrics_data.get('low_stock_count')} products with low stock levels. Review inventory."
            }
        ]