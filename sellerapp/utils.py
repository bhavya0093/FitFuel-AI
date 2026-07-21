import re
import secrets
import string
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

def myCustomMail(subject,template,to,context):
    subject = 'Subject'
    template_str = 'sellerapp/'+ template+'.html'
    html_message = render_to_string(template_str, {'data': context})
    plain_message = strip_tags(html_message)
    from_email = 'bhavyaaanjana@gmail.com'
    send_mail(subject, plain_message, from_email, [to], html_message=html_message)

def is_strong_password(password):
    """
    Returns (True, "") if password is strong, else (False, "reason").
    Rule: min 8 chars, 1 uppercase, 1 lowercase, 1 digit, 1 special char.
    """
    if not password or len(password) < 8:
        return False, "Password must be at least 8 characters long."
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter."
    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter."
    if not re.search(r"[0-9]", password):
        return False, "Password must contain at least one number."
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>_\-]", password):
        return False, "Password must contain at least one special character."
    return True, ""


def generate_strong_password(length=10):
    """
    Generates a cryptographically secure random password
    (used at registration instead of the old predictable scheme).
    """
    alphabet = string.ascii_letters + string.digits + "!@#$%&*"
    while True:
        pwd = ''.join(secrets.choice(alphabet) for _ in range(length))
        if is_strong_password(pwd)[0]:
            return pwd


def generate_business_insights(seller_obj, force_refresh=False):
    """
    Analyzes orders, products, revenue, ratings, stock, categories, and AI recommended products.
    Returns 5 business insights from DB cache or instant rule-based logic to keep page load lightning fast (<50ms).
    """
    from django.db.models import Sum, Avg
    from sellerapp.models import product, Category, BusinessInsight
    from customerapp.models import Order

    # 1. Return cached insights if available (instant 0ms DB fetch)
    if not force_refresh:
        existing = list(BusinessInsight.objects.filter(seller=seller_obj))
        if len(existing) >= 5:
            return existing

    # 2. Gather metrics
    products = product.objects.all()
    total_products = products.count()
    low_stock_products = products.filter(stock_qty__lte=5)
    low_stock_count = low_stock_products.count()
    ai_rec_count = products.filter(is_ai_recommended=True).count()
    avg_rating = products.aggregate(avg=Avg("rating"))["avg"] or 0.0

    orders = Order.objects.exclude(status="Cancelled")
    total_orders = orders.count()
    total_revenue = Order.objects.filter(status="Delivered").aggregate(total=Sum("final_amount"))["total"] or 0
    total_revenue = float(total_revenue)
    avg_order_value = round(total_revenue / total_orders, 2) if total_orders > 0 else 0.0

    categories = Category.objects.all()
    total_categories = categories.count()

    categories_analytics = Category.objects.annotate(
        total_sold_qty=Sum('products__total_sold')
    ).order_by('-total_sold_qty')

    trending_category = "None"
    if categories_analytics.exists() and categories_analytics[0].total_sold_qty:
        trending_category = categories_analytics[0].category_name

    # 3. Instant rule-based insights (~1ms)
    # Rule 1: Revenue Growth
    if total_revenue > 0:
        rev_title = "📈 Revenue Growth Strong"
        rev_desc = f"Your total delivered revenue has reached ₹{total_revenue:,.2f} over {total_orders} successful orders."
        rev_priority = "High" if total_revenue > 10000 else "Medium"
    else:
        rev_title = "📈 Increase Sales Activity"
        rev_desc = "Delivered revenue is currently at ₹0.00. Focus on marketing and user acquisition to drive orders."
        rev_priority = "High"

    # Rule 2: Categories
    if trending_category != "None":
        cat_title = f"🥗 {trending_category} Category Trending"
        cat_desc = f"The {trending_category} category is leading sales. Introduce new items in this category to capture more demand."
        cat_priority = "Medium"
    else:
        cat_title = "🥗 Expand Product Categories"
        cat_desc = f"You currently have {total_categories} active categories. Diversify your products to attract more customers."
        cat_priority = "Medium"

    # Rule 3: Stock Alert
    if low_stock_count > 0:
        first_low = low_stock_products.first()
        stock_title = "⚠ Stock Alert: Replenish Inventory"
        if low_stock_count > 1:
            stock_desc = f"'{first_low.product_name}' and {low_stock_count - 1} other products are running low (qty <= 5). Restock soon."
        else:
            stock_desc = f"'{first_low.product_name}' is critically low with only {first_low.stock_qty} left. Restock now."
        stock_priority = "High"
    else:
        stock_title = "⚠ Stock Levels Healthy"
        stock_desc = f"All {total_products} products have healthy stock levels. Monitor inventory trends regularly."
        stock_priority = "Low"

    # Rule 4: Ratings
    if avg_rating >= 4.0:
        rating_title = "⭐ Customer Satisfaction High"
        rating_desc = f"Your products enjoy an impressive average rating of {avg_rating:.1f}/5.0. Keep up the high quality standards!"
        rating_priority = "Medium"
    elif avg_rating > 0:
        rating_title = "⭐ Review Product Quality"
        rating_desc = f"Average product rating is currently {avg_rating:.1f}/5.0. Review customer feedback to make improvements."
        rating_priority = "High"
    else:
        rating_title = "⭐ Gather Customer Reviews"
        rating_desc = "No ratings received yet. Encourage buyers to review their purchases to build credibility."
        rating_priority = "Medium"

    # Rule 5: AI Personalization / AOV
    ai_ratio = (ai_rec_count / total_products * 100) if total_products > 0 else 0
    if ai_ratio > 20:
        ai_title = "🤖 AI Personalization Active"
        ai_desc = f"Over {ai_ratio:.0f}% of your catalog ({ai_rec_count} items) is AI Recommended, boosting cross-sales."
        ai_priority = "Medium"
    else:
        ai_title = "💰 Average Order Value Stable"
        ai_desc = f"Average basket size is ₹{avg_order_value:.2f}. Try bundling products to increase transaction sizes."
        ai_priority = "Low"

    insights_data = [
        {"title": rev_title, "description": rev_desc, "priority": rev_priority},
        {"title": cat_title, "description": cat_desc, "priority": cat_priority},
        {"title": stock_title, "description": stock_desc, "priority": stock_priority},
        {"title": rating_title, "description": rating_desc, "priority": rating_priority},
        {"title": ai_title, "description": ai_desc, "priority": ai_priority},
    ]

    # Save to DB cache
    try:
        BusinessInsight.objects.filter(seller=seller_obj).delete()
    except Exception:
        pass

    saved_insights = []
    for item in insights_data:
        try:
            insight = BusinessInsight.objects.create(
                seller=seller_obj,
                title=item.get("title", "Insight"),
                description=item.get("description", ""),
                priority=item.get("priority", "Medium")
            )
            saved_insights.append(insight)
        except Exception as e:
            print(f"Error saving business insight: {e}")

    return saved_insights