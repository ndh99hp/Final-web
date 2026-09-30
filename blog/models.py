from django.db import models
from django.conf import settings
from ckeditor_uploader.fields import RichTextUploadingField
class Blog(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    content = RichTextUploadingField()
    image = models.ImageField(upload_to='blogs/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='blogs'
    )
    def __str__(self):
        return self.title
class Comment(models.Model):
    id_blog = models.ForeignKey(
        Blog,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    id_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='comments'
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies'
    )
    name = models.CharField(max_length=100)
    cmt = models.TextField()
    avatar = models.ImageField(upload_to='comment_avatars/', null=True, blank=True)
    level = models.IntegerField(default=0)  # 0 = comment gốc, >0 = reply lồng nhau
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.name} - {self.cmt[:30]}"
class Rate(models.Model):
    id_blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name='rates')
    id_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rate = models.PositiveSmallIntegerField()
    time = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('id_blog', 'id_user')

    def __str__(self):
        return f"{self.id_user} - {self.id_blog} - {self.rate} sao"