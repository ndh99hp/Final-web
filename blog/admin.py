from django.contrib import admin
from .models import Blog, Comment, Rate
@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'author', 'created_at')
    list_filter = ('author', 'created_at')
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'id_blog', 'name', 'id_user', 'level', 'created_at', 'parent')
    list_filter = ('id_blog', 'level')
    search_fields = ('name', 'cmt')
@admin.register(Rate)
class RateAdmin(admin.ModelAdmin):
    list_display = ('id', 'id_blog', 'id_user', 'rate', 'time')
    list_filter = ('id_blog', 'id_user')