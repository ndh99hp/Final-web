from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.shortcuts import render, redirect
from users.models import User, Country


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
    return render(request, 'frontend/login.html')


def register_view(request):
    countries = Country.objects.all()

    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        id_country = request.POST.get('id_country')

        if password != password2:
            messages.error(request, 'Mật khẩu nhập lại không khớp.')
            return render(request, 'frontend/register.html', {'countries': countries})

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Tên đăng nhập đã tồn tại.')
            return render(request, 'frontend/register.html', {'countries': countries})

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
        )
        if id_country:
            user.id_country_id = id_country
            user.save()

        messages.success(request, 'Đăng ký thành công! Vui lòng đăng nhập.')
        return redirect('login')

    return render(request, 'frontend/register.html', {'countries': countries})


def logout_view(request):
    logout(request)
    return redirect('login')