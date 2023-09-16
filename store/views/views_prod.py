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




