# api/views_admin.py: API cho admin (cần token của superuser): user, sản phẩm, lịch sử mua hàng
from django.contrib.auth import authenticate
from django.db.models import Count, Max, Q, Sum
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from cart.models import History
from product.models import Product
from users.models import User, Country
from .helpers import get_text, is_id, paginate, update_product
from .permissions import IsSuperAdmin
from .serializers import HistorySerializer, ProductSerializer, UserSerializer
from .views_auth import check_avatar, is_email
from .views_product import products_json


# Đăng nhập của admin: chỉ superuser mới nhận được token
@api_view(['POST'])
def admin_login(request):
    username = get_text(request.data, 'username')
    password = str(request.data.get('password') or '')

    user = authenticate(username=username, password=password)
    if not user:
        return Response({'error': 'Sai tên đăng nhập hoặc mật khẩu'}, status=400)
    if not user.is_superuser:
        return Response({'error': 'Tài khoản này không phải admin'}, status=403)

    token, created = Token.objects.get_or_create(user=user)
    return Response({'token': token.key, 'user': UserSerializer(user, context={'request': request}).data})


# ---------- user ----------

# Danh sách tất cả user: tìm theo username/email (q), lọc role = admin | member, 10 user / trang
# total_products = số sản phẩm của từng user (SQL: COUNT + GROUP BY)
@api_view(['GET'])
@permission_classes([IsSuperAdmin])
def admin_users(request):
    users = User.objects.select_related('id_country').annotate(total_products=Count('product')).order_by('-date_joined')
    q = get_text(request.GET, 'q')
    role = get_text(request.GET, 'role')
    if q:
        users = users.filter(Q(username__icontains=q) | Q(email__icontains=q))
    if role == 'admin':
        users = users.filter(Q(is_superuser=True) | Q(is_staff=True))
    elif role == 'member':
        users = users.filter(is_superuser=False, is_staff=False)
    return Response(paginate(users, request, 10, lambda items: UserSerializer(items, many=True, context={'request': request}).data))


# Admin sửa thông tin 1 member (chỉ sửa được member). Ô nào không gửi thì giữ nguyên.
# is_active = 0 là khóa tài khoản, password bỏ trống = giữ mật khẩu cũ
@api_view(['PUT'])
@permission_classes([IsSuperAdmin])
def admin_user_update(request, id):
    member = User.objects.filter(id=id, is_superuser=False, is_staff=False).first()
    if member is None:
        return Response({'error': 'User not found'}, status=404)
    data = request.data

    if 'email' in data:
        email = get_text(data, 'email')
        if not is_email(email):
            return Response({'error': 'Email không hợp lệ'}, status=400)
        member.email = email
    for field in ('first_name', 'last_name', 'address', 'phone'):
        if field in data:
            setattr(member, field, get_text(data, field))
    if 'id_country' in data:
        id_country = get_text(data, 'id_country')
        if id_country and not (is_id(id_country) and Country.objects.filter(id=id_country).exists()):
            return Response({'error': 'Quốc gia không hợp lệ'}, status=400)
        member.id_country_id = id_country or None
    if 'is_active' in data:
        member.is_active = get_text(data, 'is_active').lower() in ('1', 'true')
    password = str(data.get('password') or '')
    if password:
        if len(password) < 6:
            return Response({'error': 'Mật khẩu mới phải có ít nhất 6 ký tự'}, status=400)
        member.set_password(password)
    member.save()
    return Response({'message': 'Đã cập nhật user "' + member.username + '"', 'user': UserSerializer(member, context={'request': request}).data})


# Admin xóa 1 member: xóa luôn sản phẩm + hình + avatar của member đó.
# Lịch sử mua hàng vẫn giữ lại (History.user là SET_NULL => chỉ để trống người mua)
@api_view(['DELETE'])
@permission_classes([IsSuperAdmin])
def admin_user_delete(request, id):
    member = User.objects.filter(id=id, is_superuser=False, is_staff=False).first()
    if member is None:
        return Response({'error': 'User not found'}, status=404)
    username = member.username
    products = list(member.product_set.all())
    for product in products:
        product.delete_with_images()
    if member.avatar:
        member.avatar.delete(save=False)
    member.delete()
    return Response({'message': 'Đã xóa user "' + username + '" và ' + str(len(products)) + ' sản phẩm của user này'})


# Superuser tạo thêm tài khoản superuser mới
@api_view(['POST'])
@permission_classes([IsSuperAdmin])
def admin_register_superuser(request):
    username = get_text(request.data, 'username')
    email = get_text(request.data, 'email')
    password = str(request.data.get('password') or '')
    password2 = str(request.data.get('password2') or '')
    id_country = get_text(request.data, 'id_country')
    avatar = request.FILES.get('avatar')

    if username == '' or len(username) > 150:
        return Response({'error': 'Vui lòng nhập tên đăng nhập (tối đa 150 ký tự)'}, status=400)
    if User.objects.filter(username=username).exists():
        return Response({'error': 'Tên đăng nhập đã tồn tại'}, status=400)
    if not is_email(email):
        return Response({'error': 'Email không hợp lệ'}, status=400)
    if len(password) < 6:
        return Response({'error': 'Mật khẩu phải có ít nhất 6 ký tự'}, status=400)
    if password != password2:
        return Response({'error': 'Mật khẩu nhập lại không khớp'}, status=400)
    if id_country and not (is_id(id_country) and Country.objects.filter(id=id_country).exists()):
        return Response({'error': 'Quốc gia không hợp lệ'}, status=400)
    error = check_avatar(avatar)
    if error:
        return Response({'error': error}, status=400)

    new_admin = User.objects.create_user(
        username=username,
        email=email,
        password=password,
        first_name=get_text(request.data, 'first_name'),
        last_name=get_text(request.data, 'last_name'),
    )
    new_admin.is_staff = True
    new_admin.is_superuser = True
    new_admin.level = 2
    if id_country:
        new_admin.id_country_id = id_country
    if avatar:
        new_admin.avatar = avatar
    new_admin.save()
    return Response({'message': 'Đã tạo superuser "' + username + '"', 'user': UserSerializer(new_admin, context={'request': request}).data}, status=201)


# ---------- sản phẩm ----------

# Tất cả sản phẩm của mọi member: tìm theo tên sản phẩm (q) và theo tên member (member), 10 sản phẩm / trang
@api_view(['GET'])
@permission_classes([IsSuperAdmin])
def admin_products(request):
    products = Product.objects.select_related('author', 'category', 'brand').order_by('-id')
    q = get_text(request.GET, 'q')
    member = get_text(request.GET, 'member')
    if q:
        products = products.filter(title__icontains=q)
    if member:
        products = products.filter(author__username__icontains=member)
    return Response(paginate(products, request, 10, lambda items: products_json(request, items)))


# Admin sửa bất kỳ sản phẩm nào (form-data giống member sửa sản phẩm)
@api_view(['PUT'])
@permission_classes([IsSuperAdmin])
def admin_product_update(request, id):
    product = Product.objects.filter(id=id).first()
    if product is None:
        return Response({'error': 'Product not found'}, status=404)
    error, product = update_product(product, request.data, request.FILES.getlist('images'))
    if error:
        return Response({'error': error}, status=400)
    return Response(ProductSerializer(product, context={'request': request}).data)


# Admin xóa bất kỳ sản phẩm nào
@api_view(['DELETE'])
@permission_classes([IsSuperAdmin])
def admin_product_delete(request, id):
    product = Product.objects.filter(id=id).first()
    if product is None:
        return Response({'error': 'Product not found'}, status=404)
    title = product.title
    owner = product.author.username
    product.delete_with_images()
    return Response({'message': 'Đã xóa sản phẩm "' + title + '" của user ' + owner})


# ---------- lịch sử mua hàng ----------

# Phần 1 (members): thống kê theo member = gom các đơn của cùng 1 user (SQL: GROUP BY user)
# Phần 2 (results): danh sách tất cả đơn hàng, tìm theo tên / email / sđt / username (q), lọc đơn của 1 member (user = id)
@api_view(['GET'])
@permission_classes([IsSuperAdmin])
def admin_history(request):
    members = (History.objects
               .values('user_id', 'user__username')
               .annotate(orders=Count('id'), total=Sum('price'), last_order=Max('created_at'))
               .order_by('-total'))
    summary = History.objects.aggregate(orders=Count('id'), total=Sum('price'))

    orders = History.objects.select_related('user').order_by('-id')
    q = get_text(request.GET, 'q')
    user_id = get_text(request.GET, 'user')
    if q:
        orders = orders.filter(Q(name__icontains=q) | Q(email__icontains=q) | Q(phone__icontains=q) | Q(user__username__icontains=q))
    if is_id(user_id):
        orders = orders.filter(user_id=user_id)

    data = paginate(orders, request, 10, lambda items: HistorySerializer(items, many=True, context={'request': request}).data)
    data['summary'] = summary
    data['members'] = list(members)
    return Response(data)
