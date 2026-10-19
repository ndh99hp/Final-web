# users/urls.py: nối đường dẫn với hàm trong users/views.py
from django.urls import path
from . import views

urlpatterns = [
    # đăng nhập / đăng ký / đăng xuất
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    # trang dành cho superuser (admin)
    path('users/', views.list_users_view, name='list_users'),
    path('users/register-superuser/', views.register_superuser_view, name='register_superuser'),
    # trang cập nhật thông tin cá nhân (menu Account)
    path('account/update/', views.account_update_view, name='account_update'),
]