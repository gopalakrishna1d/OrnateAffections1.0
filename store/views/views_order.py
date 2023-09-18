# from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404
# from django.contrib.auth.decorators import login_required
# from ..models import User, Product, Cart, WishList, ShippingAddress, UserAddr, Review , Order, OrderItem, Payment
# from django.core.exceptions import ObjectDoesNotExist
# from django.contrib.auth.hashers import check_password, make_password
# from django.conf import settings
# from django.core.mail import send_mail
# from django.http import JsonResponse
# from django.utils import timezone
# from datetime import timedelta
# import random
# import uuid
# import re


# ########### ORDERS contains all shipping addr values in a single column called address, has user_id, user_name.
# ######### CHECKOUT
# ######### PAYMENT
# ######### PAYMENT confirmation
# ######### Order Confirmation
# ######### ORDER CANCEL
# ######### DELETE ORDER
# ######### REVIEW
# ######### view orders




# @login_required:
# def checkout(request):
#     user_id = request.POST.get('user_id')
#     product_id = request.POST.get('product_id')
#     cart = Cart.objects.filter(user_id=user_id, product_id=product_id).first()

#     if cart:
#         user = get_object_or_404(User, user_id=user_id)
#         quantity = cart.quantity

#         product = get_object_or_404(Product, product_id=product_id)
#         price = product.price

#         total_price = price * quantity

#         # Create the order with the user's default shipping address
#         order = Order.objects.create(
#             user=user,
#             user_name=user.user_name,
#             total_price=total_price,
#             order_status='Cart'
#         )

#         for item in cart.orderitem_set.all():
#             # Create order items for the order
#             OrderItem.objects.create(
#                 order=order,
#                 product=item.product,
#                 quantity=item.quantity,
#                 subtotal_price=item.subtotal_price
#             )

#         cart.delete()

#         return JsonResponse({'status': 'Success', 'message': 'Order success, Payment pending'}, status=200)

#     return JsonResponse({'status': 'Failure', 'message': 'Order failure, try again'}, status=400)
#     #     return redirect('order_confirmation')

#     # return redirect('cart') 


# #@login_required:
# #def select_addr(request):




# ##########################Delete  from cart after payment
# # # Order Confirmation View
# # @login_required
# # def order_confirmation(request):
# #     user = request.user
# #     orders = Order.objects.filter(user=user, order_status='Pending')
# #     return render(request, 'order_confirmation.html', {'orders': orders})

# # # Review Submission View
# # @login_required
# # def submit_review(request, product_id):
# #     if request.method == 'POST':
# #         product = get_object_or_404(Product, pk=product_id)
# #         rating = request.POST.get('rating')
# #         review_text = request.POST.get('review_text')

# #         # Create a new review for the product
# #         Review.objects.create(user=request.user, product=product, rating=rating, review_text=review_text)

# #         # Redirect back to the product detail page
# #         return redirect('product_detail', product_id=product_id)

# #     return redirect('product_list')


# # # Payment View (simplified)
# # @login_required
# # def make_payment(request):
# #     if request.method == 'POST':
# #         order_id = request.POST.get('order_id')  # Get the order to be paid
# #         order = get_object_or_404(Order, pk=order_id)
# #         payment_method = request.POST.get('payment_method')

# #         # Handle payment processing here
# #         # Create a payment record, update order status, etc.

# #         return redirect('payment_confirmation')
# #     return redirect('cart')

# # # Payment Confirmation View
# # @login_required
# # def payment_confirmation(request):
# #     return render(request, 'payment_confirmation.html')



