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