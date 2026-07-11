import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bkshop.settings')
from django.conf import settings
# Add to ALLOWED_HOSTS dynamically
if hasattr(settings, 'ALLOWED_HOSTS'):
    settings.ALLOWED_HOSTS.append('*')
else:
    settings.ALLOWED_HOSTS = ['*']

django.setup()

from django.test import Client
from customerapp.models import User

# Create client
client = Client()

# Get user
user = User.objects.get(email="bhavyaaanjana@gmail.com")

# Log in the user
# Set the session manually
session = client.session
session['email'] = user.email
session['uid'] = user.id
session.save()

# Request api/ai-insights/ page
response = client.get('/seller/api/ai-insights/')
print("Response status code:", response.status_code)
try:
    print("Response JSON:")
    import pprint
    pprint.pprint(response.json())
except Exception as e:
    print("Failed to parse JSON:", e)
    print("Response Content:", response.content)

