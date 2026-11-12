# users/urls.py: nối đường dẫn với hàm trong users/views.py
from django.urls import path
from . import views

urlpatterns = [
    # đăng nhập / đăng ký / đăng xuất
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    # quên mật khẩu: nhập email -> nhận mail -> bấm link -> nhập mật khẩu mới
    path('forgot-password/', views.forgot_password_view, name='forgot_password'),
    path('reset-password/<uidb64>/<token>/', views.reset_password_view, name='reset_password'),
    # trang quản lý dành cho superuser (admin): danh sách user, sửa / xóa member, tạo superuser
    path('manage/users/', views.list_users_view, name='list_users'),
    path('manage/users/<int:user_id>/edit/', views.admin_edit_user_view, name='admin_edit_user'),
    path('manage/users/<int:user_id>/delete/', views.admin_delete_user_view, name='admin_delete_user'),
    path('manage/users/register-superuser/', views.register_superuser_view, name='register_superuser'),
    # trang cập nhật thông tin cá nhân (menu Account)
    path('account/update/', views.account_update_view, name='account_update'),
]