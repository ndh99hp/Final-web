from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Product
def product_list(request):
    products = Product.objects.all()
    return render(request, 'product/product_list.html', {'products': products})
@login_required
def product_create(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        price = request.POST.get('price')
        image = request.FILES.get('image')
        new_product = Product(title=title, price=price, image=image, author=request.user)
        new_product.save()
        return redirect('product_list')
    return render(request, 'product/product_create.html')
@login_required
def my_products(request):
    products = Product.objects.filter(author=request.user)
    return render(request, 'product/my_products.html', {'products': products})
@login_required
def edit_product(request, product_id):
    product = Product.objects.get(id=product_id)
    if request.method == 'POST':
        product.title = request.POST.get('title')
        product.price = request.POST.get('price')
        if 'image' in request.FILES:
            product.image = request.FILES['image']
        product.save()
        return redirect('my_products')
    return render(request, 'product/edit_product.html', {'product': product})
@login_required
def delete_product(request, product_id):
    product = Product.objects.get(id=product_id)
    product.delete()
    return redirect('my_products')
def product_detail(request, product_id):
    product = Product.objects.get(id=product_id)
    return render(request, 'product/product_detail.html', {'product': product})