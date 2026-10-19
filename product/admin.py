# product/admin.py: đưa các bảng của app product lên trang quản trị /admin/
from django.contrib import admin
from .models import Category, Brand, Product


# Đăng ký bảng để quản lý trong trang /admin/
# list_display = các cột hiển thị ở danh sách
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'price', 'category', 'brand', 'status', 'author')
