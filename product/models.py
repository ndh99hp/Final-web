from django.db import models
from django.contrib.auth.models import User
from users.models import User#bảng user 
class Product(models.Model):
    #name cua spham
    title = models.CharField(max_length=255)
    #price spham
    price = models.DecimalField(max_digits=10, decimal_places=2)
    #img
    image = models.ImageField(upload_to='products/')
    #tgia spam
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    #auto save time
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.title