from django.contrib import admin
from .models import Product, ProductImage, Variation


# Register your models here.
#class ProductImageInline(admin.TabularInline):  # Choose TabularInline or StackedInline for layout
   # model = ProductImage
   # extra = 4  # Allow adding up to 4 images by default  

class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'price', 'stock', 'category', 'modified_date', 'is_available')
    prepopulated_fields = {'slug' : ('product_name',)}
    #inlines = [ProductImageInline]

class VariationAdmin(admin.ModelAdmin):
    list_display = ('product', 'variation_category', 'variation_value', 'is_active')
    list_editable = ('is_active',)
    list_filter = ('product', 'variation_category', 'variation_value',)

#admin.site.register(Product,ProductAdmin)
admin.site.register(Product)
admin.site.register(ProductImage)
admin.site.register(Variation, VariationAdmin)


