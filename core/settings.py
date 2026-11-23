"""
Cấu hình Django (Django 4.2) cho đồ án Shop: backend API (Django REST Framework) + MySQL.
Giao diện do ReactJS làm riêng, gọi API ở đường dẫn /api/...
"""

from pathlib import Path

# Đường dẫn gốc của project: BASE_DIR / 'thư_mục_con'
BASE_DIR = Path(__file__).resolve().parent.parent


# Cấu hình khi học / phát triển - không dùng khi đưa web lên chạy thật
SECRET_KEY = 'django-insecure-8(%y8#wo7&5g(2cp!+(k0cijr3w3ng-1_=56!#7%!s%%5siquq'
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
ALLOWED_HOSTS = []
# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # thư viện bên thứ 3
    'ckeditor',
    'ckeditor_uploader',
    'rest_framework',                # Bài 22: Django REST Framework
    'rest_framework.authtoken',      # Bài 23: bảng Token để đăng nhập bằng API
    'corsheaders',                   # cho phép ReactJS (cổng khác) gọi API
    # app tự tạo
    'users',
    'blog',
    'product',
    'cart',
    'api',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',      # phải đứng đầu danh sách
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],     # chỉ còn template mail trong các app (APP_DIRS)
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media',
            ],
        },
    },
]
WSGI_APPLICATION = 'core.wsgi.application'


# Database (MySQL trong XAMPP)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'shop_admin',
        'USER': 'root',
        'PASSWORD': '',
        'HOST': '127.0.0.1',
        'PORT': '3306',
    }
}


AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


LANGUAGE_CODE = 'vi'
TIME_ZONE = 'Asia/Ho_Chi_Minh'
USE_I18N = True
USE_TZ = True


STATIC_URL = 'static/'


# ===================== GỬI MAIL (theo Bài 18: Send mail - gmail) =====================
# Cách hoạt động: Django đăng nhập vào Gmail (SMTP) bằng EMAIL_HOST_USER + EMAIL_HOST_PASSWORD rồi nhờ Gmail gửi thư.
# Người nhận là email khách nhập, người gửi là Gmail khai báo ở đây.
# Cách lấy App Password: bật xác minh 2 bước tại https://myaccount.google.com/security
#   rồi tạo mật khẩu ứng dụng tại https://myaccount.google.com/apppasswords (Google cho 1 mật khẩu 16 ký tự).
# >>> Điền Gmail và App Password của bạn vào 2 dòng bên dưới (App Password KHÔNG phải mật khẩu đăng nhập Gmail).
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your_gmail@gmail.com'
EMAIL_HOST_PASSWORD = 'your_app_password'      # Phải dùng App Password
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
EMAIL_TIMEOUT = 15                             # quá 15 giây không gửi được thì báo lỗi, không để web bị treo

# Nếu chưa điền (vẫn là 'your_...') thì chỉ in mail ra cửa sổ terminal để test, web không bị lỗi
if EMAIL_HOST_USER == 'your_gmail@gmail.com' or EMAIL_HOST_PASSWORD == 'your_app_password':
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
    DEFAULT_FROM_EMAIL = 'E-Shopper <noreply@eshopper.local>'
# LƯU Ý: đừng push file này lên GitHub khi đã điền mật khẩu thật. Trước khi push hãy trả 2 dòng về 'your_gmail@gmail.com' / 'your_app_password'.

AUTH_USER_MODEL = 'users.User'
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'    # giữ kiểu khóa chính cũ (tắt cảnh báo W042)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
CKEDITOR_UPLOAD_PATH = "uploads/"
CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'full',
        'height': 300,
        'width': '100%',
    },
}

# Django REST Framework
REST_FRAMEWORK = {
    # Đăng nhập bằng token: React gửi header  Authorization: Token <key>
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    # Tiền (Decimal) trả về là số (12.5) chứ không phải chuỗi ("12.50")
    'COERCE_DECIMAL_TO_STRING': False,
}

# Địa chỉ web ReactJS được phép gọi API (CORS) - đổi lại nếu React chạy cổng khác
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'http://127.0.0.1:3000',
    'http://localhost:5173',
    'http://127.0.0.1:5173',
]

# Địa chỉ web ReactJS: dùng để tạo link trong mail "quên mật khẩu" (trang React sẽ gọi API reset-password)
FRONTEND_URL = 'http://localhost:3000'
