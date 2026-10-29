# product/management/commands/seed_products.py: lệnh tạo sản phẩm mẫu để test (tìm kiếm, phân trang, giỏ hàng...)
# Cách chạy (trong thư mục có manage.py, đã bật venv):
#     python manage.py seed_products          -> thêm sản phẩm mẫu (chạy lại nhiều lần cũng không bị trùng)
#     python manage.py seed_products --xoa    -> xóa hết sản phẩm mẫu đã thêm (sản phẩm của bạn không bị đụng tới)
# Hình ảnh lấy từ giao diện E-Shopper có sẵn trong static/images, chép sang media/products/
import json
from decimal import Decimal
from django.conf import settings
from django.core.files import File
from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand
from product.models import Product, Category, Brand
from users.models import User

# đánh dấu sản phẩm mẫu bằng cột company, để lệnh --xoa chỉ xóa đúng những sản phẩm này
DEMO_MARK = 'Dữ liệu mẫu'

# hình có sẵn trong theme (static/images/...)
DEMO_IMAGES = [
    'home/product1.jpg', 'home/product2.jpg', 'home/product3.jpg', 'home/product4.jpg',
    'home/product5.jpg', 'home/product6.jpg', 'shop/product7.jpg', 'shop/product8.jpg',
    'shop/product9.jpg', 'shop/product10.jpg', 'shop/product11.jpg', 'shop/product12.jpg',
    'home/recommend1.jpg', 'home/recommend2.jpg', 'home/recommend3.jpg',
]

# (tên, giá gốc, danh mục, hãng, giá sale) - giá sale = 0 nghĩa là sản phẩm New, > 0 là sản phẩm Sale
# giá trải đủ các khoảng: dưới $10, 10-50, 50-100, 100-500, 500-1000, trên $1000
DEMO_PRODUCTS = [
    ('Áo thun basic trắng', 5, 'Áo thun', 'Uniqlo', 0),
    ('Áo thun oversize đen', 8, 'Áo thun', 'Zara', 6),
    ('Áo thun thể thao Dri-FIT', 25, 'Áo thun', 'Nike', 0),
    ('Áo polo kẻ sọc', 35, 'Áo thun', 'Adidas', 28),
    ('Áo sơ mi trắng công sở', 45, 'Áo sơ mi', 'Zara', 0),
    ('Áo sơ mi flannel caro', 55, 'Áo sơ mi', 'Uniqlo', 39),
    ('Áo sơ mi lụa cao cấp', 720, 'Áo sơ mi', 'Gucci', 0),
    ('Quần jean slim fit', 60, 'Quần jean', "Levi's", 0),
    ('Quần jean rách gối', 75, 'Quần jean', 'Zara', 49),
    ('Quần jean ống rộng', 90, 'Quần jean', "Levi's", 0),
    ('Quần short thể thao', 15, 'Quần short', 'Nike', 0),
    ('Quần short kaki', 30, 'Quần short', 'Uniqlo', 0),
    ('Quần short chạy bộ', 22, 'Quần short', 'Puma', 12),
    ('Váy đầm hoa nhí', 48, 'Váy đầm', 'Zara', 0),
    ('Đầm dạ hội', 650, 'Váy đầm', 'Gucci', 480),
    ('Chân váy jean', 38, 'Váy đầm', "Levi's", 0),
    ('Giày Air Max', 150, 'Giày thể thao', 'Nike', 0),
    ('Giày Ultraboost', 180, 'Giày thể thao', 'Adidas', 140),
    ('Giày Suede Classic', 85, 'Giày thể thao', 'Puma', 0),
    ('Giày chạy bộ Pegasus', 120, 'Giày thể thao', 'Nike', 0),
    ('Túi xách da Marmont', 1500, 'Túi xách', 'Gucci', 0),
    ('Túi tote vải', 18, 'Túi xách', 'Uniqlo', 0),
    ('Balo thể thao', 40, 'Túi xách', 'Adidas', 32),
    ('Mũ lưỡi trai', 12, 'Phụ kiện', 'Nike', 0),
    ('Thắt lưng da', 450, 'Phụ kiện', 'Gucci', 0),
    ('Tất cổ cao (3 đôi)', 6, 'Phụ kiện', 'Puma', 0),
    ('Kính mát thời trang', 1200, 'Phụ kiện', 'Gucci', 950),
]


class Command(BaseCommand):
    help = 'Thêm sản phẩm mẫu để test (dùng --xoa để xóa các sản phẩm mẫu)'

    def add_arguments(self, parser):
        parser.add_argument('--xoa', action='store_true', help='Xóa các sản phẩm mẫu đã thêm')

    def handle(self, *args, **options):
        if options['xoa']:
            demo = Product.objects.filter(company=DEMO_MARK)
            total = demo.count()
            demo.delete()
            self.stdout.write(self.style.SUCCESS('Đã xóa %d sản phẩm mẫu' % total))
            return

        # người đăng: ưu tiên tài khoản admin (superuser), không có thì lấy user đầu tiên
        author = User.objects.filter(is_superuser=True).order_by('id').first() or User.objects.order_by('id').first()
        if author is None:
            self.stdout.write(self.style.ERROR('Chưa có user nào. Hãy đăng ký 1 tài khoản (hoặc createsuperuser) rồi chạy lại.'))
            return

        images = self.copy_images()
        added = 0
        for i, (title, price, cat_name, brand_name, sale) in enumerate(DEMO_PRODUCTS):
            # đã có sản phẩm mẫu tên này thì bỏ qua (chạy lại lệnh không bị trùng)
            if Product.objects.filter(title=title, company=DEMO_MARK).exists():
                continue
            # mỗi sản phẩm 2 hình (nếu có), lấy xoay vòng trong danh sách hình
            pics = []
            if images:
                pics = [images[i % len(images)], images[(i + 1) % len(images)]]
                pics = list(dict.fromkeys(pics))   # bỏ hình trùng (khi chỉ có 1 hình)
            Product.objects.create(
                author=author,
                title=title,
                price=Decimal(price),
                category=self.get_category(cat_name),
                brand=self.get_brand(brand_name),
                status=1 if sale > 0 else 0,
                sale=Decimal(sale),
                company=DEMO_MARK,
                images=json.dumps(pics),
                detail='<p>%s - sản phẩm mẫu dùng để test chức năng tìm kiếm, lọc giá và giỏ hàng.</p>' % title,
            )
            added += 1

        self.stdout.write(self.style.SUCCESS(
            'Đã thêm %d sản phẩm mẫu (người đăng: %s). Tổng số sản phẩm hiện có: %d'
            % (added, author.username, Product.objects.count())
        ))

    # tìm danh mục theo tên (không phân biệt hoa thường), chưa có thì tạo mới
    def get_category(self, name):
        category = Category.objects.filter(name__iexact=name).first()
        if category is None:
            category = Category.objects.create(name=name)
        return category

    # tìm hãng theo tên, chưa có thì tạo mới
    def get_brand(self, name):
        brand = Brand.objects.filter(name__iexact=name).first()
        if brand is None:
            brand = Brand.objects.create(name=name)
        return brand

    # chép hình từ static/images sang media/products/demo_... (đã chép rồi thì thôi), trả về list đường dẫn
    def copy_images(self):
        result = []
        for path in DEMO_IMAGES:
            source = settings.BASE_DIR / 'static' / 'images' / path
            if not source.exists():
                continue
            name = 'products/demo_' + path.replace('/', '_')
            if not default_storage.exists(name):
                with open(source, 'rb') as f:
                    default_storage.save(name, File(f))
            result.append(name)
        return result
