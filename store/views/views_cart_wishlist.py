from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404
from .views_user_auth import login
from ..models import User, Product, Cart, WishList # ShippingAddress, UserAddr, Review , Order#, OrderItem, Payment
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.hashers import check_password, make_password
from django.conf import settings
from django.http import JsonResponse


############## user verification must be checked for all the actions and prompt them to verify using otp in settings or something.

########### Unverified users login is different from verified login (can add to cart but need verification to checkout)

def add_to_cart(request):
    if request.method == 'POST':
        user_id = request.session.get('user_id', '')
        product_id = request.POST.get('product_id')
        quantity = request.POST.get('quantity')

        try:
            user = get_object_or_404(User, user_id=user_id)
            product = get_object_or_404(Product, product_id=product_id)

            if int(quantity) <= product.stock_quantity:
                Cart.objects.create(user=user, product=product, quantity=quantity)

                login(request, user)
                success = {'status': 'Success', 'message': 'Successfully added to cart'}
                return JsonResponse(success, status=200)
            else:
                error = {'status': 'Failure', 'message': 'Quantity exceeds available stock'}
                return JsonResponse(error, status=400)

        except User.DoesNotExist:
            error = {'status': 'Failure', 'message': 'User not found'}
            return JsonResponse(error, status=404)

        except Product.DoesNotExist:
            error = {'status': 'Failure', 'message': 'Product not found'}
            return JsonResponse(error, status=404)

        except Exception as e:
            print(e)
            error = {'status': 'Failure', 'message': 'Error adding to cart'}
            return JsonResponse(error, status=400)

    else:
        error = {'status': 'Failure', 'message': 'Only POST requests are allowed'}
        return JsonResponse(error, status=405)


def get_cart_items(request):
    if request.method == 'POST':
        user_id = request.session.get('user_id', '')
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
        user_id = request.session.get('user_id', '')
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
# # Cart View
# # def cart(request):
#     user = request.user
#     cart = Order.objects.filter(user=user, order_status='Cart').first()
#     return render(request, 'cart.html', {'cart': cart})


def get_wishlist_items(request):
    if request.method == 'POST':
        user_id = request.session.get('user_id', '')
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
        user_id = request.session.get('user_id', '')
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
        user_id = request.session.get('user_id', '')
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
        user_id = request.session.get('user_id', '')
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
        user_id = request.session.get('user_id', '')
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