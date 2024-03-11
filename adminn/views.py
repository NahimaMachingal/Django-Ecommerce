from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from django.contrib import messages
from accounts.models import Account
from django.forms import modelformset_factory
from django.shortcuts import get_object_or_404
from .forms import ProductForm, ProductImageForm
from store.models import Product, ProductImage
from .forms import CategoryForm
from orders.models import Order
from category.models import Category


# Create your views here.

def user_view(request):
    return render(request, 'customer/home.html')

def adminhome(request):
    # Render your custom admin panel homepage template
    return render(request, 'adminn/adminhome.html')  

def users(request):
    # Fetch account objects from the database
    accounts = Account.objects.all()  # You can filter or order the queryset as needed
    
    # Pass the accounts queryset to the template context
    context = {'accounts': accounts}
    
    # Render the template with the context
    return render(request, 'adminn/users.html', context)


def addproduct(request):
    productform = ProductForm()
    imageform = ProductImageForm()
    
    if request.method == 'POST':
        
        files = request.FILES.getlist('images')
        
        productform = ProductForm(request.POST, request.FILES)
        if productform.is_valid():
            product = productform.save(commit=False)
           
            product.save()
            print(request, "Product created successfully")
            
            for file in files:
                ProductImage.objects.create(product=product, image=file)
            
            return redirect("adminn:productlist")
    
    context = {"form": productform, "form_image": imageform}
    return render(request, "adminn/addproduct.html", context)

def productlist(request):
    products = Product.objects.all()
    return render(request, 'adminn/productlist.html', {'products': products})

def deleteproduct(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product.is_active = False
    product.save()
    return redirect('adminn:productlist')

def editproduct(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    form = ProductForm(instance=product)
    
    if request.method == "POST":
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, "Product edited successfully")
            return redirect("adminn:productlist")
        else:
            messages.error(request, "Error editing product. Please check the form.")
    
    return render(request, "adminn/editproduct.html", {"form": form})


def categorylist(request):
    categories = Category.objects.all()
    return render(request, 'adminn/categorylist.html', {'categories': categories})

def addcategory(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('adminn:categorylist')
    else:
        form = CategoryForm()
    return render(request, 'adminn/addcategory.html', {'form': form})

def editcategory(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES, instance=category)
        if form.is_valid():
            form.save()
            return redirect('adminn:categorylist')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'adminn/editcategory.html', {'form': form})

def deletecategory(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    # Soft delete all products associated with the category
    products_to_delete = Product.objects.filter(category=category)
    products_to_delete.update(is_active=False)
    
    # Deactivate the category
    category.is_active = False
    category.save()# Update the 'is_active' field to False instead of deleting
    return redirect('adminn:categorylist')

def orderlist(request):
    orders = Order.objects.all()
    return render(request, 'adminn/orderlist.html', {'orders': orders})

def deleteorder(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order.is_ordered = False
    order.save()
    return redirect('adminn:orderlist')

def blockuser(request, user_id):
    # Retrieve the user object by its id
    account = Account.objects.get(id=user_id)
    
    # Block the user (set is_active to False)
    account.is_active = False
    account.save()
    
    # Redirect back to the user list page or any other appropriate page
    return redirect('adminn:users')  

def unblockuser(request, user_id):
    # Retrieve the user object by its id
    account = Account.objects.get(id=user_id)
    
    # Unblock the user (set is_active to True)
    account.is_active = True
    account.save()
    
    # Redirect back to the user list page or any other appropriate page
    return redirect('adminn:users') 