from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404
from django.contrib.auth.decorators import login_required
from .models import User, Product, Cart, WishList, ShippingAddress, UserAddr, Review , Order#, OrderItem, Payment
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

#from django.contrib import auth




def signup(request):
    if request.method == 'POST':
        email = request.POST['email'].lower()
        username = request.POST['username']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        phone = request.POST['phone']
        password = request.POST['password']
        role = 'Customer' or request.POST['role']

        if not first_name or not last_name or not phone or not email or not password:
            error = {'status': 'failure', 'message': 'Please fill in all the required fields'}
            return JsonResponse(error, status=400)
        
        if not username:
            username = first_name

        if not role:
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

        send_mail(
            'OTP Verification',
            f'Greetings, your OTP to signup with Ornate Affections is: {otp} (valid only for 5 mins)',
            settings.EMAIL_HOST_USER,
            [email],
            fail_silently=False,
        )
        
        success = {'status': 'success', 'message': 'Signup successful! Please check your email for the OTP.'}
        return JsonResponse(success, status=200)


def verify_otp(request):
    if request.method == 'POST':
        otp = request.POST['otp']
        email = request.POST['email']
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
                    
                    success = {'status': 'success', 'message': 'OTP verification successful'}
                    return JsonResponse(success, status=200)
                else:
                    error = {'status': 'failure', 'message': 'OTP verification failure, enter valid OTP'}
                    return JsonResponse(error, status=400)

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



# Product section

def add_product(request):
    if request.method == "POST":
        product_name = request.POST['product_name']
        description = request.POST['description']
        price = request.POST['price']
        stock_quantity = request.POST['stock_quantity']

        product_id = uuid.uuid4()

        try:
            product = Product.objects.create(description= description, product_name= product_name, price=price, stock_quantity=stock_quantity)

            success = {'status': 'Success','message':'Product added successfully'}
            return JsonResponse (success, status = 200)
        except Exception as e:
            print (e)
            error = {'status': 'Failure','message':'Problem adding product'}
            return JsonResponse(error, status=400)



# Cart and Wishlist section

def add_to_cart(request):
    if request.method == 'POST':
        user_id = request.POST['user_id']
        product_id = request.POST['product_id']
        quantity = request.POST['quantity']

        try:
            user = User.objects.filter(user_id = user_id).first()
            product = Product.objects.filter(product_id = product_id).first()
            if product is not None:
                if user is not None:
                    Cart.objects.create(user_id=user_id, product_id= product_id, quantity= quantity)

                    success = {'status': 'Success', 'message': 'Successfully added to cart'}
                    return JsonResponse(success, status = 200)
                else:
                    error= {'status': 'Failure', 'message': 'User not fount'}
                    return JsonResponse (error, status = 404)
            else:
                error= {'status': 'Failure', 'message': 'Product not fount'}
                return JsonResponse (error, status = 404)
        except Exception as e:
            print(e)
            error = {'status': 'Failure', 'message': 'Error adding to cart'}
            return JsonResponse(error, status = 400)


def get_cart_items(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        if user_id is not None:
            try:
                carts = get_list_or_404(Cart, user_id=user_id)
                cart_data = []

                for cart in carts:
                    product = get_object_or_404(Product, product_id=cart.product_id)

                    product_details = {
                        'Product_name': product.product_name,
                        'Product_description': product.description,
                        'quantity': cart.quantity
                    }
                    cart_data.append(product_details)

                response_data = {
                    'status': 'Success',
                    'message': 'Carts fetched successfully',
                    'data': cart_data
                }
                return JsonResponse(response_data, status=200)

            except Cart.DoesNotExist:
                error = {'status': 'Failure', 'message': 'Carts not found'}
                return JsonResponse(error, status=404)

            except Product.DoesNotExist:
                error = {'status': 'Failure', 'message': 'Product not found'}
                return JsonResponse(error, status=404)

            except Exception as e:
                error = {'status': 'Failure', 'message': str(e)}
                return JsonResponse(error, status=400)

        else:
            error = {'status': 'Failure', 'message': 'user_id is required'}
            return JsonResponse(error, status=400)


def add_to_wishlist(request):
    if request.method == 'POST':
        user_id = request.POST['user_id']
        product_id = request.POST['product_id']

        try:
            user = User.objects.filter(user_id = user_id).first()
            product = Product.objects.filter(product_id = product_id).first()
            if product is not None:
                if user is not None:
                    WishList.objects.create(user_id=user_id, product_id= product_id)

                    success = {'status': 'Success', 'message': 'Successfully added to wishlist'}
                    return JsonResponse(success, status = 200)
                else:
                    error= {'status': 'Failure', 'message': 'User not fount'}
                    return JsonResponse (error, status = 404)
            else:
                error= {'status': 'Failure', 'message': 'Product not fount'}
                return JsonResponse (error, status = 404)
        except Exception as e:
            print(e)
            error = {'status': 'Failure', 'message': 'Error adding to wishlist'}
            return JsonResponse(error, status = 400)


def get_wishlist_items(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        if user_id is not None:
            try:
                wishlist = get_list_or_404(WishList, user_id=user_id)
                wishlist_data = []

                for wishlist in wishlist:
                    product = get_object_or_404(Product, product_id=wishlist.product_id)

                    product_details = {
                        'Product_name': product.product_name,
                        'Product_description': product.description
                    }
                    wishlist_data.append(product_details)

                response_data = {
                    'status': 'Success',
                    'message': 'wishlist fetched successfully',
                    'data': wishlist_data
                } 
                return JsonResponse(response_data, status=200)

            except WishList.DoesNotExist:
                error = {'status': 'Failure', 'message': 'Wishlist not found'}
                return JsonResponse(error, status=404)

            except Product.DoesNotExist:
                error = {'status': 'Failure', 'message': 'Product not found'}
                return JsonResponse(error, status=404)

            except Exception as e:
                error = {'status': 'Failure', 'message': str(e)}
                return JsonResponse(error, status=400)

        else:
            error = {'status': 'Failure', 'message': 'user_id is required'}
            return JsonResponse(error, status=400)


def move_to_cart(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        product_id = request.POST.get('product_id')

        if user_id is not None and product_id is not None:
            try:
                product = get_object_or_404(Product, product_id=product_id)
                wishlist_item = get_object_or_404(WishList, user_id=user_id, product_id=product_id)

                cart_item, created = Cart.objects.get_or_create(user_id=user_id, product_id=product_id)

                cart_item.quantity += 1
                cart_item.save()

                wishlist_item.delete()

                success = {'status': 'Success', 'message': 'Product moved to cart'}
                return JsonResponse(success, status=200)
                
            except Product.DoesNotExist:
                error = {'status': 'Failure', 'message': 'Product not found'}
                return JsonResponse(error, status=404)

            except WishList.DoesNotExist:
                error = {'status': 'Failure', 'message': 'Product not found in the wishlist'}
                return JsonResponse(error, status=404)

            except Exception as e:
                error = {'status': 'Failure', 'message': str(e)}
                return JsonResponse(error, status=400)

        else:
            error = {'status': 'Failure', 'message': 'user_id and product_id are required'}
            return JsonResponse(error, status=400)

    else:
        error = {'status': 'Failure', 'message': 'Only POST requests are allowed'}
        return JsonResponse(error, status=405)


def save_for_later(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        product_id = request.POST.get('product_id')

        if user_id is not None and product_id is not None:
            try:
                product = get_object_or_404(Product, product_id=product_id)
                cart_item = get_object_or_404(Cart, user_id=user_id, product_id=product_id)

                wishlist_item, created = WishList.objects.get_or_create(user_id=user_id, product_id=product_id)

                wishlist_item.save()

                cart_item.delete()

                success = {'status': 'Success', 'message': 'Product moved to Wishlist'}
                return JsonResponse(success, status=200)
                
            except Product.DoesNotExist:
                error = {'status': 'Failure', 'message': 'Product not available'}
                return JsonResponse(error, status=404)

            except WishList.DoesNotExist:
                error = {'status': 'Failure', 'message': 'Product not found in the Wishlist'}
                return JsonResponse(error, status=404)

            except Exception as e:
                error = {'status': 'Failure', 'message': str(e)}
                return JsonResponse(error, status=400)

        else:
            error = {'status': 'Failure', 'message': 'user_id and product_id are required'}
            return JsonResponse(error, status=400)

    else:
        error = {'status': 'Failure', 'message': 'Only POST requests are allowed'}
        return JsonResponse(error, status=405)


def delete_from_cart(request):
    if request.method=="POST":
        user_id = request.POST['user_id']
        product_id = request.POST['product_id']
        if user_id is not None and product_id is not None:
            try:
                cart = get_object_or_404(Cart, user_id=user_id, product_id=product_id)
                cart.delete()

                success = {'status': 'Success', 'message': 'Product deleted from cart'}
                return JsonResponse(success, status=200)
            
            except Cart.DoesNotExist:
                error = {'status': 'Failure', 'message': 'Product already deleted'}
                return JsonResponse(error, status=404)
            
            except Exception as e:
                error = {'status': 'Failure', 'message': str(e)}
                return JsonResponse(error, status=400)
            
        else:
            error = {'status': 'Failure', 'message': 'user_id and product_id are required'}
            return JsonResponse(error, status=400)
        
    else:
        error = {'status': 'Failure', 'message': 'Only POST requests are allowed'}
        return JsonResponse(error, status=405)


def remove_from_wishlist(request):
    if request.method=="POST":
        user_id = request.POST['user_id']
        product_id = request.POST['product_id']
        if user_id is not None and product_id is not None:
            try:
                wishlist_item = get_object_or_404(WishList, user_id=user_id, product_id=product_id)
                wishlist_item.delete()

                success = {'status': 'Success', 'message': 'Product removed from wishlist'}
                return JsonResponse(success, status=200)
            
            except WishList.DoesNotExist:
                error = {'status': 'Failure', 'message': 'Product already removed'}
                return JsonResponse(error, status=404)
            
            except Exception as e:
                error = {'status': 'Failure', 'message': str(e)}
                return JsonResponse(error, status=400)
            
        else:
            error = {'status': 'Failure', 'message': 'user_id and product_id are required'}
            return JsonResponse(error, status=400)
        
    else:
        error = {'status': 'Failure', 'message': 'Only POST requests are allowed'}
        return JsonResponse(error, status=405)



# Shipping address
def shipping_addr(request):
    if request.method == "POST":
        user_id = request.POST.get('user_id')
        name = request.POST.get('name')
        address = request.POST.get('address')
        city = request.POST.get('city')
        state = request.POST.get('state')
        postal_code = request.POST.get('postal_code')
        phone = request.POST.get('phone')

        user = get_object_or_404(User, user_id=user_id)

        if not phone:
            phone = user.phone

        try:
            shipping_address = ShippingAddress.objects.create(
                name=name, address=address, city=city, state=state, phone=phone, postal_code=postal_code
            )

            addr_id = shipping_address.addr_id

            UserAddr.objects.create(user=user, addr_id=addr_id)


            success = {'status': 'Success', 'message': 'Shipping address added successfully'}
            return JsonResponse(success, status=201)

        except Exception as e:
            print(e)
            error = {'status': 'Failure', 'message': str(e)}
            return JsonResponse(error, status=400)


def delete_addr(request):
    if request.method == "POST":
        user_id = request.POST.get('user_id')
        addr_id = request.POST.get('addr_id')
        try:
            shipping_address = get_object_or_404(ShippingAddress, addr_id=addr_id)

            orders_with_address = Order.objects.filter(addr_id=shipping_address)

            UserAddr.objects.filter(addr_id=addr_id).delete()

            if orders_with_address.exists():
                return JsonResponse({'status': 'Failure', 'message': 'Cannot delete address, associated orders exist.'}, status=400)
            else:
                shipping_address.delete()


            return JsonResponse({'status': 'Success', 'message': 'Shipping address deleted successfully'}, status=204)

        except Exception as e:
            print(e)
            return JsonResponse({'status': 'Failure', 'message': str(e)}, status=400)

##########DELETE ADDRESS = deletes from user_addr and shipping-addr (if there are no orders sent to that address)
########### ORDERS contains all shipping addr values in a single column called address, has user_id, user_name.
######### CHECKOUT



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


# # Add to Cart View (simplified)
# @login_required
# def add_to_cart(request, product_id):
#     product = get_object_or_404(Product, pk=product_id)

#     # Create or retrieve the user's active order (cart)
#     user = request.user
#     order, created = Order.objects.get_or_create(user=user, order_status='Cart')

#     # Check if the product is already in the cart; if so, update quantity
#     order_item, item_created = OrderItem.objects.get_or_create(order=order, product=product)
#     if not item_created:
#         order_item.quantity += 1
#         order_item.save()

#     return redirect('cart')

# # Cart View
# @login_required
# def cart(request):
#     user = request.user
#     cart = Order.objects.filter(user=user, order_status='Cart').first()
#     return render(request, 'cart.html', {'cart': cart})

# # Checkout View (simplified)
# @login_required
# def checkout(request):
#     user = request.user
#     cart = Order.objects.filter(user=user, order_status='Cart').first()

#     if cart:
#         # Calculate total price and handle payment processing here
#         total_price = sum(item.subtotal_price for item in cart.orderitem_set.all())

#         # Create a new order with the 'Pending' status
#         order = Order.objects.create(user=user, total_price=total_price, order_status='Pending')

#         # Copy items from the cart to the new order
#         for item in cart.orderitem_set.all():
#             OrderItem.objects.create(order=order, product=item.product, quantity=item.quantity, subtotal_price=item.subtotal_price)

#         # Clear the cart
#         cart.delete()

#         return redirect('order_confirmation')

#     return redirect('cart')

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

# # Shipping Address View (simplified)
# @login_required
# def manage_shipping_address(request):
#     user = request.user
#     shipping_addresses = ShippingAddress.objects.filter(user=user)
#     return render(request, 'manage_shipping_address.html', {'shipping_addresses': shipping_addresses})

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



