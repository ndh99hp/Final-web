# cart/views.py: giỏ hàng (lưu trong session) + thanh toán (checkout)
# Giỏ hàng trong session là 1 list, mỗi sản phẩm là 1 dict:
#   {'id': 1, 'title': 'Áo', 'price': 99.0, 'image': 'products/a.jpg', 'qty': 2}
from decimal import Decimal
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.core.exceptions import ValidationError
from django.core.mail import EmailMultiAlternatives
from django.core.validators import validate_email
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST
from product.models import Product
from users.models import User
from .models import History

MAX_QTY = 99      # mỗi sản phẩm mua tối đa 99 cái


# ---------- các hàm phụ ----------

# Tính tiền từng dòng (item['total']) và tổng tiền cả giỏ hàng
def count_total(cart):
    grand_total = 0
    for item in cart:
        item['total'] = round(item['price'] * item['qty'], 2)
        grand_total += item['total']
    return cart, round(grand_total, 2)


# id hợp lệ = chỉ gồm chữ số và không quá dài
def is_id(text):
    return text is not None and text.isdigit() and len(text) < 10


# ---------- giỏ hàng (AJAX) ----------

# Bấm 'Thêm vào giỏ': JS gửi product_id (và qty) lên, Python lấy sản phẩm trong database rồi bỏ vào session
@require_POST
def add_to_cart(request):
    product_id = request.POST.get('product_id')
    qty = request.POST.get('qty', '1')
    if not is_id(product_id):
        return JsonResponse({'status': 'fail', 'message': 'Sản phẩm không hợp lệ'}, status=400)
    product = Product.objects.filter(id=product_id).first()
    if product is None:
        return JsonResponse({'status': 'fail', 'message': 'Sản phẩm không tồn tại'}, status=404)

    # số lượng: phải là số nguyên từ 1 đến MAX_QTY, sai thì lấy 1
    qty = int(qty) if is_id(qty) and 1 <= int(qty) <= MAX_QTY else 1

    # giá hiện hành: đang Sale thì lấy giá sale, không thì lấy giá gốc
    price = float(product.sale) if product.status == 1 else float(product.price)

    cart = request.session.get('cart', [])
    found = False
    for item in cart:
        if item['id'] == product.id:         # sản phẩm đã có trong giỏ thì cộng thêm số lượng
            item['qty'] = min(item['qty'] + qty, MAX_QTY)
            found = True
            break
    if not found:
        cart.append({
            'id': product.id,
            'title': product.title,
            'price': price,
            'image': product.first_image(),
            'qty': qty,
        })
    request.session['cart'] = cart            # gán lại để session được lưu
    return JsonResponse({
        'status': 'success',
        'message': 'Đã thêm "' + product.title + '" vào giỏ hàng',
        'cart_count': len(cart),               # số loại sản phẩm trong giỏ (hiện ở menu header)
    })


# Trang giỏ hàng
def cart_view(request):
    cart, grand_total = count_total(request.session.get('cart', []))
    return render(request, 'cart/cart.html', {'cart': cart, 'grand_total': grand_total})


# Nút + / - / xóa trong trang giỏ hàng (AJAX). action = up | down | delete
@require_POST
def update_cart(request):
    product_id = request.POST.get('id')
    action = request.POST.get('action')
    cart = request.session.get('cart', [])
    result = {'status': 'fail'}

    for item in cart:
        if str(item['id']) == product_id:
            if action == 'up' and item['qty'] < MAX_QTY:
                item['qty'] += 1
            elif action == 'down' and item['qty'] > 1:
                item['qty'] -= 1
            elif action == 'delete':
                cart.remove(item)
            result = {
                'status': 'success',
                'action': action,
                'new_qty': item['qty'],
                'new_total': round(item['price'] * item['qty'], 2),
            }
            break

    request.session['cart'] = cart
    cart, grand_total = count_total(cart)
    result['grand_total'] = grand_total
    result['cart_count'] = len(cart)
    return JsonResponse(result)


# ---------- thanh toán ----------

# Kiểm tra thông tin người mua (và thông tin đăng ký nhanh nếu chưa đăng nhập). Trả về câu báo lỗi ('' là ổn)
def check_checkout_form(data, need_register):
    name = data.get('name', '').strip()
    email = data.get('email', '').strip()
    phone = data.get('phone', '').strip()

    if name == '' or len(name) > 100:
        return 'Vui lòng nhập họ tên (tối đa 100 ký tự)'
    try:
        validate_email(email)
    except ValidationError:
        return 'Email không hợp lệ'
    # số điện thoại: chỉ gồm chữ số, dài 8-15 số (cho phép dấu + ở đầu)
    if not phone.lstrip('+').isdigit() or not 8 <= len(phone) <= 15:
        return 'Số điện thoại không hợp lệ (8-15 chữ số)'

    if need_register:
        username = data.get('username', '').strip()
        password = data.get('password', '')
        password2 = data.get('password2', '')
        if username == '' or len(username) > 150:
            return 'Vui lòng nhập tên đăng nhập'
        if User.objects.filter(username=username).exists():
            return 'Tên đăng nhập đã tồn tại. Nếu là bạn, hãy bấm "Đăng nhập" ở trên'
        if len(password) < 6:
            return 'Mật khẩu phải từ 6 ký tự'
        if password != password2:
            return 'Mật khẩu nhập lại không khớp'
    return ''


# Gửi mail thông tin đơn hàng cho người mua. Trả về True nếu gửi được
def send_order_mail(history, cart, grand_total):
    html = render_to_string('cart/email_order.html', {'h': history, 'cart': cart, 'grand_total': grand_total})
    text = 'Cảm ơn ' + history.name + ' đã đặt hàng. Mã đơn: #' + str(history.id) + '. Tổng tiền: $' + str(grand_total) + '\n' + history.items
    try:
        mail = EmailMultiAlternatives('Đơn hàng #' + str(history.id) + ' - E-Shopper', text, settings.DEFAULT_FROM_EMAIL, [history.email])
        mail.attach_alternative(html, 'text/html')     # bản có giao diện (HTML)
        mail.send()
        return True
    except Exception as e:
        # in lý do lỗi ra terminal để dễ sửa (sai mật khẩu ứng dụng, mất mạng, ...)
        print('LỖI GỬI MAIL:', e)
        return False


# Trang thanh toán:
# - đã đăng nhập: điền sẵn thông tin, bấm Order là lưu lịch sử + gửi mail
# - chưa đăng nhập: có thêm phần đăng ký nhanh (username + password), đăng ký xong tự đăng nhập rồi đặt hàng luôn
def checkout(request):
    cart = request.session.get('cart', [])
    if len(cart) == 0:
        messages.error(request, 'Giỏ hàng đang trống, hãy chọn sản phẩm trước khi thanh toán')
        return redirect('cart')
    cart, grand_total = count_total(cart)

    need_register = not request.user.is_authenticated
    error = ''
    # form = dữ liệu hiện trong các ô. Đã đăng nhập thì lấy sẵn thông tin của user
    if need_register:
        form = {}
    else:
        u = request.user
        form = {'name': u.get_full_name() or u.username, 'email': u.email, 'phone': u.phone or ''}

    if request.method == 'POST':
        form = request.POST
        error = check_checkout_form(request.POST, need_register)
        if error == '':
            # tạo user (nếu đăng ký nhanh) + lưu history cùng lúc: lỗi thì hủy cả 2
            with transaction.atomic():
                if need_register:
                    user = User.objects.create_user(
                        username=request.POST['username'].strip(),
                        email=request.POST['email'].strip(),
                        password=request.POST['password'],
                    )
                    user.phone = request.POST['phone'].strip()
                    user.is_staff = False          # member thường, không phải admin
                    user.is_superuser = False
                    user.save()
                    login(request, user)           # đăng ký xong tự đăng nhập
                else:
                    user = request.user
                lines = []
                for item in cart:
                    lines.append(item['title'] + ' x' + str(item['qty']) + ' = $' + str(item['total']))
                history = History.objects.create(
                    user=user,
                    name=request.POST['name'].strip(),
                    email=request.POST['email'].strip(),
                    phone=request.POST['phone'].strip(),
                    price=Decimal(str(grand_total)),
                    items='\n'.join(lines),
                )
            mail_ok = send_order_mail(history, cart, grand_total)
            request.session['cart'] = []           # mua xong thì làm trống giỏ hàng
            if mail_ok and 'console' in settings.EMAIL_BACKEND:
                # đang ở chế độ test: mail chỉ in ra terminal, chưa gửi thật
                messages.success(request, 'Đặt hàng thành công (đơn hàng #' + str(history.id) + '). Đang ở chế độ test nên mail chỉ in ra terminal, chưa gửi thật')
            elif mail_ok:
                messages.success(request, 'Đặt hàng thành công! Thông tin đơn hàng #' + str(history.id) + ' đã gửi tới ' + history.email)
            else:
                messages.success(request, 'Đặt hàng thành công (đơn hàng #' + str(history.id) + '), nhưng chưa gửi được mail. Vui lòng kiểm tra cấu hình mail')
            return redirect('home')

    return render(request, 'cart/checkout.html', {
        'cart': cart,
        'grand_total': grand_total,
        'need_register': need_register,
        'form': form,
        'error': error,
    })
