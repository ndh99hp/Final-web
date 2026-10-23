# product/urls.py: nối đường dẫn (URL) với hàm xử lý trong views.py
from django.urls import path
from . import views

urlpatterns = [
    # trang chủ: 6 sản phẩm mới nhất
    path('', views.home, name='home'),
    # trang xem tất cả sản phẩm (ai cũng xem được)
    path('shop/', views.product_list, name='product_list'),
    # <int:product_id> = id của sản phẩm trong database
    path('shop/<int:product_id>/', views.product_detail, name='product_detail'),
    # các trang dưới đây của menu Account (phải đăng nhập)
    path('account/my-product/', views.my_products, name='my_products'),
    path('account/add-product/', views.product_create, name='product_create'),
    path('account/edit-product/<int:product_id>/', views.edit_product, name='edit_product'),
    path('account/delete-product/<int:product_id>/', views.delete_product, name='delete_product'),
]
