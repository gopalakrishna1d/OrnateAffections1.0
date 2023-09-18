from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404
from django.contrib.auth.decorators import login_required
from ..models import User, ShippingAddress, UserAddr, Order, Admin # OrderItem, Payment
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.hashers import check_password, make_password
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.sessions.models import Session
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta
import random
import uuid
import re

def signup(request):
    if request.method == 'POST':
        email = request.POST['email'].lower()
        username = request.POST['username']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        phone = request.POST['phone']
        password = request.POST['password']
        role =  request.POST['role']

        if not first_name or not last_name or not phone or not email or not password:
            error = {'status': 'failure', 'message': 'Please fill in all the required fields'}
            return JsonResponse(error, status=400)
        
        if not username:
            username = first_name

        if role is None:
            role = 'Customer'

        if len(password) < 8:
            error = {'status': 'failure', 'message': 'Password should be at least 8 characters long'}
            return JsonResponse(error, status=400)

        if not re.match(r'^[A-Za-z]{2,}$', first_name):
            error = {'status': 'failure', 'message': 'Invalid first name'}
            return JsonResponse(error, status=400)

        if not re.match(r'^[A-Za-z]{2,}$', last_name):
            error = {'status': 'failure', 'message': 'Invalid last name'}
            return JsonResponse(error, status=400)

        if not re.match(r'^\d{10}$', phone):
            error = {'status': 'failure', 'message': 'Invalid phone number'}
            return JsonResponse(error, status=400)

        if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
            error = {'status': 'failure', 'message': 'Invalid email address'}
            return JsonResponse(error, status=400)
        
        user_id = uuid.uuid4()

        otp = str(random.randint(100000, 999999))
        otp_expiration = timezone.now() + timedelta(minutes=5)
        
        password_hash = make_password(password)
        current_timestamp = timezone.now()

        user = User.objects.create(
            user_id= user_id, username = username, email=email, otp=otp, otp_expiration=otp_expiration, first_name=first_name,
            last_name=last_name, password=password_hash, phone=phone, is_verified=False, 
            created_dtm=current_timestamp, modified_dtm=current_timestamp, role = role
        )

        if role == 'Admin':
            Admin.objects.create(user_id=user_id, username=username, password=password_hash, email=email, first_name=first_name, last_name=last_name)

        send_mail(
            'OTP Verification',
            f'Greetings, your OTP to signup with Ornate Affections is: {otp} (valid only for 5 mins)',
            settings.EMAIL_HOST_USER,
            [email],
            fail_silently=False,
        )
        
        success = {'status': 'success', 'message': 'Signup successful! Please check your email for the OTP.'}
        
        request.session['signup_email'] = email
        return render(request, 'verify_otp.html')
    
    return render(request, 'signup.html')
        # return JsonResponse(success, status=200)


def verify_otp(request):
    if request.method == 'POST':
        otp = request.POST['otp']

        email = request.session.get('signup_email', '')

        user = User.objects.filter(email =email).first()
        if user is not None:
            try:
                if otp == user.otp:
                    current_time = timezone.now()
                    if user.otp_expiration < current_time:
                        error = {'status': 'failure', 'message': 'OTP has expired'}
                        return JsonResponse(error, status=400)

                    user.is_verified = True
                    user.save()
                    
                    # success = {'status': 'success', 'message': 'OTP verification successful'}
                    return render(request, 'login.html')
                else:
                    error = {'status': 'failure', 'message': 'OTP verification failure, enter valid OTP'}
                    return render(request, error, 'verify_otp.html')

            except ObjectDoesNotExist:
                error = {'status': 'failure', 'message': 'User does not exist'}
                return JsonResponse(error, status=400)
        else:
            error = {'status': 'failure', 'message': 'User does not exist'}
            return JsonResponse(error, status=400)
    return JsonResponse(error, status=400)


def regenerate_otp(request):
    if request.method == 'POST':
        email = request.POST['email'].lower()

        try:
            user = User.objects.get(email=email)

            new_otp = str(random.randint(100000, 999999))
            user.otp = new_otp
            user.otp_expiration = timezone.now()+timedelta(minutes=1)
            user.save()

            send_mail(
                'OTP Verification',
                f'Greetings, your new OTP for Ornate Affections account is: {new_otp} (valid only for 5 mins)',
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )
            response = {
                'status' : 'success',
                'message' : 'New OTP generated',
                'new_otp' : new_otp
            }
            return JsonResponse(response,status=200)
        except User.DoesNotExist:
            error = {'status' : 'failure', 'message' : 'User not found'}
            return JsonResponse(error, status=400)
        except Exception as e:
            return JsonResponse({'status' : 'Failure', 'message' : 'Invalid request'}, status=400)


def reset_password(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        otp = request.POST['otp']
        
        password_hash = make_password(password)

        if password != confirm_password:
                error = {'status': 'failure', 'message': 'Passwords do not match'}
                return JsonResponse(error, status=400)
        
        user = User.objects.filter(email = email).first()

        if user.otp == otp:
            #Check if OTP has expired
            current_time = timezone.now()
            if user.otp_expiration < current_time:
                error = {'status': 'failure', 'message': 'OTP has expired'}
                return JsonResponse(error, status=400)
            user.is_verified = True
            user.password = password_hash 
            user.save()
                
            success = {'status': 'success', 'message': 'OTP verified, password reset successful!!'}
            return JsonResponse(success, status=200)
            
        elif ObjectDoesNotExist:
            error = {'status': 'failure', 'message': 'OTP verification failure, enter valid OTP!!'}
            return JsonResponse(error, status=400)
    return JsonResponse({'status' : 'failure', 'message' : 'reset failed'}, status=400)


def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        try:
            user = User.objects.get(email=email.strip())
        except User.DoesNotExist:
            error = {'status': 'failure', 'message': 'User does not exist'}
            return JsonResponse(error, status=400)
        
        if user is not None:
            if user.is_verified:
                if check_password(password, user.password):
                    user_details = {
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'email': user.email.lower(),
                    'phone': user.phone,
                    'user_id': user.user_id
                }
                    success = {
                            'status': 'success',
                            'message': f'Successfully logged in as {email}',
                            'data': user_details
                        } # Redirect to the homepage after successful login
                    return JsonResponse (success, status = 200)
                else:
                    error = {
                    'status': 'failure',
                    'message': 'Login failure, check the entered details and if the user is valid'
                }
                return JsonResponse(error, status=400)

            else:
                failure = {
                        'status': 'failure',
                        'message': 'User not verified. Try OTP verification'
                    }
                return JsonResponse (failure, status = 400)

    error = {'status': 'failure', 'message': 'Unable to login', 'data': {}}
    return JsonResponse(error, status=400) #return render(request, 'login.html')

# @login_required
# def home(request):
#     # This is a sample protected view that requires the user to be logged in
#     return render(request, 'home.html')

def delete_user(request):
    if request.method == "POST":
        email = request.POST['email']
        user = User.objects.filter(email=email).first()

        if user is not None:
            try:
                user_addr = UserAddr.objects.filter(user_id=user.user_id).first()

                if user_addr:
                    shipping_addr = get_object_or_404(ShippingAddress, addr_id=user_addr.addr_id)

                    orders_with_address = Order.objects.filter(addr=shipping_addr)

                    if orders_with_address.exists():
                        return JsonResponse({'status': 'Failure', 'message': 'Cannot delete user, associated orders exist.'}, status=400)
                    
                    user_addr.delete()
                    shipping_addr.delete()

                user.delete()

                success = {'status': 'Success', 'message': 'User deleted successfully'}
                return JsonResponse(success, status=200)
            except Exception as e:
                print(e)
                error = {'status': 'Failure', 'message': 'Check the details and try again'}
                return JsonResponse(error, status=400)
        else:
            error = {'status': 'Failure', 'message': 'User not found'}
            return JsonResponse(error, status=400)