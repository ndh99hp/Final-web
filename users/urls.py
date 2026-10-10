from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('users/', views.list_users_view, name='list_users'),
    path('users/register-superuser/', views.register_superuser_view, name='register_superuser'),
    path('account/update/', views.account_update_view, name='account_update'),
]