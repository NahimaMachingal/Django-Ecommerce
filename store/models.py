from django.db import models
from category.models import Category
from django.urls import reverse

# Create your models here.
class Product(models.Model):
    product_name = models.CharField(max_length=255,blank=True)
    slug = models.SlugField(max_length=200, unique=True,blank=True)
    description = models.TextField(blank=True)
    price = models.IntegerField()
    images = models.ImageField(upload_to='photos/products', blank=True, null=True)
    stock = models.IntegerField()
    is_available = models.BooleanField(default=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    created_date = models.DateField(auto_now_add = True)
    modified_date = models.DateField(auto_now = True)

    def get_url(self):
        return reverse('product_detail', args=[self.category.slug, self.slug])

    def __str__(self):
        return self.product_name
    
class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="product_images")
    image = models.ImageField(upload_to='photos/products', blank=True, null=True)
    is_featured = models.BooleanField(default=False)
    order = models.PositiveIntegerField(null=True, blank=True)  # Optional for image order

    def __str__(self):
        return f"Image for {self.product.product_name}"

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["product", "image"], name="unique_product_image"),
        ]
    

