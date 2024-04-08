# forms.py

from django import forms
from store.models import Product, ProductImage
from django.forms import modelformset_factory
from category.models import Category
from orders.models import Coupon

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['product_name', 'slug', 'description', 'price', 'stock', 'is_available', 'category']
        widgets = {
            'product_name': forms.TextInput(attrs={'class': 'form-control'}),
            'slug': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_available': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
        }

class ProductImageForm(forms.ModelForm):
    images = forms.FileField(widget = forms.TextInput(attrs={
            "name": "images",
            "type": "File",
            "class": "form-control",
            "multiple": "True",
        }), label = "")
    class Meta:
        model = ProductImage
        fields = ['images']
    
class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['category_name', 'slug', 'description', 'category_image']


class CouponForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
    class Meta:
        model = Coupon
        fields = ['code', 'discount', 'valid_from', 'valid_to']
        widgets = {
            'valid_from': forms.DateTimeInput(attrs={'type': 'datetime-local' , 'class': 'form-control'}),
            'valid_to': forms.DateTimeInput(attrs={'type': 'datetime-local' , 'class': 'form-control'}),
        }