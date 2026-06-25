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
    description = models.TextField()
    discount = models.IntegerField()
    badge_text = models.CharField(max_length=50)
    weight_unit = models.CharField(max_length=50)
    brand = models.CharField(max_length=30)

