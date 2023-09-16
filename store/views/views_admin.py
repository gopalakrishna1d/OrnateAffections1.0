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


######### ADMIN CONSOLE (admin required endpoints and pages)
######### ADMIN LOGIN (If user exists in user and admin tables)
######### ADD and manipulate product and other product related details but only read user and user data)


######## A command to delete the old orders if they are in orders table past 3 days and add that to cart



# from django.shortcuts import render, redirect, get_object_or_404
# from .models import User, ShippingAddress, UserAddr

# def select_shipping_address(request):
#     user_id = request.GET.get('user_id')  # Get the user_id from the request
#     user = get_object_or_404(User, user_id=user_id)
    
#     # Get all shipping addresses associated with the user
#     user_addresses = UserAddr.objects.filter(user=user)
    
#     context = {
#         'user_addresses': user_addresses,
#         'user_id': user_id,
#     }
    
#     return render(request, 'select_shipping_address.html', context)