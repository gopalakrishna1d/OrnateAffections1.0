from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404
from django.contrib.auth.decorators import login_required
from ..models import User, ShippingAddress, UserAddr, Order
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse



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
# # Shipping Address View (simplified)
# @login_required
# def manage_shipping_address(request):
#     user = request.user
#     shipping_addresses = ShippingAddress.objects.filter(user=user)
#     return render(request, 'manage_shipping_address.html', {'shipping_addresses': shipping_addresses})


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



########## Get Addresses
