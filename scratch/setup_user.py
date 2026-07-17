import os
import sys
import django

sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bkshop.settings')
django.setup()

from customerapp.models import User
from django.contrib.auth.hashers import make_password

user = User.objects.get(email="bhavyaaanjana@gmail.com")
user.password = make_password("password123")
user.save()

print(f"Password reset successfully for {user.email}")
