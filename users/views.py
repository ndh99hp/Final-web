# users/views.py: xử lý đăng nhập, đăng ký, đăng xuất, danh sách user, cập nhật tài khoản
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.shortcuts import render, redirect
from .models import User, Country
from django.contrib.auth.views import redirect_to_login
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.utils.http import url_has_allowed_host_and_scheme
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.urls import reverse
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from .decorators import member_required, is_admin_account, superuser_required
from urllib.parse import urlencode
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.core.validators import validate_email
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404


# Đăng nhập: authenticate() kiểm tra username/password, login() lưu vào session
# ?next=/checkout/ : đăng nhập xong thì quay lại trang đó (chỉ nhận link trong web mình, tránh bị chuyển sang web lạ)
# Phân quyền: trang này chỉ cho member đăng nhập. Tài khoản admin phải đăng nhập ở trang quản trị /admin/
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None and is_admin_account(user):
            messages.error(request, 'Đây là tài khoản quản trị (admin). Vui lòng đăng nhập tại trang quản trị /admin/.')
        elif user is not None:
            login(request, user)
            next_url = request.GET.get('next', '')
            if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts=request.get_host()):
                return redirect(next_url)
            return redirect('home')
        else:
            messages.error(request, 'Sai tên đăng nhập hoặc mật khẩu.')
    return render(request, 'users/login.html')

# Gửi mail chào mừng cho user vừa đăng ký (làm theo Bài 18: Send mail)
# Trả về True nếu gửi được. Gửi lỗi (sai App Password, mất mạng...) thì in lý do ra terminal và trả về False
def send_welcome_email(user, site_url):
    subject = 'Chào mừng bạn đến với website!'
    from_email = settings.DEFAULT_FROM_EMAIL
    to = [user.email]

    # Nội dung text fallback (cho mail client không hiện được HTML)
    text_content = f"Chào {user.username}, cảm ơn bạn đã đăng ký."

    # Render HTML từ template
    html_content = render_to_string('emails/welcome_email.html', {'user': user, 'site_url': site_url})

    # Gửi email
    try:
        msg = EmailMultiAlternatives(subject, text_content, from_email, to)
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        return True
    except Exception as e:
        print('LỖI GỬI MAIL:', e)
        return False


# Đăng ký tài khoản thường: kiểm tra mật khẩu nhập lại + trùng username rồi tạo user
def register_view(request):
    countries = Country.objects.all()

    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        id_country = request.POST.get('id_country')
        avatar = request.FILES.get('avatar')

        if password != password2:
            messages.error(request, 'Mật khẩu nhập lại không khớp.')
            return render(request, 'users/register.html', {'countries': countries})

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Tên đăng nhập đã tồn tại.')
            return render(request, 'users/register.html', {'countries': countries})

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )
        # Gán quyền: tài khoản đăng ký ở frontend luôn là member (không vào được trang quản trị)
        user.is_superuser = False
        user.is_staff = False
        if id_country:
            user.id_country_id = id_country
        if avatar:
            user.avatar = avatar
        user.save()

        # Đăng ký xong thì gửi mail chào mừng tới email vừa nhập
        mail_ok = send_welcome_email(user, request.build_absolute_uri('/'))
        if mail_ok and 'console' in settings.EMAIL_BACKEND:
            messages.success(request, 'Đăng ký thành công! Vui lòng đăng nhập. (Đang ở chế độ test: mail chỉ in ra terminal, chưa gửi thật)')
        elif mail_ok:
            messages.success(request, 'Đăng ký thành công, đã gửi mail chào mừng tới ' + user.email + '. Vui lòng đăng nhập.')
        else:
            messages.success(request, 'Đăng ký thành công! Vui lòng đăng nhập. (Chưa gửi được mail chào mừng, hãy kiểm tra cấu hình mail)')
        return redirect('login')

    return render(request, 'users/register.html', {'countries': countries})

# Đăng xuất: xóa session rồi quay về trang login (admin thì về trang đăng nhập quản trị)
def logout_view(request):
    was_admin = is_admin_account(request.user)
    logout(request)
    if was_admin:
        return redirect('admin:login')
    return redirect('login')
# ---------- Trang quản lý (admin): list user ----------
# Danh sách tất cả user (chỉ superuser xem được): tìm theo username/email, lọc admin/member, phân trang
# annotate(total_products=Count('product')) = đếm số sản phẩm của từng user (SQL: COUNT + GROUP BY)
@superuser_required
def list_users_view(request):
    users = User.objects.annotate(total_products=Count('product')).order_by('-date_joined')

    q = request.GET.get('q', '').strip()
    role = request.GET.get('role', '')
    if q:
        # Q(...) | Q(...) = điều kiện HOẶC: username chứa q hoặc email chứa q
        users = users.filter(Q(username__icontains=q) | Q(email__icontains=q))
    if role == 'admin':
        users = users.filter(Q(is_superuser=True) | Q(is_staff=True))
    elif role == 'member':
        users = users.filter(is_superuser=False, is_staff=False)
    else:
        role = ''

    page_obj = Paginator(users, 10).get_page(request.GET.get('page'))   # 10 user / trang
    return render(request, 'users/list_users.html', {
        'page_obj': page_obj,
        'q': q,
        'role': role,
        'page_query': urlencode({k: v for k, v in {'q': q, 'role': role}.items() if v}),
    })


# Admin sửa thông tin 1 member. Chỉ sửa được member (tài khoản admin khác sẽ báo 404)
# Có thể khóa / mở khóa tài khoản (is_active) và đặt lại mật khẩu (bỏ trống = giữ mật khẩu cũ)
@superuser_required
def admin_edit_user_view(request, user_id):
    member = get_object_or_404(User, id=user_id, is_superuser=False, is_staff=False)
    countries = Country.objects.all()
    # form = dữ liệu hiện trong các ô: lúc mới mở lấy từ database, khi bị lỗi thì giữ lại cái vừa nhập
    form = {
        'email': member.email,
        'first_name': member.first_name,
        'last_name': member.last_name,
        'phone': member.phone or '',
        'address': member.address or '',
        'id_country': str(member.id_country_id or ''),
        'is_active': '1' if member.is_active else '0',
    }

    if request.method == 'POST':
        form = request.POST
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        id_country = request.POST.get('id_country', '')

        error = ''
        try:
            validate_email(email)
        except ValidationError:
            error = 'Email không hợp lệ'
        if error == '' and password and len(password) < 6:
            error = 'Mật khẩu mới phải có ít nhất 6 ký tự'
        if error == '' and id_country and not (id_country.isdigit() and Country.objects.filter(id=id_country).exists()):
            error = 'Quốc gia không hợp lệ'

        if error:
            messages.error(request, error)
        else:
            member.email = email
            member.first_name = request.POST.get('first_name', '').strip()
            member.last_name = request.POST.get('last_name', '').strip()
            member.phone = request.POST.get('phone', '').strip()
            member.address = request.POST.get('address', '').strip()
            member.id_country_id = id_country or None
            member.is_active = request.POST.get('is_active') == '1'     # 0 = khóa, không đăng nhập được nữa
            if password:
                member.set_password(password)
            member.save()
            messages.success(request, 'Đã cập nhật user "' + member.username + '"')
            return redirect('list_users')

    return render(request, 'users/admin_edit_user.html', {'member': member, 'countries': countries, 'form': form})


# Admin xóa 1 member (chỉ nhận POST). Xóa luôn sản phẩm + hình của member đó.
# Lịch sử mua hàng vẫn giữ lại (History.user là SET_NULL => chỉ để trống người mua)
@superuser_required
def admin_delete_user_view(request, user_id):
    member = get_object_or_404(User, id=user_id, is_superuser=False, is_staff=False)
    if request.method == 'POST':
        username = member.username
        products = list(member.product_set.all())
        for product in products:
            product.delete_with_images()
        if member.avatar:
            member.avatar.delete(save=False)     # xóa file avatar
        member.delete()
        messages.success(request, 'Đã xóa user "' + username + '" và ' + str(len(products)) + ' sản phẩm của user này')
    return redirect('list_users')


# Superuser tạo thêm tài khoản superuser mới (is_staff + is_superuser, level = 2)
@superuser_required
def register_superuser_view(request):
    countries = Country.objects.all()

    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        id_country = request.POST.get('id_country')
        avatar = request.FILES.get('avatar')

        if password != password2:
            messages.error(request, 'Mật khẩu nhập lại không khớp.')
            return render(request, 'users/register_superuser.html', {'countries': countries})

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Tên đăng nhập đã tồn tại.')
            return render(request, 'users/register_superuser.html', {'countries': countries})

        new_admin = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )
        new_admin.is_staff = True
        new_admin.is_superuser = True
        new_admin.level = 2
        if id_country:
            new_admin.id_country_id = id_country
        if avatar:
            new_admin.avatar = avatar
        new_admin.save()

        messages.success(request, f'Đã tạo superuser "{username}" thành công.')
        return redirect('list_users')

    return render(request, 'users/register_superuser.html', {'countries': countries})
# Trang Account/update: member đang đăng nhập sửa thông tin của chính mình
# Nếu đổi mật khẩu thì dùng update_session_auth_hash để khỏi bị đăng xuất
@member_required
def account_update_view(request):
    user = request.user
    countries = Country.objects.all()

    if request.method == 'POST':
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        address = request.POST.get('address')
        phone = request.POST.get('phone')
        id_country = request.POST.get('id_country')
        password = request.POST.get('password')
        avatar = request.FILES.get('avatar')

        user.email = email
        user.first_name = first_name
        user.last_name = last_name
        user.address = address
        user.phone = phone
        if id_country:
            user.id_country_id = id_country
        if avatar:
            user.avatar = avatar
        if password:
            user.set_password(password)

        user.save()

        if password:
            update_session_auth_hash(request, user)

        messages.success(request, 'Cập nhật thông tin thành công!')
        return redirect('account_update')

    return render(request, 'users/account_update.html', {'countries': countries})


# ---------- Quên mật khẩu ----------
# B1: trang /forgot-password/ nhập email -> gửi mail có link đặt lại mật khẩu
# B2: member bấm link trong mail -> trang /reset-password/<uidb64>/<token>/ nhập mật khẩu mới
# uidb64 = id của user được mã hóa base64, token = chuỗi bí mật do Django tạo (default_token_generator).
# Token tự hết hiệu lực khi user đã đổi mật khẩu (hoặc quá 3 ngày) => link chỉ dùng được 1 lần

# Gửi mail chứa link đặt lại mật khẩu (giống send_welcome_email). Gửi được trả về True
def send_reset_password_email(user, reset_url):
    subject = 'Đặt lại mật khẩu - E-Shopper'
    text_content = f"Chào {user.username}, hãy mở link sau để đặt lại mật khẩu: {reset_url}"
    html_content = render_to_string('emails/reset_password_email.html', {'user': user, 'reset_url': reset_url})
    try:
        msg = EmailMultiAlternatives(subject, text_content, settings.DEFAULT_FROM_EMAIL, [user.email])
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        return True
    except Exception as e:
        print('LỖI GỬI MAIL:', e)
        return False


def forgot_password_view(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        # chỉ tìm tài khoản member còn hoạt động (admin đổi mật khẩu trong trang quản trị)
        users = User.objects.filter(email__iexact=email, is_active=True, is_superuser=False, is_staff=False)

        if not email:
            messages.error(request, 'Vui lòng nhập email.')
        elif not users.exists():
            messages.error(request, 'Email này chưa đăng ký tài khoản thành viên nào.')
        else:
            # 1 email có thể dùng cho nhiều tài khoản => gửi cho từng tài khoản 1 link riêng
            mail_ok = True
            for user in users:
                uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
                token = default_token_generator.make_token(user)
                reset_url = request.build_absolute_uri(reverse('reset_password', args=[uidb64, token]))
                if not send_reset_password_email(user, reset_url):
                    mail_ok = False

            if mail_ok and 'console' in settings.EMAIL_BACKEND:
                messages.success(request, 'Đang ở chế độ test: mail (có link đặt lại mật khẩu) chỉ in ra terminal, chưa gửi thật.')
            elif mail_ok:
                messages.success(request, 'Đã gửi link đặt lại mật khẩu tới ' + email + '. Hãy kiểm tra hộp thư (cả mục Spam).')
            else:
                messages.error(request, 'Chưa gửi được mail, vui lòng thử lại sau (hoặc kiểm tra cấu hình mail).')
                return render(request, 'users/forgot_password.html', {'email': email})
            return redirect('forgot_password')

        return render(request, 'users/forgot_password.html', {'email': email})

    return render(request, 'users/forgot_password.html')


def reset_password_view(request, uidb64, token):
    # giải mã uidb64 ra id rồi tìm user. Link bị sửa bậy thì user = None
    try:
        user_id = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=user_id)
    except (ValueError, TypeError, OverflowError, User.DoesNotExist):
        user = None

    # kiểm tra token: sai hoặc đã dùng rồi (đã đổi mật khẩu) thì báo link không hợp lệ
    if user is None or not default_token_generator.check_token(user, token):
        return render(request, 'users/reset_password.html', {'invalid': True})

    if request.method == 'POST':
        password = request.POST.get('password', '')
        password2 = request.POST.get('password2', '')
        if len(password) < 6:
            messages.error(request, 'Mật khẩu phải có ít nhất 6 ký tự.')
        elif password != password2:
            messages.error(request, 'Mật khẩu nhập lại không khớp.')
        else:
            user.set_password(password)     # set_password tự mã hóa mật khẩu trước khi lưu
            user.save()
            messages.success(request, 'Đổi mật khẩu thành công! Hãy đăng nhập bằng mật khẩu mới.')
            return redirect('login')

    return render(request, 'users/reset_password.html', {'invalid': False, 'reset_user': user})
