'''from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Product
from .forms import ProductForm

# Create your views here.

def user_view(request):
    return render(request, 'customer/home.html')

def home_view(request):
    # Render your custom admin panel homepage template
    return render(request, 'admin/adminhome.html')  # Adjust path if needed

def product_list(request):
    # Retrieve all products from the database
    products = Product.objects.all()

    # Pass the products queryset to the template context
    context = {'products': products}
    
    # Render the product_list.html template with the context data
    return render(request, 'admin/product_list.html', context)



def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('product_list')  # Redirect to the product list page
    else:
        form = ProductForm()
    return render(request, 'admin/add_product.html', {'form': form})
'''
