from django.db import models

# Create your models here.

class User(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, unique=True)
    phone = models.CharField(max_length=255)
    user_status = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Category(models.Model):
    category_name = models.CharField(max_length=255,unique=True, default='Uncategorized')
    slug = models.CharField(max_length=100, unique=True, default='Uncategorized')
    description = models.TextField(max_length=255, blank=True)
    cat_image = models.ImageField(upload_to='photos/categories', blank=True)
    
    def __str__(self):
        return self.category_name
    
