from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404
from django.contrib.auth.decorators import login_required
from ..models import User, Product, Cart, WishList, ShippingAddress, UserAddr, Review , Order#, OrderItem, Payment
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.hashers import check_password, make_password
from django.conf import settings
from django.core.mail import send_mail
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta
import random
import uuid
import re


########### ORDERS contains all shipping addr values in a single column called address, has user_id, user_name.
######### CHECKOUT
######### PAYMENT
######### PAYMENT confirmation
######### Order Confirmation
######### ORDER CANCEL
######### DELETE ORDER
######### REVIEW
######### view orders




@login_required
def checkout(request):
    user_id = request.user
    cart = Order.objects.filter(user_id=user_id, order_status='Cart').first()

    if cart:
        # Calculate total price and handle payment processing here
        total_price = sum(item.subtotal_price for item in cart.orderitem_set.all())

        # Create a new order with the 'Pending' status
        order = Order.objects.create(user=user, total_price=total_price, order_status='Pending')

        # Copy items from the cart to the new order
        for item in cart.orderitem_set.all():
            OrderItem.objects.create(order=order, product=item.product, quantity=item.quantity, subtotal_price=item.subtotal_price)

        # Clear the cart
        cart.delete()

        return redirect('order_confirmation')

    return redirect('cart') 