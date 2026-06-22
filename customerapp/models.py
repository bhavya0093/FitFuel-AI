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

    def __str__(self):
        return self.firstname
    
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
    
    
    