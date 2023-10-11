from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from ..models import User, Product, ShippingAddress, UserAddr, Order, Admin # OrderItem, Payment
from django.contrib.auth.hashers import check_password, make_password
from django.conf import settings
from django.core.mail import send_mail
from .views_user_auth import login
from django.contrib.sessions.models import Session
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from datetime import timedelta
import random
import uuid
import re


def product_list(request):
    message = request.session.get('message', '')
    login_email = request.session.get('login_email', None)
    verified_login = request.session.get('verified_login', None)

    products = Product.objects.all()

    request.session.pop('message', None)
    return render(request, 'index.html', {
        'products': products, 
        'login_email': login_email, 
        'verified_login':verified_login, 
        'message': message})

