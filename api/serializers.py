# api/serializers.py: đổi dữ liệu trong database thành JSON (giống BlogSerializer ở Bài 22)
from django.conf import settings
from rest_framework import serializers
from cart.models import History
from product.models import Product
from users.models import User


# Đổi tên file trong media thành link đầy đủ, ví dụ http://127.0.0.1:8000/media/products/a.jpg
def media_url(request, name):
    if not name:
        return None
    return request.build_absolute_uri(settings.MEDIA_URL + name)


class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.SerializerMethodField()
    brand_name = serializers.SerializerMethodField()
    author_name = serializers.SerializerMethodField()
    final_price = serializers.SerializerMethodField()   # giá hiện hành (đang sale thì lấy giá sale)
    images = serializers.SerializerMethodField()        # danh sách link hình
    image = serializers.SerializerMethodField()         # hình đầu tiên (hình đại diện)

    class Meta:
        model = Product
        fields = ['id', 'title', 'price', 'status', 'sale', 'final_price', 'company', 'detail',
                  'created_at', 'category', 'category_name', 'brand', 'brand_name',
                  'author', 'author_name', 'image', 'images']

    def get_category_name(self, obj):
        return obj.category.name if obj.category else None

    def get_brand_name(self, obj):
        return obj.brand.name if obj.brand else None

    def get_author_name(self, obj):
        return obj.author.username

    def get_final_price(self, obj):
        return obj.sale if obj.status == 1 else obj.price

    def get_images(self, obj):
        request = self.context['request']
        return [media_url(request, name) for name in obj.get_images()]

    def get_image(self, obj):
        request = self.context['request']
        return media_url(request, obj.first_image())


class UserSerializer(serializers.ModelSerializer):
    country_name = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()
    role = serializers.SerializerMethodField()                # 'admin' hoặc 'member'
    total_products = serializers.SerializerMethodField()      # chỉ có khi admin xem danh sách user

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'phone', 'address',
                  'id_country', 'country_name', 'avatar', 'role', 'is_active', 'date_joined',
                  'total_products']

    def get_country_name(self, obj):
        return obj.id_country.name if obj.id_country else None

    def get_avatar(self, obj):
        return media_url(self.context['request'], obj.avatar.name if obj.avatar else '')

    def get_role(self, obj):
        if obj.is_superuser or obj.is_staff:
            return 'admin'
        return 'member'

    def get_total_products(self, obj):
        return getattr(obj, 'total_products', None)


class HistorySerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()

    class Meta:
        model = History
        fields = ['id', 'user', 'user_name', 'name', 'email', 'phone', 'price', 'items', 'created_at']

    def get_user_name(self, obj):
        return obj.user.username if obj.user else None
