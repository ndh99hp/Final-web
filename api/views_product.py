# api/views_product.py: sản phẩm (ai cũng xem được) + sản phẩm của tôi (member, cần token)
from django.db.models import Count, Max
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from product.models import Product, Category, Brand
from .helpers import (PRICE_RANGES, SORT_CHOICES, create_product, filter_search_advanced, filter_shop,
                      get_text, paginate, update_product)
from .permissions import IsMember
from .serializers import ProductSerializer


# Đổi 1 danh sách sản phẩm thành list JSON
def products_json(request, products):
    return ProductSerializer(products, many=True, context={'request': request}).data


# Dữ liệu để vẽ bộ lọc ở thanh bên trái: danh mục + hãng (kèm số sản phẩm), khoảng giá, kiểu sắp xếp, giá tối đa cho thanh kéo
@api_view(['GET'])
def filters(request):
    categories = Category.objects.annotate(total=Count('product')).order_by('name')
    brands = Brand.objects.annotate(total=Count('product')).order_by('name')
    top_price = Product.objects.aggregate(top=Max('price'))['top'] or 0
    return Response({
        'categories': [{'id': c.id, 'name': c.name, 'total': c.total} for c in categories],
        'brands': [{'id': b.id, 'name': b.name, 'total': b.total} for b in brands],
        'price_ranges': [{'value': v, 'label': label} for v, label in PRICE_RANGES],
        'sort_options': [{'value': v, 'label': label} for v, label, field in SORT_CHOICES],
        'slider_max': max(int(top_price) + 1, 100),
    })


# Trang chủ: 6 sản phẩm mới nhất (theo ngày tạo, bằng nhau thì theo id)
@api_view(['GET'])
def home(request):
    products = Product.objects.select_related('category', 'brand', 'author').order_by('-created_at', '-id')[:6]
    return Response({'results': products_json(request, products)})


# Trang shop: xem + lọc + sắp xếp, 9 sản phẩm / trang
# Ví dụ: api/products/?q=ao&category=1&brand=2&price=0,300&sort=price_asc&page=2
# (thanh kéo giá chỉ cần gửi price=thấp,cao)
@api_view(['GET'])
def product_list(request):
    products = filter_shop(request.GET).select_related('category', 'brand', 'author')
    return Response(paginate(products, request, 9, lambda items: products_json(request, items)))


# Tìm kiếm nâng cao: name, price ("0-10", "10-50"...), category, brand, status (0 = New, 1 = Sale)
@api_view(['GET'])
def product_search(request):
    products = filter_search_advanced(request.GET).select_related('category', 'brand', 'author')
    return Response(paginate(products, request, 9, lambda items: products_json(request, items)))


# Chi tiết 1 sản phẩm + tối đa 6 sản phẩm liên quan (cùng danh mục, bỏ chính nó)
@api_view(['GET'])
def product_detail(request, id):
    product = Product.objects.select_related('category', 'brand', 'author').filter(id=id).first()
    if product is None:
        return Response({'error': 'Product not found'}, status=404)

    related = Product.objects.exclude(id=product.id)
    if product.category_id:
        related = related.filter(category_id=product.category_id)
    related = related.select_related('category', 'brand', 'author').order_by('-id')[:6]
    return Response({
        'product': ProductSerializer(product, context={'request': request}).data,
        'related': products_json(request, related),
    })


# ---------- Sản phẩm của tôi (member) ----------

# Danh sách sản phẩm do chính user đang đăng nhập đăng. Có tìm theo tên (q) + phân trang 10 sản phẩm
@api_view(['GET'])
@permission_classes([IsMember])
def my_products(request):
    products = Product.objects.filter(author=request.user).select_related('category', 'brand', 'author').order_by('-id')
    q = get_text(request.GET, 'q')
    if q:
        products = products.filter(title__icontains=q)
    return Response(paginate(products, request, 10, lambda items: products_json(request, items)))


# Thêm sản phẩm (gửi form-data: title, price, status, sale, category, brand, company, detail, images (tối đa 3 file))
@api_view(['POST'])
@permission_classes([IsMember])
def my_product_create(request):
    error, product = create_product(request.user, request.data, request.FILES.getlist('images'))
    if error:
        return Response({'error': error}, status=400)
    return Response(ProductSerializer(product, context={'request': request}).data, status=201)


# Sửa sản phẩm của mình (form-data như thêm + delete_images = tên các hình muốn xóa)
@api_view(['PUT'])
@permission_classes([IsMember])
def my_product_update(request, id):
    product = Product.objects.filter(id=id, author=request.user).first()
    if product is None:
        return Response({'error': 'Product not found'}, status=404)
    error, product = update_product(product, request.data, request.FILES.getlist('images'))
    if error:
        return Response({'error': error}, status=400)
    return Response(ProductSerializer(product, context={'request': request}).data)


# Xóa sản phẩm của mình (xóa luôn file hình)
@api_view(['DELETE'])
@permission_classes([IsMember])
def my_product_delete(request, id):
    product = Product.objects.filter(id=id, author=request.user).first()
    if product is None:
        return Response({'error': 'Product not found'}, status=404)
    product.delete_with_images()
    return Response({'message': 'Deleted successfully'})
