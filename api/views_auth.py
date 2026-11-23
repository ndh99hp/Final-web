# api/views_auth.py: đăng ký, đăng nhập (trả token), đăng xuất, tài khoản, quên mật khẩu (Bài 23)
from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ValidationError
from django.core.mail import EmailMultiAlternatives
from django.core.validators import validate_email
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from users.models import User, Country
from .helpers import get_text, is_id
from .permissions import IsMember
from .serializers import UserSerializer


# Link trang web ReactJS (dùng trong mail)
def frontend_url():
    return getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')


# Kiểm tra email hợp lệ
def is_email(text):
    try:
        validate_email(text)
        return True
    except ValidationError:
        return False


# Kiểm tra file avatar phải là hình ảnh. Trả về câu báo lỗi ('' là ổn)
def check_avatar(f):
    if f is None:
        return ''
    if not f.content_type.startswith('image/'):
        return 'Avatar phải là file hình ảnh'
    if f.size >= 1024 * 1024:
        return 'Avatar phải nhỏ hơn 1MB'
    return ''


# Gửi mail chào mừng cho user vừa đăng ký (Bài 18: Send mail). Gửi được trả về True
def send_welcome_email(user):
    html_content = render_to_string('emails/welcome_email.html', {'user': user, 'site_url': frontend_url()})
    text_content = 'Chào ' + user.username + ', cảm ơn bạn đã đăng ký.'
    try:
        msg = EmailMultiAlternatives('Chào mừng bạn đến với website!', text_content, settings.DEFAULT_FROM_EMAIL, [user.email])
        msg.attach_alternative(html_content, 'text/html')
        msg.send()
        return True
    except Exception as e:
        print('LỖI GỬI MAIL:', e)
        return False


# Danh sách quốc gia (cho ô chọn country ở form đăng ký / account)
@api_view(['GET'])
def countries(request):
    data = []
    for c in Country.objects.all().order_by('name'):
        data.append({'id': c.id, 'name': c.name})
    return Response(data)


# Đăng ký (gửi form-data nếu có avatar): tạo user + tạo token (giống Bài 23), rồi gửi mail chào mừng
@api_view(['POST'])
def register(request):
    username = get_text(request.data, 'username')
    email = get_text(request.data, 'email')
    password = str(request.data.get('password') or '')
    password2 = str(request.data.get('password2') or '')
    id_country = get_text(request.data, 'id_country')
    avatar = request.FILES.get('avatar')

    if username == '' or len(username) > 150:
        return Response({'error': 'Vui lòng nhập tên đăng nhập (tối đa 150 ký tự)'}, status=400)
    if User.objects.filter(username=username).exists():
        return Response({'error': 'Tên đăng nhập đã tồn tại'}, status=400)
    if not is_email(email):
        return Response({'error': 'Email không hợp lệ'}, status=400)
    if len(password) < 6:
        return Response({'error': 'Mật khẩu phải có ít nhất 6 ký tự'}, status=400)
    if password != password2:
        return Response({'error': 'Mật khẩu nhập lại không khớp'}, status=400)
    if id_country and not (is_id(id_country) and Country.objects.filter(id=id_country).exists()):
        return Response({'error': 'Quốc gia không hợp lệ'}, status=400)
    error = check_avatar(avatar)
    if error:
        return Response({'error': error}, status=400)

    user = User.objects.create_user(
        username=username,
        email=email,
        password=password,
        first_name=get_text(request.data, 'first_name'),
        last_name=get_text(request.data, 'last_name'),
    )
    user.is_superuser = False      # đăng ký ở frontend luôn là member
    user.is_staff = False
    user.phone = get_text(request.data, 'phone')
    user.address = get_text(request.data, 'address')
    if id_country:
        user.id_country_id = id_country
    if avatar:
        user.avatar = avatar
    user.save()

    token, created = Token.objects.get_or_create(user=user)
    mail_ok = send_welcome_email(user)
    return Response({
        'message': 'Đăng ký thành công',
        'mail_sent': mail_ok,
        'token': token.key,
        'user': UserSerializer(user, context={'request': request}).data,
    }, status=201)


# Đăng nhập của member: đúng thì trả về token. Tài khoản admin phải dùng api/admin/login/
@api_view(['POST'])
def login(request):
    username = get_text(request.data, 'username')
    password = str(request.data.get('password') or '')

    user = authenticate(username=username, password=password)
    if not user:
        return Response({'error': 'Sai tên đăng nhập hoặc mật khẩu'}, status=400)
    if user.is_superuser or user.is_staff:
        return Response({'error': 'Đây là tài khoản admin, vui lòng đăng nhập ở api/admin/login/'}, status=403)

    token, created = Token.objects.get_or_create(user=user)
    return Response({'token': token.key, 'user': UserSerializer(user, context={'request': request}).data})


# Đăng xuất: xóa token (token cũ không dùng được nữa). Cả member và admin đều dùng được
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    request.auth.delete()
    return Response({'message': 'Đã đăng xuất'})


# Xem thông tin tài khoản của chính mình (trang account)
@api_view(['GET'])
@permission_classes([IsMember])
def account_detail(request):
    return Response(UserSerializer(request.user, context={'request': request}).data)


# Cập nhật thông tin tài khoản (gửi form-data nếu có avatar). Ô nào không gửi thì giữ nguyên.
# Có gửi password thì đổi mật khẩu (token vẫn dùng tiếp được)
@api_view(['PUT'])
@permission_classes([IsMember])
def account_update(request):
    user = request.user
    data = request.data

    if 'email' in data:
        email = get_text(data, 'email')
        if not is_email(email):
            return Response({'error': 'Email không hợp lệ'}, status=400)
        user.email = email
    for field in ('first_name', 'last_name', 'address', 'phone'):
        if field in data:
            setattr(user, field, get_text(data, field))
    if 'id_country' in data:
        id_country = get_text(data, 'id_country')
        if id_country and not (is_id(id_country) and Country.objects.filter(id=id_country).exists()):
            return Response({'error': 'Quốc gia không hợp lệ'}, status=400)
        user.id_country_id = id_country or None

    password = str(data.get('password') or '')
    if password:
        if len(password) < 6:
            return Response({'error': 'Mật khẩu phải có ít nhất 6 ký tự'}, status=400)
        user.set_password(password)

    avatar = request.FILES.get('avatar')
    error = check_avatar(avatar)
    if error:
        return Response({'error': error}, status=400)
    if avatar:
        user.avatar = avatar

    user.save()
    return Response({'message': 'Cập nhật thông tin thành công', 'user': UserSerializer(user, context={'request': request}).data})


# ---------- Quên mật khẩu ----------
# B1: POST api/forgot-password/ {email} -> gửi mail có link tới trang React: <FRONTEND_URL>/reset-password/<uid>/<token>
# B2: trang React đó gọi POST api/reset-password/ {uid, token, password, password2}
# uid = id của user mã hóa base64, token = chuỗi bí mật do Django tạo. Token hết hiệu lực khi user đã đổi mật khẩu

# Gửi mail chứa link đặt lại mật khẩu. Gửi được trả về True
def send_reset_password_email(user, reset_url):
    html_content = render_to_string('emails/reset_password_email.html', {'user': user, 'reset_url': reset_url})
    text_content = 'Chào ' + user.username + ', hãy mở link sau để đặt lại mật khẩu: ' + reset_url
    try:
        msg = EmailMultiAlternatives('Đặt lại mật khẩu - E-Shopper', text_content, settings.DEFAULT_FROM_EMAIL, [user.email])
        msg.attach_alternative(html_content, 'text/html')
        msg.send()
        return True
    except Exception as e:
        print('LỖI GỬI MAIL:', e)
        return False


@api_view(['POST'])
def forgot_password(request):
    email = get_text(request.data, 'email')
    if not email:
        return Response({'error': 'Vui lòng nhập email'}, status=400)

    # chỉ tìm tài khoản member còn hoạt động (admin đổi mật khẩu trong trang quản trị)
    users = User.objects.filter(email__iexact=email, is_active=True, is_superuser=False, is_staff=False)
    if not users.exists():
        return Response({'error': 'Email này chưa đăng ký tài khoản thành viên nào'}, status=404)

    mail_ok = True
    for user in users:      # 1 email có thể dùng cho nhiều tài khoản => mỗi tài khoản 1 link riêng
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        reset_url = frontend_url() + '/reset-password/' + uid + '/' + token
        if not send_reset_password_email(user, reset_url):
            mail_ok = False

    if not mail_ok:
        return Response({'error': 'Chưa gửi được mail, vui lòng thử lại sau (hoặc kiểm tra cấu hình mail)'}, status=500)
    return Response({'message': 'Đã gửi link đặt lại mật khẩu tới ' + email + '. Hãy kiểm tra hộp thư (cả mục Spam)'})


@api_view(['POST'])
def reset_password(request):
    uid = get_text(request.data, 'uid')
    token = get_text(request.data, 'token')
    password = str(request.data.get('password') or '')
    password2 = str(request.data.get('password2') or '')

    # giải mã uid ra id rồi tìm user. Link bị sửa bậy thì user = None
    try:
        user = User.objects.get(pk=urlsafe_base64_decode(uid).decode())
    except (ValueError, TypeError, OverflowError, User.DoesNotExist):
        user = None
    if user is None or not default_token_generator.check_token(user, token):
        return Response({'error': 'Link không hợp lệ hoặc đã được sử dụng'}, status=400)

    if len(password) < 6:
        return Response({'error': 'Mật khẩu phải có ít nhất 6 ký tự'}, status=400)
    if password != password2:
        return Response({'error': 'Mật khẩu nhập lại không khớp'}, status=400)

    user.set_password(password)
    user.save()
    return Response({'message': 'Đổi mật khẩu thành công, hãy đăng nhập bằng mật khẩu mới'})
