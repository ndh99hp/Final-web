# cart/models.py: bảng history = lịch sử mua hàng (admin xem user nào mua nhiều để gửi khuyến mãi)
# Sau khi sửa file này phải chạy: python manage.py makemigrations && python manage.py migrate
from django.db import models
from users.models import User


class History(models.Model):
    # id_user: người mua (nếu user bị xóa thì giữ lại lịch sử, chỉ để trống id_user)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    # price: tổng tiền của đơn hàng
    price = models.DecimalField(max_digits=12, decimal_places=2)
    # items: nội dung đơn hàng (mỗi dòng 1 sản phẩm) để admin xem lại
    items = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name + ' - $' + str(self.price)
