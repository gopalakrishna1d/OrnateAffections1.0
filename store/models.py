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
    phone = models.CharField(max_length=20, unique=True)
    otp = models.CharField(max_length=7, null=False, default= not None)
    otp_expiration = models.DateTimeField(default=timezone.now)
    created_dtm = models.DateTimeField(default= None)
    modified_dtm = models.DateTimeField(default= None)
    role = models.CharField(max_length=20, default='Customer', choices=[('Customer', 'Customer'), ('Admin', 'Admin')])
    display_picture = models.ImageField(default=None)


class ShippingAddress(models.Model):
    addr_id = models.CharField(primary_key=True, max_length=10)
    name = models.CharField(max_length=32)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    postal_code = models.CharField(max_length=20)

    def save(self, *args, **kwargs):
        if not self.addr_id:
            highest_existing_address = ShippingAddress.objects.filter(addr_id__startswith='addr').order_by('-addr_id').first()

            if highest_existing_address:
                numeric_part = int(highest_existing_address.addr_id[4:]) + 1
            else:
                numeric_part = 1

            self.addr_id = f'addr{str(numeric_part).zfill(3)}'

        super(ShippingAddress, self).save(*args, **kwargs)


class UserAddr(models.Model):
    user=models.ForeignKey(User, on_delete=models.CASCADE)
    addr=models.ForeignKey(ShippingAddress, primary_key=True, on_delete=models.DO_NOTHING)


class Product(models.Model):
    product_id = models.CharField(max_length=10, primary_key=True)
    product_name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.IntegerField()

    def save(self, *args, **kwargs):
        if not self.product_id:
            highest_existing_product = Product.objects.filter(product_id__startswith='prod').order_by('-product_id').first()

            if highest_existing_product:
                numeric_part = int(highest_existing_product.product_id[4:]) + 1
            else:
                numeric_part = 1

            self.product_id = f'prod{str(numeric_part).zfill(3)}'

        super(Product, self).save(*args, **kwargs)




class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.DO_NOTHING)
    quantity = models.IntegerField(default=1)

    class Meta:
        unique_together = ('user', 'product')

class WishList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.DO_NOTHING)

    class Meta:
        unique_together = ('user', 'product')

# # Category model
# class Category(models.Model):
#     category_name = models.CharField(max_length=255)


# Order model
#######if order deleted???
class Order(models.Model):
    order_id = models.CharField(max_length=20, primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    user_name = models.CharField(max_length=32)
    addr = models.ForeignKey(ShippingAddress, on_delete=models.DO_NOTHING, null=True)
    order_date = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    order_status = models.CharField(max_length=20, default='Cart', choices=[('Cart', 'Cart'), ('Order Placed', 'Order Placed'),('Out for delivery', 'Out for delivery'),('Delivered', 'Delivered')])

    def save(self, *args, **kwargs):
        if not self.order_id:
            highest_existing_order = Order.objects.filter(order_id__startswith='order').order_by('-order_id').first()

            if highest_existing_order:
                numeric_part = int(highest_existing_order.order_id[5:]) + 1
            else:
                numeric_part = 1

            self.order_id = f'order{str(numeric_part).zfill(3)}'

        super(Order, self).save(*args, **kwargs)


# OrderItem model
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    subtotal_price = models.DecimalField(max_digits=10, decimal_places=2)

# Payment model
class Payment(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    payment_date = models.DateTimeField(auto_now_add=True)
    payment_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50)
    payment_status = models.CharField(max_length=20)


class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ordered_product = models.ForeignKey(Product, on_delete=models.DO_NOTHING)
    rating = models.IntegerField()
    review_text = models.TextField()
    date_posted = models.DateTimeField(auto_now_add=True)

# Admin model (if applicable)
class Admin(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    email = models.EmailField(unique=True, primary_key=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
