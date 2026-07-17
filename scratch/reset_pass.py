import os
import sys
import django

sys.path.append('c:/Django Task/Project/myenv/bkshop')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bkshop.settings')
django.setup()

from sellerapp.models import User
from django.contrib.auth.hashers import make_password

user = User.objects.filter(email='bhavyachaudhary.developer@gmail.com').first()
if user:
    user.password = make_password('12345')
    user.save()
    print("SUCCESS: Reset password to 12345")
else:
    print("User not found!")
