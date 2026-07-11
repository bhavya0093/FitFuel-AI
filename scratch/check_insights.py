import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bkshop.settings')
django.setup()

from sellerapp.models import seller, BusinessInsight
from sellerapp.utils import generate_business_insights

# Get first seller
s = seller.objects.first()
if s:
    print(f"Generating business insights for seller: {s.firstname} {s.lastname}")
    insights = generate_business_insights(s)
    print(f"Generated {len(insights)} insights.")
    for idx, ins in enumerate(insights, 1):
        print(f"{idx}. [{ins.priority}] {ins.title}: {ins.description}")
else:
    print("No seller found in the database.")
