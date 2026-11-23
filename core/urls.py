# core/urls.py: backend chỉ còn trang quản trị Django (/admin/), API (/api/) và file media.
# Giao diện (HTML/CSS/JS) do ReactJS làm, gọi API ở đường dẫn /api/...
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('ckeditor/', include('ckeditor_uploader.urls')),
    path('api/', include('api.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
