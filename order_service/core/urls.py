from django.contrib import admin
from django.urls import path
from orders.views import create_order, get_order, add_to_cart, get_cart, checkout, health_check

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/health', health_check),
    path('api/v1/orders/create/', create_order),
    path('api/v1/orders/<int:order_id>/', get_order),
    path('api/v1/orders/cart/add/', add_to_cart),
    path('api/v1/orders/cart/<int:user_id>/', get_cart),
    path('api/v1/orders/checkout/', checkout),
]
