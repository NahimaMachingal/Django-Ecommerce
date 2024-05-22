from django.shortcuts import render,get_object_or_404, redirect
from . models import Product, Wishlist, ReviewRating
from category.models import Category
from orders.models import OrderProduct
from .forms import ReviewForm
from django.urls import reverse
from django.contrib import messages
from django.db.models import Sum
from django.http import Http404
from carts.views import _cart_id
from carts.models import CartItem, Variation
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import HttpResponse
from django.db.models import Q
from django.http import HttpResponseRedirect
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
    single_product = None  # Initialize single_product as None
    if request.user.is_authenticated:  # Check if the user is authenticated
        try:
            single_product = Product.objects.get(category__slug=category_slug, slug=product_slug)
            in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request), product=single_product).exists()
            in_wishlist = Wishlist.objects.filter(user=request.user, product=single_product).exists()
        except Exception as e:
            raise e
    else:
        in_wishlist = None
    
    orderproduct = None  # Initialize orderproduct as None
    if request.user.is_authenticated:  # Check if the user is authenticated
        try:
            orderproduct = OrderProduct.objects.filter(user=request.user, product_id=single_product.id).exists()
        except OrderProduct.DoesNotExist:
            pass
    else:
        orderproduct = None

    
    # Get the reviews if single_product is not None
    reviews = []
    if single_product:

    #Get the reviews

        reviews = ReviewRating.objects.filter(product_id=single_product.id, status=True)

    
    
    
    context = {
        'single_product': single_product,
        'in_cart' : in_cart if single_product else False,
        'orderproduct' : orderproduct if single_product else False,
        'in_wishlist': in_wishlist,
        'reviews' : reviews,
        
    }
    return render(request, 'store/product_detail.html', context)

def search(request):
    keyword = request.GET.get('keyword', None)
    products = Product.objects.all()
    product_count = products.count()  # Initialize product_count

    if keyword:
        products = products.filter(Q(description__icontains=keyword) | Q(product_name__icontains=keyword))
        product_count = products.count()

        # Sorting options
    sort_by = request.GET.get('sort_by')
    if sort_by == 'price_low_high':
        products = products.order_by('price')
    elif sort_by == 'price_high_low':
        products = products.order_by('-price')
    elif sort_by == 'name_a_to_z':
        products = products.order_by('product_name')
    elif sort_by == 'name_z_to_a':
        products = products.order_by('-product_name')
    
    context = {
        'products' : products,
        'product_count' : product_count,
    }
    return render(request, 'store/store.html', context)

@login_required(login_url='loginn')
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


        # Check if the product is already in the cart
        is_in_cart = CartItem.objects.filter(product=product, user=request.user).exists()
       
        if is_in_cart:
            # If the product is already in the cart, remove it from the wishlist
            Wishlist.objects.filter(user=request.user, product=product).delete()
        else:
            # If the product is not in the cart, add it to the wishlist
            wishlist_item = Wishlist.objects.create(user=request.user, product=product)
            if variations:
                wishlist_item.variations.set(variations)




    except Product.DoesNotExist:
        return redirect('store')  # Redirect to home page if the product doesn't exist
   
    # Redirect to the previous page
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


    

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


    # Get the slug of the current product from the request or session
    current_product_slug = request.GET.get('product_slug', None)




    

# Check if any product in the wishlist matches the current product
    in_wishlist = wishlist_items.filter(product__slug=current_product_slug).exists()


    context = {
        'wishlist_items': wishlist_items,
        'in_wishlist': in_wishlist,  # Pass the in_wishlist variable to the template
        }
    return render(request, 'store/wishlist.html', context)




def product_detaill(request, product_slug):
    try:
        single_product = Product.objects.get(slug=product_slug)
        in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request), product=single_product).exists()
        in_wishlist = Wishlist.objects.filter(user=request.user, product=single_product).exists()
        
    except Exception as e:
        raise e
    
    
    context = {
        'single_product': single_product,
        'in_cart' : in_cart,
        'in_wishlist': in_wishlist,
        
    }
    return render(request, 'store/product_detail.html', context)


def submit_review(request, product_id):
    url = request.META.get('HTTP_REFERER')
    if request.method == "POST":
        try:
            reviews = ReviewRating.objects.get(user__id = request.user.id, product__id = product_id)
            form = ReviewForm(request.POST, instance=reviews)
            form.save()
            messages.success(request, 'Thank you! Your review has been updated.')
            return redirect(url)

        except ReviewRating.DoesNotExist:
            form = ReviewForm(request.POST)
            if form.is_valid():
                data = ReviewRating()
                data.subject = form.cleaned_data['subject']
                data.rating = form.cleaned_data['rating']
                data.review = form.cleaned_data['review']
                data.ip = request.META.get('REMOTE_ADDR')
                data.product_id = product_id
                data.user_id = request.user.id
                data.save()
                messages.success(request, 'Thank you! Your review has been Submitted.')
                return redirect(url)


        








