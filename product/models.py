# product/models.py: định nghĩa các bảng trong database (Category, Brand, Product)
# Sau khi sửa file này phải chạy: python manage.py makemigrations && python manage.py migrate
import json
from django.core.files.storage import default_storage
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

    # Xóa sản phẩm + xóa luôn file hình trong media/products/
    # (hình nào còn sản phẩm khác dùng chung, ví dụ hình của sản phẩm mẫu, thì giữ lại)
    def delete_with_images(self):
        for name in self.get_images():
            used_by_other = Product.objects.exclude(id=self.id).filter(images__contains='"' + name + '"').exists()
            if not used_by_other:
                default_storage.delete(name)
        self.delete()

    def __str__(self):
        return self.title
