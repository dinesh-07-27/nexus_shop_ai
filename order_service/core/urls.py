from django.contrib import admin
from django.urls import path
from orders.views import create_order, get_order, add_to_cart, get_cart, checkout

urlpatterns = [
    path('admin/', admin.site.urls),
    path('orders/', create_order),
    path('orders/<int:order_id>/', get_order),
    path('cart/add/', add_to_cart),
    path('cart/<int:user_id>/', get_cart),
    path('checkout/', checkout),
]
