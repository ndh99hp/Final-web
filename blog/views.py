from django.shortcuts import render, get_object_or_404
from .models import Blog


def blog_list(request):
    blogs = Blog.objects.all().order_by('-created_at')
    return render(request, 'blog/list.html', {'blogs': blogs})


def blog_detail(request, slug):
    blog = get_object_or_404(Blog, slug=slug)
    comments = blog.comments.filter(level=0)  # chỉ lấy comment gốc, reply sẽ query lồng sau
    return render(request, 'blog/detail.html', {'blog': blog, 'comments': comments})