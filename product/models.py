import json
from django.db import models
from users.models import User  # bảng user


# Bảng danh mục (giống bảng Country bên users)
class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


# Bảng thương hiệu
class Brand(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Product(models.Model):
    # id_user: người đăng sản phẩm
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    # name
    title = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    # id_category, id_brand (cho phép trống để không lỗi khi đã có dữ liệu cũ)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True)
    # status: 0 = new, 1 = sale
    status = models.PositiveSmallIntegerField(default=0)
    # sale: giá sale (chỉ dùng khi status = 1)
    sale = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    company = models.CharField(max_length=255, blank=True, default='')
    # hình ảnh: lưu chuỗi JSON, ví dụ '["products/a.jpg", "products/b.jpg"]'
    images = models.TextField(default='[]')
    detail = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    # đổi chuỗi JSON thành list (mảng) để dùng
    def get_images(self):
        return json.loads(self.images)

    # lấy hình đầu tiên làm hình đại diện, không có hình thì trả về chuỗi rỗng
    def first_image(self):
        list_images = self.get_images()
        if len(list_images) > 0:
            return list_images[0]
        return ''

    def __str__(self):
        return self.title
