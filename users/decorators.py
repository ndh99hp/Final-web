# users/decorators.py: các hàm phân quyền dùng chung (users, product...)
# Admin và member dùng chung 1 bảng user:
#   - admin  = is_superuser hoặc is_staff = True  -> chỉ dùng trang quản trị /admin/
#   - member = cả 2 đều False (lúc đăng ký đã gán) -> chỉ dùng frontend (account, sản phẩm của tôi...)
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.views import redirect_to_login
from django.shortcuts import redirect


# True nếu là tài khoản quản trị (admin)
def is_admin_account(user):
    return user.is_authenticated and (user.is_superuser or user.is_staff)


# Decorator cho các trang của member (giống @login_required nhưng chặn thêm tài khoản admin):
#   - chưa đăng nhập: chuyển về trang login (kèm ?next= để đăng nhập xong quay lại)
#   - là admin: báo lỗi và về trang chủ
def member_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path(), 'login')
        if is_admin_account(request.user):
            messages.error(request, 'Trang này chỉ dành cho thành viên. Tài khoản quản trị vui lòng dùng trang /admin/.')
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return wrapper


# Decorator cho các trang quản lý (/manage/...): chỉ superuser vào được, người khác bị chuyển về trang login
def superuser_required(view_func):
    def check(user):
        return user.is_authenticated and user.is_superuser
    decorated = user_passes_test(check, login_url='login')
    return decorated(view_func)
