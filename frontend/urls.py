from django.urls import path
from . import views
urlpatterns = [
    path('', views.home, name='home'),
    path('shop/', views.shop, name='shop'),
    path('product-details/', views.product_details, name='product_details'),
    path('checkout/', views.checkout, name='checkout'),
    path('cart/', views.show_cart, name='show_cart'),
    path('account/', views.account, name='account'),
    path('logout/', views.logout, name='logout'),
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('404/', views.page404, name='page404'),
    path('contact/', views.contact, name='contact'),
]