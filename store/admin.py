from django.contrib import admin
from .models import Product, ProductImage, Variation, Wishlist


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
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'added_date')  # Display these fields in the admin list
    list_filter = ('user', 'added_date')  # Add filters for these fields
    search_fields = ['user__username', 'product__product_name']  # Add search functionality for related fields

admin.site.register(Wishlist, WishlistAdmin)

#admin.site.register(Product,ProductAdmin)
admin.site.register(Product)
admin.site.register(ProductImage)
admin.site.register(Variation, VariationAdmin)


