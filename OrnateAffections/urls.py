from django.contrib import admin
from django.urls import path
import store.views.views_admin as admin_views
import store.views.views_order as order_views
import store.views.views_prod as prod_views
import store.views.views_cart_wishlist as cart_wishlist_views
import store.views.views_user_auth as user_auth_views
import store.views.views_address as addr_views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    path('', user_auth_views.signup, name= 'signup'),
    path('signup/', user_auth_views.signup, name= 'signup'),
    path('generate_ornate_af_otp/verify/', user_auth_views.generate_otp, {'purpose': 'verify'}, name='generate_otp_verify'),
    path('generate_ornate_af_otp/reset/', user_auth_views.generate_otp, {'purpose': 'reset'}, name='generate_otp_reset'),
    path('forgoten_password/', user_auth_views.forgoten_password, name='forgoten_password'),
    path('verify_ornate_af_otp/', user_auth_views.verify_otp, name='verify_otp'),
    path('reset_password/logged_in/', user_auth_views.reset_password, {'purpose': 'logged_in'}, name='reset_password_logged_in'),
    path('reset_password/forgot_password/', user_auth_views.reset_password, {'purpose': 'forgot_password'}, name= 'reset_password_forgot_password'),
    path('login/', user_auth_views.login, name='login'),
    path('logout/', user_auth_views.logout, name='logout'),
    path('delete_ornate_af_user/', user_auth_views.delete_user, name='delete_user'),

    path('add_product/', prod_views.add_product, name='add_product'),

    path('add_to_cart/', cart_wishlist_views.add_to_cart, name='add_to_cart'),
    path('add_to_wishlist/', cart_wishlist_views.add_to_wishlist, name='add_to_wishlist'),
    path('get_cart_items/', cart_wishlist_views.get_cart_items, name='get_cart_items'),
    path('get_wishlist_items/', cart_wishlist_views.get_wishlist_items, name='get_wishlist_items'),
    path('move_to_cart/', cart_wishlist_views.move_to_cart, name='move_to_cart'),
    path('save_for_later/', cart_wishlist_views.save_for_later, name='save_for_later'),
    path('delete_from_cart/', cart_wishlist_views.delete_from_cart, name='delete_from_cart'),
    path('remove_from_wishlist/', cart_wishlist_views.remove_from_wishlist, name='remove_from_wishlist'),
    
    path('shipping_addr/', addr_views.shipping_addr, name='shipping_addr'),
    path('get_addr/', addr_views.get_addr, name='get_addr'),
    path('delete_addr/', addr_views.delete_addr, name='delete_addr'),
]
