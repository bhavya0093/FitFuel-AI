from django.contrib import admin
from .models import *

admin.site.register(ProductReview)
admin.site.register(ProgressLog)
admin.site.register(Wishlist)
admin.site.register(Coupon)
admin.site.register(UserCoupon)