from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404
from django.contrib.auth.decorators import login_required
from ..models import User, Product, Cart, WishList, ShippingAddress, UserAddr, Review , Order#, OrderItem, Payment
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.hashers import check_password, make_password
from django.conf import settings
from .views_user_auth import login
from django.core.mail import send_mail
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta
import random
import uuid
import re


def add_ornate_af_product(request):
    if request.method == "POST":
        user_id = request.session.get('user_id', '')
        product_name = request.POST['product_name']
        description = request.POST['description']
        price = request.POST['price']
        stock_quantity = request.POST['stock_quantity']

        try:
            user = get_object_or_404(User, user_id=user_id)
            if user.role == 'Admin':
                if user.is_verified:
                    Product.objects.create(description= description, product_name= product_name, price=price, stock_quantity=stock_quantity)

                    success = {'message':'Product added successfully'}
                    return render(request, 'admin/add_product.html', context=success)
                else:
                    error = {'message':'Please verify your OTP to perform any activity'}
                    return render(request, 'admin/add_product.html', context=error)
            else:
                error = {'message':'You are not authorized to add a product'}
                return render(request, 'admin/add_product.html', context=error)

        except Exception as e:
            print (e)
            error = {'message':'Problem adding product'}
            return render(request, 'admin/add_product.html', context=error)
    return render(request, 'admin/add_product.html')



def product_list(request):
    products = Product.objects.all()
    return render(request, 'admin/product_list.html', {'products': products})


def update_ornate_af_prod_details(request):
    if request.method == 'POST':
        user_id = request.session.get('user_id', '')
        product_id = request.POST['product_id']
        
        try:
            user = get_object_or_404(User, user_id=user_id)
            if user.role == 'Admin':
                if user.is_verified:
                    product = Product.objects.filter(product_id=product_id).first()
                    product_name = request.POST.get('product_name')
                    description = request.POST.get('description')
                    price = request.POST.get('price')
                    stock_quantity = request.POST.get('stock_quantity')

                    if not product_name:
                        product_name= product.product_name
                    if not description:
                        description= product.description
                    if not price:
                        price= product.price
                    if not stock_quantity:
                        stock_quantity = product.stock_quantity
                        
                    prod_update = Product(product_id=product_id, product_name=product_name, description=description, price=price, stock_quantity=stock_quantity)
                    prod_update.save()

                    success = {'message':'Product updated successfully'}
                    return render(request, 'admin/update_product.html', context=success)
                else:
                    error = {'message':'Please verify your OTP to perform any activity'}
                    return render(request, 'admin/update_product.html', context=error)
            else:
                error = {'message':'You are not authorized to update a product'}
                return render(request, 'admin/update_product.html', context=error)
                    
        except Exception as e:
            print(e)
            error = {'message':'Problem adding product'}
            return render(request, 'admin/update_product.html', context=error)
    return render(request, 'admin/update_product.html')



# # Product Detail View
# def product_detail(request, product_id):
#     product = get_object_or_404(Product, pk=product_id)
#     reviews = Review.objects.filter(product=product)
#     return render(request, 'product_detail.html', {'product': product, 'reviews': reviews})