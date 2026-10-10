import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.files.storage import default_storage
from .models import Product, Category, Brand


# ---------- 2 hàm phụ dùng chung cho add và edit ----------

# Kiểm tra danh sách file upload, trả về câu báo lỗi (hoặc '' nếu ổn)
def check_images(files):
    for f in files:
        # file phải là hình ảnh
        if not f.content_type.startswith('image/'):
            return 'File ' + f.name + ' không phải hình ảnh'
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


# ---------- các view ----------

def product_list(request):
    products = Product.objects.all().order_by('-id')
    return render(request, 'product/product_list.html', {'products': products})


@login_required
def product_create(request):
    categories = Category.objects.all()
    brands = Brand.objects.all()
    error = ''
    if request.method == 'POST':
        title = request.POST.get('title')
        price = request.POST.get('price')
        category_id = request.POST.get('category')
        brand_id = request.POST.get('brand')
        status = request.POST.get('status')
        sale = request.POST.get('sale')
        company = request.POST.get('company')
        detail = request.POST.get('detail')
        files = request.FILES.getlist('images')   # lấy nhiều file

        # --- kiểm tra ---
        if len(files) > 3:
            error = 'Chỉ được upload tối đa 3 hình'
        else:
            error = check_images(files)
        if error == '' and status == '1' and not sale:
            error = 'Bạn chọn Sale thì phải nhập giá sale'

        if error == '':
            names = save_images(files)
            if status != '1':
                sale = 0
            Product.objects.create(
                author=request.user,
                title=title,
                price=price,
                category_id=category_id or None,
                brand_id=brand_id or None,
                status=status,
                sale=sale,
                company=company,
                images=json.dumps(names),   # list -> chuỗi JSON
                detail=detail,
            )
            return redirect('my_products')

    return render(request, 'product/product_create.html', {
        'categories': categories,
        'brands': brands,
        'error': error,
        'old': request.POST,    # giữ lại dữ liệu đã nhập khi bị lỗi
    })


@login_required
def my_products(request):
    products = Product.objects.filter(author=request.user).order_by('-id')
    return render(request, 'product/my_products.html', {'products': products})


@login_required
def edit_product(request, product_id):
    # chỉ lấy sản phẩm của chính user đang đăng nhập
    product = get_object_or_404(Product, id=product_id, author=request.user)
    categories = Category.objects.all()
    brands = Brand.objects.all()
    error = ''
    if request.method == 'POST':
        title = request.POST.get('title')
        price = request.POST.get('price')
        category_id = request.POST.get('category')
        brand_id = request.POST.get('brand')
        status = request.POST.get('status')
        sale = request.POST.get('sale')
        company = request.POST.get('company')
        detail = request.POST.get('detail')
        files = request.FILES.getlist('images')
        delete_images = request.POST.getlist('delete_images')  # các hình được tick xóa

        old_images = product.get_images()      # hinhcu
        # hinhconlai = hình cũ nhưng không nằm trong danh sách xóa
        remain_images = []
        for name in old_images:
            if name not in delete_images:
                remain_images.append(name)

        # --- kiểm tra ---
        if len(remain_images) + len(files) > 3:
            error = 'Tổng số hình không được quá 3'
        else:
            error = check_images(files)
        if error == '' and status == '1' and not sale:
            error = 'Bạn chọn Sale thì phải nhập giá sale'

        if error == '':
            new_names = save_images(files)
            # xóa file thật của các hình bị tick
            for name in old_images:
                if name in delete_images:
                    default_storage.delete(name)
            product.title = title
            product.price = price
            product.category_id = category_id or None
            product.brand_id = brand_id or None
            product.status = status
            product.sale = sale if status == '1' else 0
            product.company = company
            product.detail = detail
            # hình còn lại + hình mới -> JSON
            product.images = json.dumps(remain_images + new_names)
            product.save()
            return redirect('my_products')

    return render(request, 'product/edit_product.html', {
        'product': product,
        'categories': categories,
        'brands': brands,
        'error': error,
    })


@login_required
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id, author=request.user)
    if request.method == 'POST':
        product.delete()
    return redirect('my_products')


def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'product/product_detail.html', {'product': product})
