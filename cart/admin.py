# cart/admin.py: admin xem lịch sử mua hàng ở trang /admin/
from django.contrib import admin
from .models import History


@admin.register(History)
class HistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'phone', 'user', 'price', 'created_at')
    # tìm theo tên, email, phone, username của người mua
    search_fields = ('name', 'email', 'phone', 'user__username')
    list_filter = ('created_at',)
