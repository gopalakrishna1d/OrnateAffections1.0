from django.contrib import admin
from django.urls import path
import store.views as views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    path('signup/', views.signup, name= 'signup'),
    path('regenerate_ornate_af_otp/', views.regenerate_otp, name= 'regenerate_otp'),
    path('verify_ornate_af_otp/', views.verify_otp, name='verify_otp'),
    path('reset_password/', views.reset_password, name= 'reset_password'),
    path('login/', views.login, name='login'),
    path('delete_ornate_af_user/', views.delete_user, name='delete_user'),

    path('add_product/', views.add_product, name='add_product'),

    path('add_to_cart/', views.add_to_cart, name='add_to_cart'),
    path('add_to_wishlist/', views.add_to_wishlist, name='add_to_wishlist'),
    path('get_cart_items/', views.get_cart_items, name='get_cart_items'),
    path('get_wishlist_items/', views.get_wishlist_items, name='get_wishlist_items'),
    path('move_to_cart/', views.move_to_cart, name='move_to_cart'),
    path('save_for_later/', views.save_for_later, name='save_for_later'),
    path('delete_from_cart/', views.delete_from_cart, name='delete_from_cart'),
    path('remove_from_wishlist/', views.remove_from_wishlist, name='remove_from_wishlist'),
    
    path('shipping_addr/', views.shipping_addr, name='shipping_addr'),
    path('delete_addr/', views.delete_addr, name='delete_addr'),
]
