from django.db import models


# Create your models here.
class User(models.Model):
    email = models.CharField(max_length=50,unique=True)
    password = models.CharField(max_length=128)
    role = models.CharField(max_length=20)
    otp = models.IntegerField(null=True, blank=True)
    otp_created_at = models.DateTimeField(null=True, blank=True)
    otp_attempts = models.IntegerField(default=0) 
    create_at =models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.email

class seller(models.Model):
    user_id = models.ForeignKey(User,on_delete=models.CASCADE)
    firstname = models.CharField(max_length=20)
    lastname = models.CharField(max_length=20)
    contectno = models.CharField(max_length=20)
    seller_store_name = models.CharField(max_length=20,null=True,blank=True)
    pic = models.FileField(
        upload_to="images/",
        default="images/seller_admin.jpg"
    )
    city = models.CharField(max_length=20,null=True,blank=True)
    address = models.TextField(null=True,blank=True)
    GSTNO = models.CharField(max_length=20,null=True,blank=True)

    def __str__(self):
        return self.firstname+" "+self.lastname
    
class Category(models.Model):
    category_name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    category_image = models.ImageField(upload_to='category_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['-created_at']

    def __str__(self):
        return self.category_name
    
class product(models.Model):
    user_id = models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True)
    product_name = models.CharField(max_length=50)
    product_category = models.ForeignKey(Category,on_delete=models.CASCADE,related_name="products")
    product_price = models.IntegerField()
    stock_qty = models.IntegerField()
    picture = models.FileField(
        upload_to="images/",
        default="images/default.jpg"
    )
    description = models.TextField(blank=True)
    discount = models.IntegerField(default=0)
    badge_text = models.CharField(max_length=50, blank=True, default="")
    weight_unit = models.CharField(max_length=50, default="100g")
    brand = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    total_sold = models.IntegerField(default=0)
    calories = models.IntegerField(default=0, help_text="Calories per serving")

    protein = models.FloatField(default=0.0, help_text="Protein in grams")

    carbs = models.FloatField(default=0.0, help_text="Carbohydrates in grams")

    fat = models.FloatField(default=0.0, help_text="Fat in grams")

    sugar = models.FloatField(default=0.0, help_text="Sugar in grams")

    fiber = models.FloatField(default=0.0, help_text="Fiber in grams")

    serving_size = models.CharField(max_length=50, default="100g")

    ingredients = models.TextField(blank=True)

    benefits = models.TextField(blank=True)

    recommended_usage = models.TextField(blank=True)
    rating = models.FloatField(default=0.0)

    review_count = models.IntegerField(default=0)


    # ===========================
# AI Recommendation Fields
# ===========================

    diet_type = models.CharField(
        max_length=20,
        choices=[
            ("Veg", "Veg"),
            ("Non-Veg", "Non-Veg"),
            ("Vegan", "Vegan")
        ],
        default="Veg"
    )

    goal_type = models.CharField(
        max_length=30,
        choices=[
            ("Weight Loss", "Weight Loss"),
            ("Muscle Gain", "Muscle Gain"),
            ("Maintenance", "Maintenance")
        ],
        default="Maintenance"
    )

    flavour = models.CharField(max_length=50, blank=True)

    is_featured = models.BooleanField(default=False)

    is_ai_recommended = models.BooleanField(default=False)

    def __str__(self):
        return self.product_name


