from django.contrib import admin
from django.urls import path
from orders.views import create_order, get_order

urlpatterns = [
    path('admin/', admin.site.urls),
    path('orders/', create_order),
    path('orders/<int:order_id>/', get_order),
]
