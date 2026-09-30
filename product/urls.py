from django.urls import path
from . import views

urlpatterns = [
    path('shop/', views.product_list, name='product_list'),
    path('shop/them-san-pham/', views.product_create, name='product_create'),
    path('shop/<int:product_id>/', views.product_detail, name='product_detail'),
    path('account/my-product/', views.my_products, name='my_products'),
    path('account/product/<int:product_id>/sua/', views.edit_product, name='edit_product'),
    path('account/product/<int:product_id>/xoa/', views.delete_product, name='delete_product'),
]