from django.db import models
from django.utils import timezone
import uuid


class User(models.Model):
    user_id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    is_verified = models.BooleanField(default=False)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    otp = models.CharField(max_length=7, null=False, default= not None)
    otp_expiration = models.DateTimeField(default=timezone.now)
    created_dtm = models.DateTimeField(default= None)
    modified_dtm = models.DateTimeField(default= None)
    role = models.CharField(max_length=20, default='Customer', choices=[('Customer', 'Customer'), ('Admin', 'Admin')])
    display_picture = models.ImageField(default=None)


class ShippingAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)


class user_addr(models.Model):
    user=models.ForeignKey(User, on_delete=models.CASCADE)
    Address=models.ForeignKey(ShippingAddress, on_delete=models.DO_NOTHING)


class Product(models.Model):
    product_id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    product_name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.IntegerField()


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.DO_NOTHING)
    quantity = models.IntegerField(default=1)

class WishList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.DO_NOTHING)
    quantity = models.IntegerField(default=1)

# # Category model
# class Category(models.Model):
#     category_name = models.CharField(max_length=255)


class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ordered_product = models.ForeignKey(Product, on_delete=models.CASCADE)
    rating = models.IntegerField()
    review_text = models.TextField()
    date_posted = models.DateTimeField(auto_now_add=True)




# # Order model
# class Order(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     order_date = models.DateTimeField(auto_now_add=True)
#     total_price = models.DecimalField(max_digits=10, decimal_places=2)
#     order_status = models.CharField(max_length=20)

# # OrderItem model
# class OrderItem(models.Model):
#     order = models.ForeignKey(Order, on_delete=models.CASCADE)
#     product = models.ForeignKey(Product, on_delete=models.CASCADE)
#     quantity = models.IntegerField()
#     subtotal_price = models.DecimalField(max_digits=10, decimal_places=2)

# # Payment model
# class Payment(models.Model):
#     order = models.ForeignKey(Order, on_delete=models.CASCADE)
#     payment_date = models.DateTimeField(auto_now_add=True)
#     payment_amount = models.DecimalField(max_digits=10, decimal_places=2)
#     payment_method = models.CharField(max_length=50)
#     payment_status = models.CharField(max_length=20)

# Admin model (if applicable)
# class Admin(models.Model):
#     username = models.CharField(max_length=255)
#     password = models.CharField(max_length=255)
#     email = models.EmailField()
#     first_name = models.CharField(max_length=255)
#     last_name = models.CharField(max_length=255)
