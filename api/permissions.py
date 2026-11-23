# api/permissions.py: phân quyền cho API (dùng với @permission_classes như Bài 23)
# Admin và member dùng chung 1 bảng user:
#   - admin  = is_superuser hoặc is_staff
#   - member = cả 2 đều False
from rest_framework.permissions import BasePermission


# Chỉ member (đã đăng nhập, không phải admin) mới được gọi
class IsMember(BasePermission):
    message = 'API này chỉ dành cho thành viên (tài khoản admin không dùng được).'

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and not (user.is_superuser or user.is_staff))


# Chỉ superuser (admin) mới được gọi
class IsSuperAdmin(BasePermission):
    message = 'API này chỉ dành cho admin.'

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and user.is_superuser)
