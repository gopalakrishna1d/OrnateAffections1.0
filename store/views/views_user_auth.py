from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from ..models import User, ShippingAddress, UserAddr, Order, Admin # OrderItem, Payment
from django.contrib.auth.hashers import check_password, make_password
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.sessions.models import Session
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from datetime import timedelta
import random
import uuid
import re

def signup(request):
    if request.method == 'POST':
        email = request.POST['email'].lower()
        full_name = request.POST['full_name']
        phone = request.POST['phone']
        password = request.POST['password']
        role =  request.POST.get('role', 'customer')

        name_parts = full_name.split()

        if len(name_parts) == 1:
            first_name = name_parts[0]
            middle_name = ""
            last_name = ""

        elif len(name_parts) == 2:
            first_name = name_parts[0]
            middle_name = ""
            last_name = name_parts[1]

        else:
            first_name = name_parts[0]
            middle_name = " ".join(name_parts[1:-1])
            last_name = name_parts[1]
        
        username = request.POST.get('username', first_name)

        if not first_name or not phone or not email or not password:
            error = {'status': 'failure', 'message': 'Please fill in all the required fields'}
            return JsonResponse(error, status=400)

        if len(password) < 8:
            error = {'status': 'failure', 'message': 'Password should be at least 8 characters long'}
            return JsonResponse(error, status=400)

        if not re.match(r'^[A-Za-z]{2,}$', first_name):
            error = {'status': 'failure', 'message': 'Invalid first name'}
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

        exists = User.objects.filter(email=email).first()
        if exists is None:
            try:
                user = User.objects.create(
                    user_id= user_id, username = username, email=email, otp=otp, otp_expiration=otp_expiration, first_name=first_name, 
                    middle_name=middle_name, last_name=last_name, password=password_hash, phone=phone, is_verified=False, 
                    created_dtm=current_timestamp, modified_dtm=current_timestamp, role = role
                )
                send_mail(
                    'OTP Verification',
                    f'Greetings, your OTP to signup with Ornate Affections is: {otp} (valid only for 5 mins)',
                    settings.EMAIL_HOST_USER,
                    [email],
                    fail_silently=False,
                )
            except:
                failure={'message':'User already exists'}
                return render (request, 'signup.html', context= failure)
            
        if role == 'Admin':
            Admin.objects.create(user_id=user_id, username=username, password=password_hash, 
                                    email=email, first_name=first_name, last_name=last_name)
            return render(request, 'admin_console.html')
        else:
            user = User.objects.get(email=email.strip())
            if user is not None:
                if check_password(password, user.password):
                    request.session['login_email']= user.email
                    request.session['user_id'] = str(user.user_id)
                    success = {'message': "Please enter otp and verify your email"}
                    return render (request, 'home.html', context=success)
                else:
                    failure = {'message': 'Check your Password'}
                    return render(request, 'login.html', context=failure)
            else:
                failure = {'message': 'User does not exist. Try again and if the error persists contact customer service'}
                return render(request, 'login.html')
    failure = {'message': 'Error signing up. Contact customer service'}
    return render(request, 'signup.html')


def verify_otp(request):
    if request.method == 'POST':
        otp = request.POST['otp']
        email = request.session.get('signup_email', 'login_email')

        user = User.objects.filter(email=email).first()
        if user is not None:
            try:
                if otp == user.otp:
                    current_time = timezone.now()
                    if user.otp_expiration < current_time:
                        error = {'message': 'OTP has expired, try Regenerating OTP'}
                        return render(request, 'verify_otp.html', context=error)
                    else:
                        user.is_verified = True
                        user.save()

                        success = {'message': 'OTP verification successful, you can close this tab'}
                        return render(request, 'success.html', context=success)
                else:
                    error = {'message': 'OTP verification failure, enter valid OTP'}
                    return render(request, 'verify_otp.html', context=error)

            except Exception as e:
                error = {'message': str(e)}
                return render(request, 'verify_otp.html', context=error)
        else:
            error = {'message': 'User does not exist'}
            return render(request, 'verify_otp.html', context=error)
    elif request.method =='GET':
        return render(request, 'verify_otp.html')


def regenerate_otp(request):
    if request.method == 'GET':
        email = request.session.get('login_email')

        try:
            user = User.objects.get(email=email)

            new_otp = str(random.randint(100000, 999999))
            user.otp = new_otp
            user.otp_expiration = timezone.now()+timedelta(minutes=5)
            user.save()

            send_mail(
                'OTP Verification',
                f'Greetings, your new OTP for your Ornate Affections account is: {new_otp} (valid only for 5 mins)',
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )
            response = {'message' : 'New OTP generated. Please check your email'}
            return render(request, 'verify_otp.html', context=response) 
        except Exception as e:
            error = {'message' : str(e)}
            return render(request, 'verify_otp.html', context=error)
    else:
        return render(request, 'verify_otp.html')


########### Unverified users login is different from verified login (can add to cart but need verification to checkout)
                    

def login(request):
    def login_anyways():
        if check_password(password, user.password):
            request.session['login_email']= user.email
            request.session['user_id'] = str(user.user_id)
            return render (request, 'home.html', context=success)
        else:
            failure = {'message': 'Check your Password'}
            return render(request, 'login.html', context=failure)
        
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        try:
            user = User.objects.get(email=email.strip())
        except User.DoesNotExist:
            error = {'status': 'failure', 'message': 'User does not exist'}
            return render(request, 'login.html', context=error)
        
        if user is not None:
            if user.is_verified:
                success = {'status': 'success', 'message': f'Welcome back {user.username}'}
                return login_anyways()
            else:
                success = {'message': "Please enter otp and verify your email"}
                return login_anyways()
            
        error = {'status': 'failure', 'message': 'User does not exist'}
        return render(request, 'login.html', context=error)
    
    return render(request, 'login.html')


def reset_password(request):
    if request.method == 'POST':
        email = request.session.get('signup_email', 'login_email')
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        otp = request.POST['otp']

        if password != confirm_password:
            error = {'message': 'Passwords do not match'}
            return render(request, 'reset_password.html', context=error)
    
        password_hash = make_password(password)
        
        try:
            user = User.objects.filter(email = email).first()
        except User.DoesNotExist:
            error = {'message': 'User not found'}
            return render(request, 'reset_password.html', context=error)
        
        if user.otp == otp:
            current_time = timezone.now()
            if user.otp_expiration < current_time:
                error = {'status': 'failure', 'message': 'OTP has expired'}
                return JsonResponse(error, status=400)
            user.is_verified = True
            user.password = password_hash 
            user.save()
            return redirect('logout')
        
            success = {'status': 'success', 'message': 'OTP verified, password reset successful!!'}
            return JsonResponse(success, status=200)
        else:
            error = {'status': 'failure', 'message': 'OTP verification failure, enter valid OTP!!'}
            return JsonResponse(error, status=400)
        
    else :
        return render(request, 'reset_password.html')



# @login_required
# def home(request):
#     # This is a sample protected view that requires the user to be logged in
#     return render(request, 'home.html')


def delete_user(request):
    if request.method == "POST":
        email = request.session.get('email_id', '')
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
            
            
            
            
########## HTML page for confirm user delete
######## User-Settings page and options in the settings page

def logout(request):
    # Clear session variables to log the user out
    message = "You have been logged out successfully"
    request.session.clear()
    return render (request, 'login.html')