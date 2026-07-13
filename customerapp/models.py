from django.db import models
from sellerapp.models import *

# Create your models here.
class customer(models.Model):
    user_id = models.ForeignKey(User,on_delete=models.CASCADE,blank=True,null=True)
    firstname = models.CharField(max_length=20)
    lastname = models.CharField(max_length=20)
    contectno = models.CharField(max_length=10)
    pic = models.FileField(
        upload_to="images/",
        default="images/seller_admin.jpg"
    )
    subscription_plan = models.CharField(
        max_length=20,
        default="Free",
        choices=(("Free", "Free"), ("Pro", "Pro"), ("Elite", "Elite"))
    )

    def __str__(self):
        return self.firstname

    @property
    def total_orders(self):
        return self.order_set.count()

    @property
    def total_spent(self):
        total = sum(order.final_amount for order in self.order_set.exclude(status="Cancelled"))
        if total >= 1000:
            k_val = float(total) / 1000
            if k_val == int(k_val):
                return f"₹{int(k_val)}k"
            return f"₹{k_val:.1f}k"
        if total == int(total):
            return f"₹{int(total)}"
        return f"₹{total}"

    @property
    def wishlist_count(self):
        return self.wishlist_set.count()

    @property
    def coupons_count(self):
        return 3
    
class cart(models.Model):
    customer = models.ForeignKey(customer,on_delete=models.CASCADE)
    create_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.customer.firstname

class cartitem(models.Model):
    cart = models.ForeignKey(cart,on_delete=models.CASCADE)
    product = models.ForeignKey(product,on_delete=models.CASCADE)
    qty = models.IntegerField(default=1)

    def productprice(self):
        return self.product.product_price * self.qty

class Address(models.Model):

    customer = models.ForeignKey(
        customer,
        on_delete=models.CASCADE,
        related_name="addresses"
    )

    fullname = models.CharField(max_length=100)
    mobile = models.CharField(max_length=10)

    house_no = models.CharField(max_length=120)
    area = models.CharField(max_length=200)
    landmark = models.CharField(max_length=200, blank=True)

    city = models.CharField(max_length=80)
    state = models.CharField(max_length=80)
    pincode = models.CharField(max_length=6)

    address_type = models.CharField(
        max_length=20,
        choices=[
            ("Home","Home"),
            ("Work","Work"),
            ("Other","Other")
        ],
        default="Home"
    )

    is_default = models.BooleanField(default=False)

    created_at=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.fullname

class Order(models.Model):

    PAYMENT_CHOICES = (
        ("UPI", "UPI"),
        ("CARD", "Card"),
        ("COD", "Cash On Delivery"),
    )

    STATUS_CHOICES = (
        ("Pending", "Pending"),
        ("Confirmed", "Confirmed"),
        ("Packed", "Packed"),
        ("Shipped", "Shipped"),
        ("Delivered", "Delivered"),
        ("Cancelled", "Cancelled"),
    )

    customer = models.ForeignKey(customer, on_delete=models.CASCADE)
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True)

    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES)

    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    final_amount = models.DecimalField(max_digits=10, decimal_places=2)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="Pending"
    )

    order_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id}"
    
class OrderItem(models.Model):

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items"
    )

    product = models.ForeignKey(product, on_delete=models.CASCADE)

    quantity = models.IntegerField()

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    def __str__(self):
        return self.product.product_name
    
class Payment(models.Model):

    STATUS = (
        ("Pending", "Pending"),
        ("Paid", "Paid"),
        ("Failed", "Failed"),
        ("Refunded", "Refunded"),
    )

    METHOD = (
        ("UPI", "UPI"),
        ("CARD", "CARD"),
        ("COD", "Cash On Delivery"),
    )

    order = models.OneToOneField(Order, on_delete=models.CASCADE)

    payment_id = models.CharField(max_length=100, unique=True)

    transaction_id = models.CharField(max_length=150, blank=True, null=True)

    amount = models.DecimalField(max_digits=10, decimal_places=2)

    method = models.CharField(max_length=20, choices=METHOD)

    status = models.CharField(
        max_length=20,
        choices=STATUS,
        default="Pending"
    )

    payment_date = models.DateTimeField(auto_now_add=True) 

class UserHealthProfile(models.Model):

    ACTIVITY_CHOICES = (
        ("Sedentary", "Sedentary"),
        ("Light", "Light"),
        ("Moderate", "Moderate"),
        ("Active", "Active"),
        ("Very Active", "Very Active"),
    )

    GOAL_CHOICES = (
        ("Weight Loss", "Weight Loss"),
        ("Muscle Gain", "Muscle Gain"),
        ("Maintenance", "Maintenance"),
    )

    DIET_CHOICES = (
        ("Veg", "Veg"),
        ("Vegan", "Vegan"),
        ("Non-Veg", "Non-Veg"),
    )

    GENDER_CHOICES = (
        ("Male", "Male"),
        ("Female", "Female"),
        ("Other", "Other"),
    )

    customer = models.OneToOneField(
        customer,
        on_delete=models.CASCADE,
        related_name="health_profile"
    )

    age = models.PositiveIntegerField(default=18)

    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES
    )

    height = models.FloatField(
        help_text="Height in centimeters"
    )

    weight = models.FloatField(
        help_text="Weight in kilograms"
    )

    activity_level = models.CharField(
        max_length=20,
        choices=ACTIVITY_CHOICES
    )

    goal = models.CharField(
        max_length=30,
        choices=GOAL_CHOICES
    )

    diet_type = models.CharField(
        max_length=20,
        choices=DIET_CHOICES
    )

    bmi = models.FloatField(default=0)

    daily_calories = models.IntegerField(default=0)

    protein_goal = models.FloatField(default=0)

    carbs_goal = models.FloatField(default=0)

    fat_goal = models.FloatField(default=0)

    water_goal = models.FloatField(default=0)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.customer.firstname} Health Profile"

class ProductReview(models.Model):

    product = models.ForeignKey(
        product,
        on_delete=models.CASCADE,
        related_name="reviews"
    )

    customer = models.ForeignKey(
        customer,
        on_delete=models.CASCADE
    )

    rating = models.PositiveSmallIntegerField(default=5)

    review = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.customer.firstname} - {self.product.product_name}"

class ProgressLog(models.Model):

    customer = models.ForeignKey(
        customer,
        on_delete=models.CASCADE,
        related_name="progress_logs"
    )

    weight = models.FloatField()

    bmi = models.FloatField()

    calories = models.IntegerField(default=0)

    protein = models.FloatField(default=0)

    water = models.FloatField(default=0)

    created_at = models.DateField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.customer.firstname} - {self.created_at}"

class Wishlist(models.Model):

    customer = models.ForeignKey(
        customer,
        on_delete=models.CASCADE
    )

    product = models.ForeignKey(
        product,
        on_delete=models.CASCADE
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("customer", "product")

    def __str__(self):
        return f"{self.customer.firstname} - {self.product.product_name}"

class Notification(models.Model):

    customer = models.ForeignKey(
        customer,
        on_delete=models.CASCADE
    )

    title = models.CharField(max_length=150)

    message = models.TextField()

    is_read = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    
class Wallet(models.Model):

    customer = models.OneToOneField(
        customer,
        on_delete=models.CASCADE,
        related_name="wallet"
    )

    balance = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.customer.firstname} Wallet"

class WalletTransaction(models.Model):

    TRANSACTION_TYPES = (
        ("Credit", "Credit"),
        ("Debit", "Debit"),
    )

    wallet = models.ForeignKey(
        Wallet,
        on_delete=models.CASCADE,
        related_name="transactions"
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    transaction_type = models.CharField(
        max_length=10,
        choices=TRANSACTION_TYPES
    )

    description = models.CharField(max_length=255)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.transaction_type} - ₹{self.amount}"

class Coupon(models.Model):

    code = models.CharField(
        max_length=30,
        unique=True
    )

    description = models.CharField(
        max_length=255
    )

    discount = models.PositiveIntegerField(
        help_text="Discount Percentage"
    )

    minimum_amount = models.PositiveIntegerField(
        default=0
    )

    maximum_discount = models.PositiveIntegerField(
        default=500
    )

    expiry_date = models.DateField()

    is_active = models.BooleanField(
        default=True
    )

    def __str__(self):
        return self.code
    
class UserCoupon(models.Model):

    customer = models.ForeignKey(
        customer,
        on_delete=models.CASCADE
    )

    coupon = models.ForeignKey(
        Coupon,
        on_delete=models.CASCADE
    )

    is_used = models.BooleanField(
        default=False
    )

    used_at = models.DateTimeField(
        null=True,
        blank=True
    )

    class Meta:
        unique_together = (
            "customer",
            "coupon"
        )
class MealPlan(models.Model):

    customer = models.ForeignKey(
        customer,
        on_delete=models.CASCADE
    )

    meal_type = models.CharField(
        max_length=30,
        choices=[
            ("Breakfast","Breakfast"),
            ("Lunch","Lunch"),
            ("Dinner","Dinner"),
            ("Snacks","Snacks")
        ]
    )

    product = models.ForeignKey(
        product,
        on_delete=models.CASCADE
    )

    quantity = models.PositiveIntegerField(default=1)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer.firstname} - {self.meal_type}"

class DailyMealLog(models.Model):

    customer = models.ForeignKey(
        customer,
        on_delete=models.CASCADE
    )

    product = models.ForeignKey(
        product,
        on_delete=models.CASCADE
    )

    meal_type = models.CharField(
        max_length=30,
        choices=[
            ("Breakfast","Breakfast"),
            ("Lunch","Lunch"),
            ("Dinner","Dinner"),
            ("Snacks","Snacks"),
        ]
    )

    quantity = models.PositiveIntegerField(default=1)

    calories = models.IntegerField(default=0)

    protein = models.FloatField(default=0)

    carbs = models.FloatField(default=0)

    fat = models.FloatField(default=0)

    consumed = models.BooleanField(default=False)

    log_date = models.DateField(auto_now_add=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):

        return f"{self.customer.firstname} - {self.product.product_name}"

class UserAchievement(models.Model):

    customer = models.ForeignKey(
        customer,
        on_delete=models.CASCADE
    )

    title = models.CharField(max_length=100)

    description = models.CharField(max_length=255)

    badge = models.CharField(max_length=50)

    unlocked_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):

        return f"{self.customer} - {self.title}"
    
class UserGamification(models.Model):

    customer = models.OneToOneField(
        customer,
        on_delete=models.CASCADE
    )

    xp = models.IntegerField(default=0)

    level = models.IntegerField(default=1)

    streak = models.IntegerField(default=0)

    ai_questions = models.IntegerField(default=0)

    total_meals = models.IntegerField(default=0)

    water_streak = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

class DailyHealthInsight(models.Model):

    customer = models.ForeignKey(
        customer,
        on_delete=models.CASCADE
    )

    insight = models.TextField()

    health_score = models.IntegerField(default=0)

    calories = models.IntegerField(default=0)

    protein = models.FloatField(default=0)

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:

        ordering = ["-created_at"]  