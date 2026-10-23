# cart/urls.py: giỏ hàng + thanh toán
from django.urls import path
from . import views

urlpatterns = [
    path('cart/', views.cart_view, name='cart'),
    # 2 đường dẫn dưới đây chỉ nhận AJAX (POST), trả về JSON
    path('cart/add/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/', views.update_cart, name='update_cart'),
    path('checkout/', views.checkout, name='checkout'),
]
