from django.urls import path
from . import views

urlpatterns = [
    path('blog/', views.blog_list, name='blog_list'),
    path('blog/<slug:slug>/', views.blog_detail, name='blog_detail'),
    path('blog/<slug:slug>/rate/', views.rate_blog_view, name='rate_blog'),
    path('blog/<slug:slug>/comment/', views.add_comment_ajax, name='add_comment_ajax'),
]