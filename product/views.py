# product/views.py: xử lý logic cho sản phẩm (xem, thêm, sửa, xóa)
import json
from decimal import Decimal, InvalidOperation
from urllib.parse import urlencode
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Case, Count, DecimalField, F, Max, Q, When
from django.contrib.auth.decorators import login_required
from django.core.files.storage import default_storage
from .models import Product, Category, Brand

MAX_IMAGES = 3                                        # mỗi sản phẩm tối đa 3 hình
ALLOWED_EXT = ('.jpg', '.jpeg', '.png', '.gif', '.webp')   # đuôi file hình được phép


# ---------- các hàm phụ dùng chung cho add và edit ----------

# Kiểm tra danh sách file upload, trả về câu báo lỗi (hoặc '' nếu ổn)
def check_images(files):
    for f in files:
        # file phải là hình ảnh (kiểm tra cả loại file lẫn đuôi file)
        if not f.content_type.startswith('image/') or not f.name.lower().endswith(ALLOWED_EXT):
            return 'File ' + f.name + ' không phải hình ảnh (chỉ nhận jpg, png, gif, webp)'
        # dung lượng < 1MB
        if f.size >= 1024 * 1024:
            return 'File ' + f.name + ' lớn hơn 1MB'
    return ''


# Lưu file vào thư mục media/products/, trả về list tên file đã lưu
def save_images(files):
    names = []
    for f in files:
        # default_storage.save tự đổi tên nếu bị trùng, và trả về đường dẫn đã lưu
        saved_name = default_storage.save('products/' + f.name, f)
        names.append(saved_name)
    return names


# Đổi chuỗi người dùng nhập thành số tiền (2 chữ số thập phân). Sai định dạng thì trả về None
def to_money(text):
    try:
        value = Decimal((text or '').strip()).quantize(Decimal('0.01'))
        if abs(value) >= 10 ** 8:     # database chỉ chứa tối đa 8 chữ số phần nguyên
            return None
        return value
    except InvalidOperation:          # chữ, NaN, Infinity, số quá lớn...
        return None


# Kiểm tra các ô nhập (chưa gồm hình) của form thêm / sửa.
# Trả về (câu báo lỗi, dữ liệu đã làm sạch). Không lỗi thì câu báo lỗi là ''
def check_product_form(data):
    title = data.get('title', '').strip()
    company = data.get('company', '').strip()
    detail = data.get('detail', '').strip()
    status = data.get('status', '0')
    category_id = data.get('category', '')
    brand_id = data.get('brand', '')
    price = to_money(data.get('price'))
    sale = to_money(data.get('sale'))

    error = ''
    if title == '':
        error = 'Vui lòng nhập tên sản phẩm'
    elif len(title) > 255:
        error = 'Tên sản phẩm tối đa 255 ký tự'
    elif price is None or price <= 0:
        error = 'Giá phải là số lớn hơn 0'
    elif status not in ('0', '1'):
        error = 'Trạng thái không hợp lệ'
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
        'sale': sale if status == '1' else 0,    # sản phẩm New thì không có giá sale
        'company': company,
        'detail': detail,
    }
    return error, cleaned


# ---------- các view ----------

# id hợp lệ = chỉ gồm chữ số và không quá dài (tránh người dùng gõ bậy lên URL)
def is_id(text):
    return text.isdigit() and len(text) < 10


# Tạo link tới trang /shop/ có kèm điều kiện lọc: giữ các điều kiện đang lọc, chỉ đổi 1 điều kiện
# ví dụ đang lọc category=1 mà bấm brand=2 thì ra /shop/?category=1&brand=2
def build_url(filters, **change):
    data = dict(filters)
    data.update(change)
    data = {k: v for k, v in data.items() if v}   # bỏ điều kiện rỗng
    url = reverse('product_list')
    if data:
        url += '?' + urlencode(data)
    return url


# Lấy danh mục và thương hiệu kèm số sản phẩm (Count) để hiện ở thanh bên trái.
# Dùng chung cho trang /shop/ và trang chi tiết. Mỗi mục có thêm .url là link lọc
def sidebar_data(filters):
    categories = list(Category.objects.annotate(total=Count('product')))
    for c in categories:
        c.url = build_url(filters, category=c.id, page='')
    brands = list(Brand.objects.annotate(total=Count('product')))
    for b in brands:
        b.url = build_url(filters, brand=b.id, page='')
    return categories, brands


# Trang chủ: hiện 6 sản phẩm mới nhất (theo ngày tạo created_at, bằng nhau thì theo id)
def home(request):
    products = Product.objects.order_by('-created_at', '-id')[:6]
    categories, brands = sidebar_data({})
    return render(request, 'product/home.html', {
        'products': products,
        'categories': categories,
        'brands': brands,
        'category_id': '',
        'brand_id': '',
        'all_category_url': build_url({}),
        'all_brand_url': build_url({}),
    })


# Trang /shop/: xem + lọc + sắp xếp sản phẩm.
# Ví dụ: /shop/?q=ao&category=1&brand=2&price=0,300&sort=price_asc&page=2
# q = từ khóa | category, brand = id | price = "thấp nhất,cao nhất" | sort = kiểu sắp xếp | page = số trang
def product_list(request):
    # giá hiện hành: sản phẩm Sale (status=1) lấy giá sale, sản phẩm New lấy giá gốc
    products = Product.objects.annotate(
        final_price=Case(
            When(status=1, then=F('sale')),
            default=F('price'),
            output_field=DecimalField(),
        )
    )

    q = request.GET.get('q', '').strip()
    category_id = request.GET.get('category', '')
    brand_id = request.GET.get('brand', '')
    price = request.GET.get('price', '')
    sort = request.GET.get('sort', '')

    # --- lọc theo từ khóa, category, brand ---
    if q:
        products = products.filter(title__icontains=q)
    if is_id(category_id):
        products = products.filter(category_id=category_id)
    if is_id(brand_id):
        products = products.filter(brand_id=brand_id)

    # --- lọc theo khoảng giá. Đổi chuỗi "10,300" thành 2 số (sai định dạng thì bỏ qua, không báo lỗi) ---
    price_min = price_max = None
    parts = price.split(',')
    if len(parts) == 2:
        try:
            low = Decimal(parts[0])
            high = Decimal(parts[1])
            # so sánh với 10**8 để loại số quá lớn / NaN / Infinity (so sánh NaN sẽ báo InvalidOperation)
            if abs(low) < 10 ** 8 and abs(high) < 10 ** 8:
                price_min, price_max = low, high
        except InvalidOperation:
            pass
    if price_min is not None:
        products = products.filter(final_price__range=(price_min, price_max))
    else:
        price = ''

    # --- sắp xếp (mặc định: mới nhất lên đầu) ---
    sort_choices = [
        ('', 'Mới nhất', '-id'),
        ('price_asc', 'Giá tăng dần', 'final_price'),
        ('price_desc', 'Giá giảm dần', '-final_price'),
        ('name', 'Tên A-Z', 'title'),
    ]
    order_by = '-id'
    for key, label, field in sort_choices:
        if sort == key:
            order_by = field
    if sort not in [c[0] for c in sort_choices]:
        sort = ''
    products = products.order_by(order_by, '-id')

    # --- thanh trượt giá: tối đa = giá gốc cao nhất trong database (tối thiểu 100) ---
    top_price = Product.objects.aggregate(top=Max('price'))['top'] or 0
    slider_max = max(int(top_price) + 1, 100)
    slider_min_now = int(price_min) if price_min is not None else 0
    slider_max_now = int(price_max) if price_max is not None else slider_max

    # --- phân trang: 9 sản phẩm / trang ---
    page_obj = Paginator(products, 9).get_page(request.GET.get('page'))

    # --- thanh bên trái + danh sách các kiểu sắp xếp (mỗi kiểu là 1 link, giữ nguyên điều kiện lọc) ---
    filters = {'q': q, 'category': category_id, 'brand': brand_id, 'price': price, 'sort': sort}
    categories, brands = sidebar_data(filters)
    sort_options = []
    for key, label, field in sort_choices:
        sort_options.append({'label': label, 'url': build_url(filters, sort=key, page=''), 'selected': key == sort})

    return render(request, 'product/product_list.html', {
        'page_obj': page_obj,
        'total': page_obj.paginator.count,
        'categories': categories,
        'brands': brands,
        'all_category_url': build_url(filters, category='', page=''),
        'all_brand_url': build_url(filters, brand='', page=''),
        'sort_options': sort_options,
        'page_query': urlencode({k: v for k, v in filters.items() if v}),   # giữ điều kiện lọc khi bấm sang trang khác
        'has_filter': bool(q or category_id or brand_id or price),
        'q': q,
        'category_id': category_id,
        'brand_id': brand_id,
        'sort': sort,
        'slider_max': slider_max,
        'slider_min_now': slider_min_now,
        'slider_max_now': slider_max_now,
    })


# Trang thêm sản phẩm. @login_required = chưa đăng nhập thì chuyển về trang login
# GET: hiện form trống | POST: kiểm tra dữ liệu rồi lưu vào database
@login_required
def product_create(request):
    error = ''
    if request.method == 'POST':
        files = request.FILES.getlist('images')   # lấy nhiều file

        # --- kiểm tra ---
        error, data = check_product_form(request.POST)
        if error == '':
            if len(files) > MAX_IMAGES:
                error = 'Chỉ được upload tối đa ' + str(MAX_IMAGES) + ' hình'
            else:
                error = check_images(files)

        if error == '':
            names = save_images(files)
            # **data = truyền các ô đã kiểm tra (title, price, category_id, ...) vào bảng Product
            Product.objects.create(author=request.user, images=json.dumps(names), **data)
            messages.success(request, 'Đã thêm sản phẩm "' + data['title'] + '" thành công')
            return redirect('my_products')

    return render(request, 'product/product_create.html', {
        'categories': Category.objects.all(),
        'brands': Brand.objects.all(),
        'error': error,
        'form': request.POST,    # giữ lại dữ liệu đã nhập khi bị lỗi (GET thì rỗng)
    })


# Trang 'Sản phẩm của tôi': chỉ lấy sản phẩm do user đang đăng nhập đăng. Có tìm theo tên + phân trang
@login_required
def my_products(request):
    products = Product.objects.filter(author=request.user).order_by('-id')
    q = request.GET.get('q', '').strip()
    if q:
        products = products.filter(title__icontains=q)
    page_obj = Paginator(products, 10).get_page(request.GET.get('page'))   # 10 sản phẩm / trang
    return render(request, 'product/my_products.html', {
        'page_obj': page_obj,
        'q': q,
        'page_query': urlencode({'q': q}) if q else '',
    })


# Trang sửa sản phẩm: hình cũ (trừ hình bị tick xóa) + hình mới <= 3 hình
@login_required
def edit_product(request, product_id):
    # chỉ lấy sản phẩm của chính user đang đăng nhập
    product = get_object_or_404(Product, id=product_id, author=request.user)
    error = ''
    delete_images = []
    # form = dữ liệu hiện trong các ô: lúc mới mở là dữ liệu trong database, khi bị lỗi thì giữ lại cái vừa nhập
    form = {
        'title': product.title,
        'price': str(product.price),
        'category': str(product.category_id or ''),
        'brand': str(product.brand_id or ''),
        'status': str(product.status),
        'sale': str(product.sale),
        'company': product.company,
        'detail': product.detail,
    }

    if request.method == 'POST':
        form = request.POST
        files = request.FILES.getlist('images')
        old_images = product.get_images()      # hinhcu
        # chỉ nhận tên hình thật sự thuộc sản phẩm này (tránh gửi tên file lạ để xóa file khác)
        delete_images = [n for n in request.POST.getlist('delete_images') if n in old_images]
        # hinhconlai = hình cũ nhưng không nằm trong danh sách xóa
        remain_images = [n for n in old_images if n not in delete_images]

        # --- kiểm tra ---
        error, data = check_product_form(request.POST)
        if error == '':
            if len(remain_images) + len(files) > MAX_IMAGES:
                error = 'Tổng số hình không được quá ' + str(MAX_IMAGES)
            else:
                error = check_images(files)

        if error == '':
            new_names = save_images(files)
            for field, value in data.items():
                setattr(product, field, value)        # gán từng ô đã kiểm tra vào sản phẩm
            # hình còn lại + hình mới -> JSON
            product.images = json.dumps(remain_images + new_names)
            product.save()
            # lưu database xong mới xóa file thật của các hình bị tick (lỡ lưu lỗi thì không mất hình)
            for name in delete_images:
                default_storage.delete(name)
            messages.success(request, 'Đã cập nhật sản phẩm "' + product.title + '" thành công')
            return redirect('my_products')

    return render(request, 'product/edit_product.html', {
        'product': product,
        'categories': Category.objects.all(),
        'brands': Brand.objects.all(),
        'error': error,
        'form': form,
        'delete_images': delete_images,    # giữ lại các ô đã tick xóa khi bị lỗi
    })


# Xóa sản phẩm: chỉ nhận POST (nút Xóa trong form), GET thì không làm gì
@login_required
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id, author=request.user)
    if request.method == 'POST':
        title = product.title
        for name in product.get_images():      # xóa luôn file hình của sản phẩm
            default_storage.delete(name)
        product.delete()
        messages.success(request, 'Đã xóa sản phẩm "' + title + '"')
    return redirect('my_products')


# Trang chi tiết 1 sản phẩm (ai cũng xem được). Không có id thì báo lỗi 404
def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    # sản phẩm liên quan: cùng danh mục (nếu có), bỏ chính nó, lấy tối đa 6 cái mới nhất
    related = Product.objects.exclude(id=product.id)
    if product.category_id:
        related = related.filter(category_id=product.category_id)
    related = list(related.order_by('-id')[:6])
    # chia thành từng nhóm 3 sản phẩm, mỗi nhóm là 1 trang của băng chuyền (carousel)
    related_groups = [related[i:i + 3] for i in range(0, len(related), 3)]

    categories, brands = sidebar_data({})
    # chủ sản phẩm mới thấy nút Sửa / Xóa
    is_owner = request.user.is_authenticated and product.author_id == request.user.id

    return render(request, 'product/product_detail.html', {
        'product': product,
        'images': product.get_images(),
        'related_groups': related_groups,
        'categories': categories,
        'brands': brands,
        'category_id': str(product.category_id or ''),   # để tô sáng danh mục / hãng của sản phẩm này
        'brand_id': str(product.brand_id or ''),
        'all_category_url': build_url({}),
        'all_brand_url': build_url({}),
        'is_owner': is_owner,
    })
