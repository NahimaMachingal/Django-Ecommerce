from django.contrib import admin
from .models import Product, ProductImage


# Register your models here.
class ProductImageInline(admin.TabularInline):  # Choose TabularInline or StackedInline for layout
    model = ProductImage
    extra = 4  # Allow adding up to 4 images by default  

class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'price', 'stock', 'category', 'modified_date', 'is_available')
    prepopulated_fields = {'slug' : ('product_name',)}
    inlines = [ProductImageInline]

admin.site.register(Product,ProductAdmin)


