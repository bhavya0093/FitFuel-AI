from django.db import models


# Create your models here.
class User(models.Model):
    email = models.CharField(max_length=50,unique=True)
    password = models.CharField(max_length=20)
    role = models.CharField(max_length=20)
    otp = models.IntegerField(null=True, blank=True)
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
    
class product(models.Model):
    user_id = models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True)
    product_name = models.CharField(max_length=50)
    product_category = models.CharField(max_length=50)
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

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name