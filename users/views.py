from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.shortcuts import render, redirect
from .models import User, Country
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.views import redirect_to_login
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('blog_list')
        else:
            messages.error(request, 'Sai tên đăng nhập hoặc mật khẩu.')
    return render(request, 'users/login.html')

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

        messages.success(request, 'Đăng ký thành công! Vui lòng đăng nhập.')
        return redirect('login')

    return render(request, 'users/register.html', {'countries': countries})

def logout_view(request):
    logout(request)
    return redirect('login')
def superuser_required(view_func):
    def check(user):
        return user.is_authenticated and user.is_superuser
    decorated = user_passes_test(check, login_url='login')
    return decorated(view_func)


@superuser_required
def list_users_view(request):
    users = User.objects.all().order_by('-date_joined')
    return render(request, 'users/list_users.html', {'users': users})


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


@login_required
def account_my_product_view(request):
    return render(request, 'users/account_placeholder.html', {
        'title': 'Sản phẩm của tôi',
        'note': 'Tính năng này sẽ hoạt động sau khi hoàn thành app Product.'
    })


@login_required
def account_add_product_view(request):
    return render(request, 'users/account_placeholder.html', {
        'title': 'Thêm sản phẩm',
        'note': 'Tính năng này sẽ hoạt động sau khi hoàn thành app Product.'
    })