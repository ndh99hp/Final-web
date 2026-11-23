# cart/models.py: bảng history = lịch sử mua hàng (admin xem user nào mua nhiều để gửi khuyến mãi)
# Sau khi sửa file này phải chạy: python manage.py makemigrations && python manage.py migrate
from django.db import models
from users.models import User
from product.models import Product


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


# Giỏ hàng lưu trong database: mỗi dòng = 1 sản phẩm trong giỏ của 1 user
# (giá không lưu ở đây, lúc xem giỏ sẽ lấy giá hiện tại của sản phẩm)
class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    qty = models.PositiveSmallIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # 1 user chỉ có 1 dòng cho mỗi sản phẩm (thêm lần nữa thì cộng dồn số lượng)
        unique_together = ('user', 'product')

    def __str__(self):
        return self.user.username + ' - ' + self.product.title + ' x' + str(self.qty)
