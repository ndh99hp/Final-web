import math
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Avg
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Blog, Comment, Rate


def php_round(value):
    """Làm tròn kiểu PHP: luôn làm tròn LÊN ở mốc .5 (khác Python round mặc định)."""
    return int(math.floor(value + 0.5))


def blog_list(request):
    all_blogs = Blog.objects.all().order_by('-created_at')
    paginator = Paginator(all_blogs, 3)
    page_number = request.GET.get('page')
    blogs = paginator.get_page(page_number)
    return render(request, 'blog/list.html', {'blogs': blogs})


def blog_detail(request, slug):
    blog = get_object_or_404(Blog, slug=slug)

    comments = blog.comments.filter(parent__isnull=True).order_by('-created_at')

    prev_blog = Blog.objects.filter(created_at__gt=blog.created_at).order_by('created_at').first()
    next_blog = Blog.objects.filter(created_at__lt=blog.created_at).order_by('-created_at').first()

    avg = blog.rates.aggregate(Avg('rate'))['rate__avg'] or 0
    user_rating = None
    if request.user.is_authenticated:
        existing = Rate.objects.filter(id_blog=blog, id_user=request.user).first()
        if existing:
            user_rating = existing.rate

    return render(request, 'blog/detail.html', {
        'blog': blog,
        'comments': comments,
        'prev_blog': prev_blog,
        'next_blog': next_blog,
        'avg_rating': php_round(avg),
        'avg_rating_raw': round(avg, 1),
        'rate_count': blog.rates.count(),
        'user_rating': user_rating,
    })


@require_POST
def rate_blog_view(request, slug):
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'message': 'Vui lòng đăng nhập để đánh giá.'}, status=401)

    blog = get_object_or_404(Blog, slug=slug)

    if Rate.objects.filter(id_blog=blog, id_user=request.user).exists():
        return JsonResponse({'success': False, 'message': 'Bạn đã đánh giá bài viết này rồi.'}, status=400)

    try:
        rate_value = int(request.POST.get('rate'))
    except (TypeError, ValueError):
        return JsonResponse({'success': False, 'message': 'Điểm đánh giá không hợp lệ.'}, status=400)

    if rate_value < 1 or rate_value > 5:
        return JsonResponse({'success': False, 'message': 'Điểm đánh giá phải từ 1 đến 5.'}, status=400)

    Rate.objects.create(id_blog=blog, id_user=request.user, rate=rate_value)

    avg = blog.rates.aggregate(Avg('rate'))['rate__avg'] or 0
    count = blog.rates.count()

    return JsonResponse({
        'success': True,
        'message': 'Đánh giá thành công!',
        'your_rate': rate_value,
        'average': php_round(avg),
        'average_raw': round(avg, 1),
        'count': count,
    })


@require_POST
def add_comment_ajax(request, slug):
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'message': 'Vui lòng đăng nhập để bình luận.'}, status=401)

    blog = get_object_or_404(Blog, slug=slug)
    cmt_text = request.POST.get('cmt', '').strip()
    parent_id = request.POST.get('parent_id')

    if not cmt_text:
        return JsonResponse({'success': False, 'message': 'Nội dung bình luận không được để trống.'}, status=400)

    parent = None
    level = 0
    if parent_id:
        parent = get_object_or_404(Comment, id=parent_id, id_blog=blog)
        level = parent.level + 1

    comment = Comment.objects.create(
        id_blog=blog,
        id_user=request.user,
        name=request.user.username,
        cmt=cmt_text,
        level=level,
        parent=parent,
    )
    avatar_url = '/static/images/blog/man-one.jpg'
    if request.user.avatar:
        avatar_url = request.user.avatar.url

    return JsonResponse({
        'success': True,
        'message': 'Gửi bình luận thành công!',
        'comment': {
            'id': comment.id,
            'name': comment.name,
            'cmt': comment.cmt,
            'level': comment.level,
            'parent_id': parent.id if parent else None,
            'time': comment.created_at.strftime('%H:%M'),
            'date': comment.created_at.strftime('%d %m, %Y'),
            'avatar_url': avatar_url,
        }
    })