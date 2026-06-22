from django.contrib import admin
from .models import *
from customerapp.models import *

# Register your models here.
admin.site.register(User)
admin.site.register(seller)
admin.site.register(customer)
admin.site.register(product)
admin.site.register(cart)
admin.site.register(cartitem)