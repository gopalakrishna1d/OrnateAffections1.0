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


def add_product(request):
    if request.method == "POST":
        product_name = request.POST['product_name']
        description = request.POST['description']
        price = request.POST['price']
        stock_quantity = request.POST['stock_quantity']

        try:
            product = Product.objects.create(description= description, product_name= product_name, price=price, stock_quantity=stock_quantity)

            success = {'status': 'Success','message':'Product added successfully'}
            return JsonResponse (success, status = 200)
        except Exception as e:
            print (e)
            error = {'status': 'Failure','message':'Problem adding product'}
            return JsonResponse(error, status=400)

# #from .forms import RegistrationForm

# # Product List View
# def product_list(request):
#     products = Product.objects.all()
#     return render(request, 'product_list.html', {'products': products})

# # Product Detail View
# def product_detail(request, product_id):
#     product = get_object_or_404(Product, pk=product_id)
#     reviews = Review.objects.filter(product=product)
#     return render(request, 'product_detail.html', {'product': product, 'reviews': reviews})





# # Order Confirmation View
# @login_required
# def order_confirmation(request):
#     user = request.user
#     orders = Order.objects.filter(user=user, order_status='Pending')
#     return render(request, 'order_confirmation.html', {'orders': orders})

# # Review Submission View
# @login_required
# def submit_review(request, product_id):
#     if request.method == 'POST':
#         product = get_object_or_404(Product, pk=product_id)
#         rating = request.POST.get('rating')
#         review_text = request.POST.get('review_text')

#         # Create a new review for the product
#         Review.objects.create(user=request.user, product=product, rating=rating, review_text=review_text)

#         # Redirect back to the product detail page
#         return redirect('product_detail', product_id=product_id)

#     return redirect('product_list')


# # Payment View (simplified)
# @login_required
# def make_payment(request):
#     if request.method == 'POST':
#         order_id = request.POST.get('order_id')  # Get the order to be paid
#         order = get_object_or_404(Order, pk=order_id)
#         payment_method = request.POST.get('payment_method')

#         # Handle payment processing here
#         # Create a payment record, update order status, etc.

#         return redirect('payment_confirmation')
#     return redirect('cart')

# # Payment Confirmation View
# @login_required
# def payment_confirmation(request):
#     return render(request, 'payment_confirmation.html')



