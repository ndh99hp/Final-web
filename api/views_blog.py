# api/views_blog.py: blog (list, detail), đánh giá sao (rate) và bình luận (comment)
import math
from django.db.models import Avg, Q
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from blog.models import Blog, Comment, Rate
from .helpers import get_text, is_id, paginate
from .serializers import media_url


# Làm tròn kiểu PHP: luôn làm tròn LÊN ở mốc .5 (khác round của Python)
def php_round(value):
    return int(math.floor(value + 0.5))


def blog_to_dict(request, blog):
    return {
        'id': blog.id,
        'title': blog.title,
        'slug': blog.slug,
        'description': blog.description,
        'image': media_url(request, blog.image.name if blog.image else ''),
        'created_at': blog.created_at,
        'author': blog.author.username if blog.author else None,
    }


# Đổi 1 comment thành dict, kèm luôn các reply (trả lời) lồng bên trong (mục replies)
def comment_to_dict(request, comment):
    avatar = None
    if comment.id_user and comment.id_user.avatar:
        avatar = media_url(request, comment.id_user.avatar.name)
    replies = []
    for r in comment.replies.order_by('created_at'):
        replies.append(comment_to_dict(request, r))
    return {
        'id': comment.id,
        'name': comment.name,
        'cmt': comment.cmt,
        'level': comment.level,
        'parent_id': comment.parent_id,
        'avatar': avatar,
        'created_at': comment.created_at,
        'replies': replies,
    }


# Danh sách bài blog: mới nhất lên đầu, 3 bài / trang
@api_view(['GET'])
def blog_list(request):
    blogs = Blog.objects.select_related('author').order_by('-created_at', '-id')
    return Response(paginate(blogs, request, 3, lambda items: [blog_to_dict(request, b) for b in items]))


# Chi tiết 1 bài blog (tìm theo slug): nội dung, comment (lồng nhau), bài trước / sau, điểm đánh giá
# Gửi kèm token thì có thêm your_rate (điểm mình đã đánh giá)
@api_view(['GET'])
def blog_detail(request, slug):
    blog = Blog.objects.filter(slug=slug).first()
    if blog is None:
        return Response({'error': 'Blog not found'}, status=404)

    comments = blog.comments.filter(parent__isnull=True).order_by('-created_at')
    # bài trước = mới hơn, bài sau = cũ hơn. Nếu 2 bài có cùng giờ tạo thì dùng id để phân biệt
    prev_blog = Blog.objects.filter(Q(created_at__gt=blog.created_at) | Q(created_at=blog.created_at, id__gt=blog.id)).order_by('created_at', 'id').first()
    next_blog = Blog.objects.filter(Q(created_at__lt=blog.created_at) | Q(created_at=blog.created_at, id__lt=blog.id)).order_by('-created_at', '-id').first()

    avg = blog.rates.aggregate(Avg('rate'))['rate__avg'] or 0
    your_rate = None
    if request.user.is_authenticated:
        existing = Rate.objects.filter(id_blog=blog, id_user=request.user).first()
        if existing:
            your_rate = existing.rate

    data = blog_to_dict(request, blog)
    data['content'] = blog.content
    return Response({
        'blog': data,
        'comments': [comment_to_dict(request, c) for c in comments],
        'prev': {'title': prev_blog.title, 'slug': prev_blog.slug} if prev_blog else None,
        'next': {'title': next_blog.title, 'slug': next_blog.slug} if next_blog else None,
        'rating': {
            'average': php_round(avg),
            'average_raw': round(avg, 1),
            'count': blog.rates.count(),
            'your_rate': your_rate,
        },
    })


# Đánh giá sao (1 đến 5), mỗi người đánh giá 1 lần. Gửi rate
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def blog_rate(request, slug):
    blog = Blog.objects.filter(slug=slug).first()
    if blog is None:
        return Response({'error': 'Blog not found'}, status=404)
    if Rate.objects.filter(id_blog=blog, id_user=request.user).exists():
        return Response({'error': 'Bạn đã đánh giá bài viết này rồi'}, status=400)

    try:
        rate_value = int(get_text(request.data, 'rate'))
    except ValueError:
        return Response({'error': 'Điểm đánh giá không hợp lệ'}, status=400)
    if rate_value < 1 or rate_value > 5:
        return Response({'error': 'Điểm đánh giá phải từ 1 đến 5'}, status=400)

    Rate.objects.create(id_blog=blog, id_user=request.user, rate=rate_value)
    avg = blog.rates.aggregate(Avg('rate'))['rate__avg'] or 0
    return Response({
        'message': 'Đánh giá thành công',
        'your_rate': rate_value,
        'average': php_round(avg),
        'average_raw': round(avg, 1),
        'count': blog.rates.count(),
    }, status=201)


# Gửi bình luận: cmt = nội dung, parent_id = id comment muốn trả lời (không gửi thì là comment gốc)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def blog_comment(request, slug):
    blog = Blog.objects.filter(slug=slug).first()
    if blog is None:
        return Response({'error': 'Blog not found'}, status=404)

    cmt = get_text(request.data, 'cmt')
    parent_id = get_text(request.data, 'parent_id')
    if cmt == '':
        return Response({'error': 'Nội dung bình luận không được để trống'}, status=400)

    parent = None
    level = 0
    if parent_id:
        if is_id(parent_id):
            parent = Comment.objects.filter(id=parent_id, id_blog=blog).first()
        if parent is None:
            return Response({'error': 'Comment cần trả lời không tồn tại'}, status=404)
        level = parent.level + 1

    comment = Comment.objects.create(
        id_blog=blog,
        id_user=request.user,
        name=request.user.username,
        cmt=cmt,
        level=level,
        parent=parent,
    )
    return Response({'message': 'Gửi bình luận thành công', 'comment': comment_to_dict(request, comment)}, status=201)
