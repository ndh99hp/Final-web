# api/urls.py: nối đường dẫn API với hàm xử lý (giống Bài 22: api/list, api/create, api/detail/<id>/ ...)
# Các đường dẫn dưới đây đều bắt đầu bằng /api/ (xem core/urls.py)
from django.urls import path
from . import views_admin, views_auth, views_blog, views_cart, views_product


# Trang gốc /api/: liệt kê nhanh các API (xem đầy đủ trong API_DOCS.md)
from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(['GET'])
def api_root(request):
    return Response({
        'message': 'E-Shopper API. Xem danh sách đầy đủ trong file API_DOCS.md',
        'auth': ['register/', 'login/', 'logout/', 'account/', 'account/update/', 'forgot-password/', 'reset-password/', 'countries/'],
        'product': ['filters/', 'home/', 'products/', 'products/search/', 'products/<id>/', 'my-products/'],
        'cart': ['cart/', 'cart/add/', 'cart/update/', 'checkout/', 'orders/'],
        'blog': ['blogs/', 'blogs/<slug>/', 'blogs/<slug>/rate/', 'blogs/<slug>/comment/'],
        'admin': ['admin/login/', 'admin/users/', 'admin/products/', 'admin/history/'],
    })


urlpatterns = [
    path('', api_root),

    # ----- tài khoản -----
    path('countries/', views_auth.countries),
    path('register/', views_auth.register),
    path('login/', views_auth.login),
    path('logout/', views_auth.logout),
    path('account/', views_auth.account_detail),
    path('account/update/', views_auth.account_update),
    path('forgot-password/', views_auth.forgot_password),
    path('reset-password/', views_auth.reset_password),

    # ----- sản phẩm (ai cũng xem được) -----
    path('filters/', views_product.filters),
    path('home/', views_product.home),
    path('products/', views_product.product_list),
    path('products/search/', views_product.product_search),
    path('products/<int:id>/', views_product.product_detail),

    # ----- sản phẩm của tôi (member) -----
    path('my-products/', views_product.my_products),
    path('my-products/create/', views_product.my_product_create),
    path('my-products/update/<int:id>/', views_product.my_product_update),
    path('my-products/delete/<int:id>/', views_product.my_product_delete),

    # ----- giỏ hàng, thanh toán, lịch sử (member) -----
    path('cart/', views_cart.cart_list),
    path('cart/add/', views_cart.cart_add),
    path('cart/update/', views_cart.cart_update),
    path('checkout/', views_cart.checkout),
    path('orders/', views_cart.my_orders),

    # ----- blog -----
    path('blogs/', views_blog.blog_list),
    path('blogs/<slug:slug>/', views_blog.blog_detail),
    path('blogs/<slug:slug>/rate/', views_blog.blog_rate),
    path('blogs/<slug:slug>/comment/', views_blog.blog_comment),

    # ----- admin (cần token của superuser) -----
    path('admin/login/', views_admin.admin_login),
    path('admin/users/', views_admin.admin_users),
    path('admin/users/update/<int:id>/', views_admin.admin_user_update),
    path('admin/users/delete/<int:id>/', views_admin.admin_user_delete),
    path('admin/users/register-superuser/', views_admin.admin_register_superuser),
    path('admin/products/', views_admin.admin_products),
    path('admin/products/update/<int:id>/', views_admin.admin_product_update),
    path('admin/products/delete/<int:id>/', views_admin.admin_product_delete),
    path('admin/history/', views_admin.admin_history),
]
