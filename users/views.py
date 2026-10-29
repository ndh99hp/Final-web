# users/views.py: xử lý đăng nhập, đăng ký, đăng xuất, danh sách user, cập nhật tài khoản
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.shortcuts import render, redirect
from .models import User, Country
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.views import redirect_to_login
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.utils.http import url_has_allowed_host_and_scheme
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


# Đăng nhập: authenticate() kiểm tra username/password, login() lưu vào session
# ?next=/checkout/ : đăng nhập xong thì quay lại trang đó (chỉ nhận link trong web mình, tránh bị chuyển sang web lạ)
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
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

# Đăng xuất: xóa session rồi quay về trang login
def logout_view(request):
    logout(request)
    return redirect('login')
# Decorator tự viết: chỉ cho superuser vào, người khác bị chuyển về trang login
def superuser_required(view_func):
    def check(user):
        return user.is_authenticated and user.is_superuser
    decorated = user_passes_test(check, login_url='login')
    return decorated(view_func)


# Danh sách tất cả user (chỉ superuser xem được)
@superuser_required
def list_users_view(request):
    users = User.objects.all().order_by('-date_joined')
    return render(request, 'users/list_users.html', {'users': users})


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
# Trang Account/update: user đang đăng nhập sửa thông tin của chính mình
# Nếu đổi mật khẩu thì dùng update_session_auth_hash để khỏi bị đăng xuất
@login_required
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
