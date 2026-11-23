# api/helpers.py: các hàm phụ dùng chung cho các API (kiểm tra dữ liệu, lọc sản phẩm, phân trang...)
import json
from decimal import Decimal, InvalidOperation
from django.core.files.storage import default_storage
from django.core.paginator import Paginator
from django.db.models import Case, DecimalField, F, When
from product.models import Product, Category, Brand

MAX_IMAGES = 3                                              # mỗi sản phẩm tối đa 3 hình
ALLOWED_EXT = ('.jpg', '.jpeg', '.png', '.gif', '.webp')    # đuôi file hình được phép
MAX_QTY = 99                                                # mỗi sản phẩm mua tối đa 99 cái

# Các khoảng giá của tìm kiếm nâng cao. value có dạng "thấp-cao"
PRICE_RANGES = [
    ('0-10', 'Dưới $10'),
    ('10-50', '$10 - $50'),
    ('50-100', '$50 - $100'),
    ('100-500', '$100 - $500'),
    ('500-1000', '$500 - $1000'),
    ('1000-99999999', 'Trên $1000'),
]

# Các kiểu sắp xếp của trang shop: (giá trị gửi lên, tên hiển thị, cột sắp xếp)
SORT_CHOICES = [
    ('', 'Mới nhất', '-id'),
    ('price_asc', 'Giá tăng dần', 'final_price'),
    ('price_desc', 'Giá giảm dần', '-final_price'),
    ('name', 'Tên A-Z', 'title'),
]


# ---------- đọc dữ liệu gửi lên ----------

# id hợp lệ = chỉ gồm chữ số và không quá dài (tránh gửi bậy lên)
def is_id(value):
    text = str(value)
    return text.isascii() and text.isdigit() and len(text) < 10


# Lấy 1 ô dạng chữ, bỏ khoảng trắng 2 đầu (không có thì trả về chuỗi rỗng)
def get_text(data, key):
    value = data.get(key)
    if value is None:
        return ''
    return str(value).strip()


# Lấy 1 ô dạng danh sách (ví dụ delete_images). Form gửi nhiều giá trị thì dùng getlist, JSON thì là list
def get_list(data, key):
    if hasattr(data, 'getlist'):
        return data.getlist(key)
    value = data.get(key, [])
    if isinstance(value, list):
        return value
    return [value]


# Phân trang: trả về {count, page, total_pages, results}
# make_list là hàm đổi danh sách bản ghi của trang này thành list dữ liệu JSON
def paginate(queryset, request, per_page, make_list):
    page_obj = Paginator(queryset, per_page).get_page(request.GET.get('page'))
    return {
        'count': page_obj.paginator.count,
        'page': page_obj.number,
        'total_pages': page_obj.paginator.num_pages,
        'results': make_list(page_obj.object_list),
    }


# ---------- sản phẩm ----------

# Lấy tất cả sản phẩm kèm cột final_price = giá hiện hành:
# sản phẩm Sale (status=1) lấy giá sale, sản phẩm New lấy giá gốc
def products_with_final_price():
    return Product.objects.annotate(
        final_price=Case(
            When(status=1, then=F('sale')),
            default=F('price'),
            output_field=DecimalField(),
        )
    )


# Giá hiện hành của 1 sản phẩm
def final_price_of(product):
    if product.status == 1:
        return product.sale
    return product.price


# Lọc cho trang shop: q, category, brand, price="thấp,cao", sort
def filter_shop(params):
    products = products_with_final_price()
    q = get_text(params, 'q')
    category_id = get_text(params, 'category')
    brand_id = get_text(params, 'brand')
    price = get_text(params, 'price')
    sort = get_text(params, 'sort')

    if q:
        products = products.filter(title__icontains=q)
    if is_id(category_id):
        products = products.filter(category_id=category_id)
    if is_id(brand_id):
        products = products.filter(brand_id=brand_id)

    # khoảng giá: "10,300" -> 2 số (sai định dạng thì bỏ qua, không báo lỗi)
    parts = price.split(',')
    if len(parts) == 2:
        try:
            low = Decimal(parts[0])
            high = Decimal(parts[1])
            if abs(low) < 10 ** 8 and abs(high) < 10 ** 8:    # loại số quá lớn / NaN / Infinity
                products = products.filter(final_price__range=(low, high))
        except InvalidOperation:
            pass

    order_by = '-id'
    for key, label, field in SORT_CHOICES:
        if sort == key:
            order_by = field
    return products.order_by(order_by, '-id')


# Lọc cho tìm kiếm nâng cao: name, price ("0-10"...), category, brand, status. Không chọn gì thì ra tất cả
def filter_search_advanced(params):
    products = products_with_final_price()
    name = get_text(params, 'name')
    price = get_text(params, 'price')
    category_id = get_text(params, 'category')
    brand_id = get_text(params, 'brand')
    status = get_text(params, 'status')

    if name:
        products = products.filter(title__icontains=name)
    if price in dict(PRICE_RANGES):
        low, high = price.split('-')
        products = products.filter(final_price__range=(Decimal(low), Decimal(high)))
    if is_id(category_id):
        products = products.filter(category_id=category_id)
    if is_id(brand_id):
        products = products.filter(brand_id=brand_id)
    if status in ('0', '1'):                 # 0 = New, 1 = Sale
        products = products.filter(status=status)
    return products.order_by('-id')


# Đổi chuỗi người nhập thành số tiền (2 chữ số thập phân). Sai định dạng thì trả về None
def to_money(text):
    try:
        value = Decimal((text or '').strip()).quantize(Decimal('0.01'))
        if abs(value) >= 10 ** 8:      # database chỉ chứa tối đa 8 chữ số phần nguyên
            return None
        return value
    except InvalidOperation:           # chữ, NaN, Infinity, số quá lớn...
        return None


# Kiểm tra các ô nhập (chưa gồm hình) khi thêm / sửa sản phẩm.
# Trả về (câu báo lỗi, dữ liệu đã làm sạch). Không lỗi thì câu báo lỗi là ''
def check_product_form(data):
    title = get_text(data, 'title')
    company = get_text(data, 'company')
    detail = get_text(data, 'detail')
    status = get_text(data, 'status') or '0'
    category_id = get_text(data, 'category')
    brand_id = get_text(data, 'brand')
    price = to_money(get_text(data, 'price'))
    sale = to_money(get_text(data, 'sale'))

    error = ''
    if title == '':
        error = 'Vui lòng nhập tên sản phẩm'
    elif len(title) > 255:
        error = 'Tên sản phẩm tối đa 255 ký tự'
    elif price is None or price <= 0:
        error = 'Giá phải là số lớn hơn 0'
    elif status not in ('0', '1'):
        error = 'Trạng thái không hợp lệ (0 = New, 1 = Sale)'
    elif status == '1' and (sale is None or sale <= 0):
        error = 'Bạn chọn Sale thì phải nhập giá sale lớn hơn 0'
    elif status == '1' and sale >= price:
        error = 'Giá sale phải nhỏ hơn giá gốc'
    elif len(company) > 255:
        error = 'Tên công ty tối đa 255 ký tự'
    elif category_id and not (is_id(category_id) and Category.objects.filter(id=category_id).exists()):
        error = 'Danh mục không hợp lệ'
    elif brand_id and not (is_id(brand_id) and Brand.objects.filter(id=brand_id).exists()):
        error = 'Thương hiệu không hợp lệ'

    cleaned = {
        'title': title,
        'price': price,
        'category_id': category_id or None,
        'brand_id': brand_id or None,
        'status': int(status) if status in ('0', '1') else 0,
        'sale': sale if status == '1' else 0,      # sản phẩm New thì không có giá sale
        'company': company,
        'detail': detail,
    }
    return error, cleaned


# Kiểm tra danh sách file hình upload. Trả về câu báo lỗi (hoặc '' nếu ổn)
def check_images(files):
    for f in files:
        if not f.content_type.startswith('image/') or not f.name.lower().endswith(ALLOWED_EXT):
            return 'File ' + f.name + ' không phải hình ảnh (chỉ nhận jpg, png, gif, webp)'
        if f.size >= 1024 * 1024:                  # dung lượng < 1MB
            return 'File ' + f.name + ' lớn hơn 1MB'
    return ''


# Lưu file vào thư mục media/products/, trả về list tên file đã lưu
def save_images(files):
    names = []
    for f in files:
        # default_storage.save tự đổi tên nếu bị trùng
        names.append(default_storage.save('products/' + f.name, f))
    return names


# Thêm sản phẩm mới. Trả về (câu báo lỗi, sản phẩm). Lỗi thì sản phẩm là None
def create_product(user, data, files):
    error, cleaned = check_product_form(data)
    if error == '':
        if len(files) > MAX_IMAGES:
            error = 'Chỉ được upload tối đa ' + str(MAX_IMAGES) + ' hình'
        else:
            error = check_images(files)
    if error != '':
        return error, None

    names = save_images(files)
    product = Product.objects.create(author=user, images=json.dumps(names), **cleaned)
    return '', product


# Sửa sản phẩm (dùng chung cho member và admin). Hình cũ (trừ hình trong delete_images) + hình mới <= 3
# Trả về (câu báo lỗi, sản phẩm)
def update_product(product, data, files):
    old_images = product.get_images()
    # chỉ nhận tên hình thật sự thuộc sản phẩm này (tránh gửi tên file lạ để xóa file khác)
    delete_images = [n for n in get_list(data, 'delete_images') if n in old_images]
    remain_images = [n for n in old_images if n not in delete_images]

    error, cleaned = check_product_form(data)
    if error == '':
        if len(remain_images) + len(files) > MAX_IMAGES:
            error = 'Tổng số hình không được quá ' + str(MAX_IMAGES)
        else:
            error = check_images(files)
    if error != '':
        return error, None

    new_names = save_images(files)
    for field, value in cleaned.items():
        setattr(product, field, value)
    product.images = json.dumps(remain_images + new_names)
    product.save()
    # lưu database xong mới xóa file thật (lỡ lưu lỗi thì không mất hình)
    for name in delete_images:
        default_storage.delete(name)
    return '', product
