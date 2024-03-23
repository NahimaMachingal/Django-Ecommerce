from django.shortcuts import render,get_object_or_404, redirect
from . models import Product, Wishlist
from category.models import Category
from django.http import Http404
from carts.views import _cart_id
from carts.models import CartItem, Variation
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import HttpResponse
from django.db.models import Q
from django.db.models import Count, Avg
from django.contrib.auth.decorators import login_required

# Create your views here.



def store(request, category_slug=None):
    categories = None
    products = None

    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category=category, is_available=True, is_active = True)
        paginator = Paginator(products, 4)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        product_count = products.count()
        
    else:
        products = Product.objects.all().filter(is_available=True, is_active = True).order_by('id')
        paginator = Paginator(products, 6)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        product_count = products.count()
    
    context = {
        'products': paged_products,
        'product_count': product_count,
               
    }
    return render(request, 'store/store.html', context)

def product_detail(request, category_slug, product_slug):
    try:
        single_product = Product.objects.get(category__slug=category_slug, slug=product_slug)
        in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request), product=single_product).exists()
    
    except Exception as e:
        raise e
    
    
    context = {
        'single_product': single_product,
        'in_cart' : in_cart,
    }
    return render(request, 'store/product_detail.html', context)

def search(request):
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            products = Product.objects.order_by('-created_date').filter(Q(description__icontains=keyword) | Q(product_name__icontains = keyword))
            product_count = products.count()

        # Sorting options
    sort_by = request.GET.get('sort_by')
    if sort_by == 'price_low_high':
        products = products.order_by('price')
    elif sort_by == 'price_high_low':
        products = products.order_by('-price')
    
    context = {
        'products' : products,
        'product_count' : product_count,
    }
    return render(request, 'store/store.html', context)

def add_wishlist(request, product_slug):
    try:
        product = Product.objects.get(slug=product_slug)
        variations = []  # Initialize an empty list to store variations

        # Get the selected variations from the request
        if request.method == "POST":
            for item in request.POST:
                if 'variation_id' in item:
                    variation_id = request.POST.get(item)
                    print(f"Variation ID: {variation_id}")
                    try:
                        variation = Variation.objects.get(id=variation_id)
                        variations.append(variation)
                    except Variation.DoesNotExist:
                        pass

        # Create the Wishlist item with the selected variations
        wishlist_item = Wishlist.objects.create(user=request.user, product=product)
        if variations:
            wishlist_item.variations.set(variations)


    except Product.DoesNotExist:
        return redirect('store')  # Redirect to home page if the product doesn't exist

    return redirect('wishlist')  # Redirect to the wishlist page after adding the product

    

def remove_from_wishlist(request, wishlist_item_id):
    wishlist_item = get_object_or_404(Wishlist, id=wishlist_item_id)
    wishlist_item.delete()
    return redirect('wishlist')

@login_required(login_url='loginn')
def wishlist(request):
    if request.method == 'POST':
        wishlist_item_id = request.POST.get('wishlist_item_id')
        if wishlist_item_id:
            wishlist_item = get_object_or_404(Wishlist, id=wishlist_item_id)
            wishlist_item.delete()
            return redirect('wishlist')

    wishlist_items = Wishlist.objects.filter(user=request.user)
    
    context = {
        'wishlist_items': wishlist_items,
        }
    return render(request, 'store/wishlist.html', context)

def product_detaill(request, product_slug):
    try:
        single_product = Product.objects.get(slug=product_slug)
        in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request), product=single_product).exists()
        
    except Exception as e:
        raise e
    
    
    context = {
        'single_product': single_product,
        'in_cart' : in_cart,
        
    }
    return render(request, 'store/product_detail.html', context)







