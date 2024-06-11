# forms.py

from django import forms
from store.models import Product, ProductImage, Variation
from django.forms import modelformset_factory
from django.core.validators import MinValueValidator, MaxValueValidator
from category.models import Category
from orders.models import Coupon

class ProductForm(forms.ModelForm):
    discount = forms.DecimalField(
        label='Discount',
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    class Meta:
        model = Product
        fields = ['product_name', 'slug', 'description', 'price', 'discount', 'stock', 'is_available', 'category']
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
    category_discount = forms.DecimalField(
        label='Category_Discount',
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    class Meta:
        model = Category
        fields = ['category_name', 'slug', 'description', 'category_image', 'category_discount']

variation_category_choice = (
    ('color', 'Color'),
    ('size', 'Size'),
)


class VariationForm(forms.ModelForm):
    product = forms.ModelChoiceField(
        queryset=Product.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    variation_category = forms.ChoiceField(
        choices=variation_category_choice,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    variation_value = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    is_active = forms.BooleanField(
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )


    class Meta:
        model = Variation
        fields = ['product', 'variation_category', 'variation_value', 'is_active']
        widgets = {
            'created_at': forms.DateTimeInput(attrs={'type': 'hidden'}),
        }

    def _init_(self, *args, **kwargs):
        super()._init_(*args, **kwargs)
        self.fields['variation_value'].widget.attrs.update({'class': 'form-control'})

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


class OrderFilterForm(forms.Form):
    STATUS_CHOICES = (
        ('', 'All'),  # Include an option to show all orders
        ('New', 'New'),
        ('Accepted', 'Accepted'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
        ('Delivered', 'Delivered'),
        ('Returned', 'Returned'),
    )
    status = forms.ChoiceField(choices=STATUS_CHOICES, required=False)
