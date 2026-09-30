from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.shortcuts import render, redirect
from users.models import User, Country
def home(request):
    return render(request, 'home.html')
def shop(request):
    return render(request, 'shop.html')
def product_details(request):
    return render(request, 'product_details.html')
def checkout(request):
    return render(request, 'checkout.html')
def show_cart(request):
    return render(request, 'cart.html')
def account(request):
    return render(request, 'account.html')
def logout(request):
    pass
def login(request):
    return render(request, 'login.html')
def register(request):
    return render(request, 'register.html')
def page404(request):
    return render(request, '404.html')
def contact(request):
    return render(request, 'contact.html')