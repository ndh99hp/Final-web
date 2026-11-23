# api/views_cart.py: giỏ hàng (lưu trong database, cần token của member), thanh toán, lịch sử đơn hàng
from decimal import Decimal
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.db import transaction
from django.template.loader import render_to_string
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from cart.models import CartItem, History
from product.models import Product
from .helpers import MAX_QTY, final_price_of, get_text, is_id, paginate
from .permissions import IsMember
from .serializers import HistorySerializer, media_url
from .views_auth import is_email


# Đọc giỏ hàng của user: danh sách sản phẩm (kèm giá hiện tại, thành tiền) + tổng tiền + số loại sản phẩm
def cart_data(request):
    items = []
    grand_total = Decimal('0')
    cart_items = CartItem.objects.filter(user=request.user).select_related('product').order_by('id')
    for c in cart_items:
        price = final_price_of(c.product)
        total = price * c.qty
        grand_total += total
        items.append({
            'product_id': c.product.id,
            'title': c.product.title,
            'image': media_url(request, c.product.first_image()),
            'price': price,
            'qty': c.qty,
            'total': total,
        })
    return {'items': items, 'grand_total': grand_total, 'cart_count': len(items)}


# Xem giỏ hàng
@api_view(['GET'])
@permission_classes([IsMember])
def cart_list(request):
    return Response(cart_data(request))


# Bấm 'Thêm vào giỏ': gửi product_id (và qty). Sản phẩm đã có trong giỏ thì cộng thêm số lượng
@api_view(['POST'])
@permission_classes([IsMember])
def cart_add(request):
    product_id = get_text(request.data, 'product_id')
    qty = get_text(request.data, 'qty') or '1'
    if not is_id(product_id):
        return Response({'error': 'Sản phẩm không hợp lệ'}, status=400)
    product = Product.objects.filter(id=product_id).first()
    if product is None:
        return Response({'error': 'Sản phẩm không tồn tại'}, status=404)

    # số lượng: phải là số nguyên từ 1 đến MAX_QTY, sai thì lấy 1
    qty = int(qty) if is_id(qty) and 1 <= int(qty) <= MAX_QTY else 1

    item, created = CartItem.objects.get_or_create(user=request.user, product=product, defaults={'qty': qty})
    if not created:
        item.qty = min(item.qty + qty, MAX_QTY)
        item.save()
    data = cart_data(request)
    return Response({
        'message': 'Đã thêm "' + product.title + '" vào giỏ hàng',
        'cart_count': data['cart_count'],      # số loại sản phẩm trong giỏ (hiện ở menu cart)
    }, status=201 if created else 200)


# Nút + / - / xóa trong trang giỏ hàng. Gửi product_id và action = up | down | delete. Trả về giỏ hàng mới
@api_view(['PUT'])
@permission_classes([IsMember])
def cart_update(request):
    product_id = get_text(request.data, 'product_id')
    action = get_text(request.data, 'action')
    if action not in ('up', 'down', 'delete'):
        return Response({'error': 'action phải là up, down hoặc delete'}, status=400)

    item = None
    if is_id(product_id):
        item = CartItem.objects.filter(user=request.user, product_id=product_id).first()
    if item is None:
        return Response({'error': 'Sản phẩm không có trong giỏ hàng'}, status=404)

    if action == 'up' and item.qty < MAX_QTY:
        item.qty += 1
        item.save()
    elif action == 'down' and item.qty > 1:
        item.qty -= 1
        item.save()
    elif action == 'delete':
        item.delete()
    return Response(cart_data(request))


# ---------- thanh toán ----------

# Gửi mail thông tin đơn hàng cho người mua. Trả về True nếu gửi được
def send_order_mail(history, items, grand_total):
    html = render_to_string('cart/email_order.html', {'h': history, 'cart': items, 'grand_total': grand_total})
    text = 'Cảm ơn ' + history.name + ' đã đặt hàng. Mã đơn: #' + str(history.id) + '. Tổng tiền: $' + str(grand_total) + '\n' + history.items
    try:
        mail = EmailMultiAlternatives('Đơn hàng #' + str(history.id) + ' - E-Shopper', text, settings.DEFAULT_FROM_EMAIL, [history.email])
        mail.attach_alternative(html, 'text/html')
        mail.send()
        return True
    except Exception as e:
        print('LỖI GỬI MAIL:', e)
        return False


# Đặt hàng: gửi name, email, phone (React lấy sẵn từ api/account/ để điền vào form).
# Lưu lịch sử mua hàng + làm trống giỏ + gửi mail xác nhận
@api_view(['POST'])
@permission_classes([IsMember])
def checkout(request):
    name = get_text(request.data, 'name')
    email = get_text(request.data, 'email')
    phone = get_text(request.data, 'phone')
    if name == '' or len(name) > 100:
        return Response({'error': 'Vui lòng nhập họ tên (tối đa 100 ký tự)'}, status=400)
    if not is_email(email):
        return Response({'error': 'Email không hợp lệ'}, status=400)
    # số điện thoại: chỉ gồm chữ số, dài 8-15 số (cho phép dấu + ở đầu)
    if not phone.lstrip('+').isascii() or not phone.lstrip('+').isdigit() or not 8 <= len(phone) <= 15:
        return Response({'error': 'Số điện thoại không hợp lệ (8-15 chữ số)'}, status=400)

    data = cart_data(request)
    if data['cart_count'] == 0:
        return Response({'error': 'Giỏ hàng đang trống, hãy chọn sản phẩm trước khi thanh toán'}, status=400)

    lines = []
    for item in data['items']:
        lines.append(item['title'] + ' x' + str(item['qty']) + ' = $' + str(item['total']))

    # lưu lịch sử + xóa giỏ hàng cùng lúc: lỗi thì hủy cả 2
    with transaction.atomic():
        history = History.objects.create(
            user=request.user,
            name=name,
            email=email,
            phone=phone,
            price=data['grand_total'],
            items='\n'.join(lines),
        )
        CartItem.objects.filter(user=request.user).delete()

    mail_ok = send_order_mail(history, data['items'], data['grand_total'])
    return Response({
        'message': 'Đặt hàng thành công (đơn hàng #' + str(history.id) + ')',
        'mail_sent': mail_ok,
        'order': HistorySerializer(history, context={'request': request}).data,
    }, status=201)


# Lịch sử mua hàng của chính mình, 10 đơn / trang
@api_view(['GET'])
@permission_classes([IsMember])
def my_orders(request):
    orders = History.objects.filter(user=request.user).order_by('-id')
    return Response(paginate(orders, request, 10, lambda items: HistorySerializer(items, many=True, context={'request': request}).data))
