from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from ..models import User, ShippingAddress, UserAddr, Order, Admin, OrderItem, Payment
from django.contrib.auth.hashers import check_password, make_password
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.sessions.models import Session
from django.http import JsonResponse, HttpResponseRedirect
from django.utils import timezone
from datetime import timedelta
import random
import uuid
import re

###########Add country code to the phone number

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
                return render (request, 'auth/signup.html', context= failure)
            
        if role == 'Admin':
            Admin.objects.create(user_id=user_id, username=username, password=password_hash, 
                                    email=email, first_name=first_name, last_name=last_name)
            return render(request, 'admin/admin_console.html')
        else:
            user = User.objects.get(email=email.strip())
            if user is not None:
                if check_password(password, user.password):
                    request.session['login_email']= user.email
                    request.session['user_id'] = str(user.user_id)
                    request.session['message'] = f'Welcome {user.username}, Please verify OTP and activate your account'
                    return redirect('/')
                else:
                    failure = {'message': 'Check your Password'}
                    return render(request, 'auth/login.html', context=failure)
            else:
                failure = {'message': 'User does not exist. Try again and if the error persists contact customer service'}
                return render(request, 'auth/login.html')
    failure = {'message': 'Error signing up. Contact customer service'}
    return render(request, 'auth/signup.html')


def verify_otp(request):
    if request.method == 'POST':
        otp = request.POST['otp']
        email = request.session.get('login_email', '')

        user = User.objects.filter(email=email).first()
        if user is not None:
            try:
                if otp == user.otp:
                    current_time = timezone.now()
                    if user.otp_expiration < current_time:
                        error = {'message': 'OTP has expired, try Regenerating OTP'}
                        return render(request, 'auth/verify_otp.html', context=error)
                    else:
                        user.is_verified = True
                        user.save()

                        success = {'message': 'OTP verification successful'}
                        return render(request, 'auth/success.html', context=success)
                else:
                    error = {'message': 'OTP verification failure, enter valid OTP'}
                    return render(request, 'auth/verify_otp.html', context=error)

            except Exception as e:
                error = {'message': str(e)}
                return render(request, 'auth/verify_otp.html', context=error)
        else:
            error = {'message': 'User does not exist'}
            return render(request, 'auth/verify_otp.html', context=error)
    elif request.method =='GET':
        return render(request, 'auth/verify_otp.html')


def generate_otp(request, purpose):
    if request.method == 'GET':
        if purpose == 'verify':
            email = request.session.get('login_email', '')
            redirect_url = 'auth/verify_otp.html'
        elif purpose == 'reset':
            email = request.session.get('forgot_email','')
            redirect_url = 'auth/forgot_password.html'
        else:
            error = {'message': 'Invalid purpose'}
            return render(request, 'auth/invalid.html', context=error)

        try:
            user = User.objects.get(email=email)

            new_otp = str(random.randint(100000, 999999))
            user.otp = new_otp
            user.otp_expiration = timezone.now() + timedelta(minutes=5)
            user.save()

            if purpose == 'verify':
                email_subject = 'OTP Verification'
            elif purpose == 'reset':
                email_subject = 'Password Reset OTP'

            email_message = f'Use this OTP to {purpose}: {new_otp} (valid only for 5 mins)'

            send_mail(
                email_subject,
                email_message,
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )

            response = {'message': 'New OTP generated. Please check your email'}
            return render(request, redirect_url, context=response)

        except Exception as e:
            error = {'message': str(e)}
            return render(request, 'auth/invalid.html', context=error)
    else:
        if purpose == 'verify':
            return render(request, 'auth/verify_otp.html')
        elif purpose == 'reset':
            return render(request, 'auth/password_otp.html')



# def home(request):
#     # This is a sample protected view that requires the user to be logged in
#     return render(request, 'index.html')


def login(request):
    def login_anyways():
        if check_password(password, user.password):
            request.session['login_email']= user.email
            request.session['user_id'] = str(user.user_id)
            if user.role == 'Admin':
                success = {'message': f'Welcome back {user.username}'}
                return render (request, 'admin/admin_console.html', context=success)
            else:
                if user.is_verified:
                    request.session['verified_login']= user.email
                    request.session['message'] = f'Welcome back {user.username}'
                    return redirect('/')
                else:
                    request.session['message'] = f'Welcome {user.username}, Please enter OTP and verify your account'
                    return redirect('/')
        else:
            failure = {'message': 'Check your Password'}
            return render(request, 'auth/login.html', context=failure)
        
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        try:
            user = User.objects.get(email=email.strip())
        except User.DoesNotExist:
            error = {'status': 'failure', 'message': 'User does not exist'}
            return render(request, 'auth/login.html', context=error)
        
        if user is not None:
                return login_anyways()
            
        error = {'status': 'failure', 'message': 'User does not exist'}
        return render(request, 'auth/login.html', context=error)
    
    return render(request, 'auth/login.html')


def settings(request):
    email = request.session.get('login_email', '')
    return render(request, 'settings.html')


def forgoten_password(request):
    if request.method == 'POST':
        email = request.POST['email']
        request.session['forgot_email']=email
        return render(request, 'auth/forgot_password.html')
    else:
        return render(request, 'auth/password_otp.html')


def reset_password(request, purpose):
    if request.method == 'POST':
        if purpose == 'logged_in':
            email = request.session.get('login_email')
            previous_password = request.POST['previous_password']
            password = request.POST['password']
            confirm_password = request.POST['confirm_password']

            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return render(request, 'auth/reset_password.html', {'message': 'User not found'})

            if password != confirm_password:
                return render(request, 'auth/reset_password.html', {'message': 'New Passwords do not match'})

            if not check_password(previous_password, user.password):
                return render(request, 'auth/reset_password.html', {'message': 'Incorrect previous password'})

            user.password = make_password(password)
            user.save()
            return redirect('logout')

        elif purpose == 'forgot_password':
            email = request.session.get('forgot_email')
            otp = request.POST.get('otp')
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')

            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return render(request, 'auth/forgot_password.html', {'message': 'User not found'})

            if user.otp == otp:
                current_time = timezone.now()
                if user.otp_expiration < current_time:
                    return render(request, 'auth/forgot_password.html', {'message': 'OTP has expired, generate a new one'})

                if password != confirm_password:
                    return render(request, 'auth/forgot_password.html', {'message': 'New Passwords do not match'})

                user.password = make_password(password)
                user.is_verified = True
                user.save()

                success = {'message': 'Password reset successful!'}
                return render(request, 'auth/success.html', context=success) 
            return render(request, 'auth/forgot_password.html', {'message': 'OTP verification failure, enter valid OTP!!'})

    elif request.method == 'GET':
        if purpose == 'logged_in':
            return render(request, 'auth/reset_password.html')
        elif purpose == 'forgot_password':
            return render(request, 'auth/forgot_password.html')
    
    return render(request, 'auth/reset_password.html', {'message': 'Invalid Request'})




############## SEND MAIL TO USER THAT ACCOUNT DELETED

def delete_user(request):
    if request.method == "POST":
        email = request.session.get('login_email', '')
        password = request.POST['password']
        
        user =  User.objects.filter(email=email).first()
        if not check_password(password, user.password):
            error= {'message' : 'Incorrect Password. Try again.'}
            return render(request, 'auth/delete_user.html', context=error)
        
        try:
            user_addr = UserAddr.objects.filter(user=user).first()
            order = Order.objects.filter(user=user, order_status='Delivered').first()

            if order:
                
                error= {'message' : 'You have undelivered orders. Contact customer service for information.'}
                return render(request, 'index.html', context=error)
            
            if user_addr:
                user_addr.delete()

            # Log the user out and delete the account
            logout(request)
            user.delete()

            success= {'message' : 'Account deleted successfully. We are sad seeing you go :('}
            return render(request, 'auth/signup.html', context=success)
        
        except Exception as e:
            print(e)
            error= {'message': 'An error occurred while deleting your account.'}
            return render(request, 'auth/delete_user.html', context=error)

    return render(request, 'auth/delete_user.html')
        
        
        
####### User-Settings page and options in the settings page

def logout(request):
    # Clear session variables to log the user out
    request.session.clear()
    success = {'message': "You have been logged out successfully"}
    return render (request, 'auth/login.html', context= success)