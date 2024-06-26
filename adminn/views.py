from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
import csv
from .forms import OrderFilterForm
from django.contrib import messages,auth
from django.db.models.functions import Coalesce
from .utils import is_ajax
from django.db.models import Sum, F, ExpressionWrapper, DecimalField
import pandas as pd  # Import Pandas library
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from accounts.models import Account
from django.forms import modelformset_factory
from django.shortcuts import get_object_or_404
from .forms import ProductForm, ProductImageForm, CouponForm, VariationForm
from store.models import Product, ProductImage,Variation
from .forms import CategoryForm
from orders.models import Order, Coupon, OrderProduct
from django.db.models import Sum, Count, F
from django.db.models.functions import ExtractWeek, ExtractMonth
from category.models import Category
from reportlab.pdfgen import canvas
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest
from django.utils import timezone
from datetime import timedelta, datetime
from django.db.models import Sum, Q
from datetime import timedelta, date
from django.http import HttpResponseRedirect, JsonResponse
from django.utils import timezone
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import openpyxl
from django.contrib.auth.decorators import user_passes_test
from reportlab.pdfgen import canvas


# Create your views here.

def superuser_required(view_func):
    """
    Decorator for views that checks if the user is a superuser,
    redirects to the dashboard if not.
    """
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_superadmin:
            return view_func(request, *args, **kwargs)
        else:
            return redirect('loginn')  # Redirect to the dashboard or any other page
    return _wrapped_view

def user_view(request):
    return render(request, 'customer/home.html')

@superuser_required
def adminhome(request):
    # Render your custom admin panel homepage template
    return render(request, 'adminn/adminhome.html')  

@superuser_required
def users(request):
    # Fetch account objects from the database
    accounts = Account.objects.all()  # You can filter or order the queryset as needed
    
    # Pass the accounts queryset to the template context
    context = {'accounts': accounts}
    
    # Render the template with the context
    return render(request, 'adminn/users.html', context)

@superuser_required
def signout(request):
    auth.logout(request)
    messages.success(request, "you are logged out")
    return redirect('loginn')


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

@superuser_required
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
    image_form = ProductImageForm()
    
    if request.method == "POST":
        form = ProductForm(request.POST, instance=product)
        image_form = ProductImageForm(request.POST, request.FILES)
        if form.is_valid() and image_form.is_valid():
            form.save()
            if 'images' in request.FILES:
                for image in request.FILES.getlist('images'):
                    ProductImage.objects.create(product=product, image=image)
            messages.success(request, "Product edited successfully")
            return redirect("adminn:productlist")
        else:
            messages.error(request, "Error editing product. Please check the form.")
    else:
        # This ensures existing images can be seen and edited
        image_form = ProductImageForm(initial={'images': product.images.all()})
    # Fetch existing images and pass them to the template
    existing_images = product.images.all()
    return render(request, "adminn/editproduct.html", {"form": form, "image_form": image_form, "existing_images": existing_images })

@superuser_required
def addvariation(request):
    if request.method == 'POST':
        form = VariationForm(request.POST)
        if form.is_valid():
            variation = form.save(commit=False)
            variation.save()
            return redirect('adminn:variationlist')  # Redirect to the variation list page
    else:
        form = VariationForm()
    return render(request, 'adminn/addvariation.html', {'form': form})

@superuser_required
def variationlist(request):
    variations = Variation.objects.all()
    return render(request, 'adminn/variationlist.html', {'variations': variations})

@superuser_required
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


@superuser_required
def orderlist(request):
    orders = Order.objects.all().order_by('-created_at')  # Orders sorted by created_at field in descending order
    return render(request, 'adminn/orderlist.html', {'orders': orders})

def cancelorder(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order.is_ordered = False
    order.status = 'Cancelled'
    order.save()
    return redirect('adminn:orderlist')

def process_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order.is_ordered = False
    order.status = 'processing'
    order.save()
    messages.success(request, 'Order status has been updated to Processing.')
    return redirect('adminn:orderlist')  # Redirect to the order detail page or another appropriate page

def ship_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order.is_ordered = False
    order.status = 'Shipped'
    order.save()
    messages.success(request, 'Order status has been updated to Shipped.')
    return redirect('adminn:orderlist')  # Redirect to the order detail page or another appropriate page

def deliver_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order.is_ordered = False
    order.status = 'Delivered'
    order.save()
    messages.success(request, 'Order status has been updated to Delivered.')
    return redirect('adminn:orderlist')  # Redirect to the order detail page or another appropriate page

def order_detaill(request, order_id):
    order_detail = OrderProduct.objects.filter(order__order_number = order_id)
    order = Order.objects.get(order_number = order_id)
    subtotal = 0
    for i in order_detail:
        product = Product.objects.get(id=i.product_id)  # Retrieve the product
        subtotal += product.price_after_discount() * i.quantity  # Calculate subtotal using price_after_discount

    # Fetching payment method from the related Payment object
    payment_method = order.payment.payment_method if order.payment else None

    context = {
        'order_detail' : order_detail,
        'order' : order,
        'subtotal' : subtotal,
        'payment': order.payment,
        'payment_method': payment_method,
        
    }
    

    return render(request, 'adminn/order_detaill.html', context)

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

@superuser_required
def coupon(request):
    coupons = Coupon.objects.all()
    return render(request, 'adminn/coupon.html', {'coupons': coupons})

def add_coupon(request):
    if request.method == 'POST':
        form = CouponForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('adminn:coupon')  # Redirect to the coupon list page after successful addition
    else:
        form = CouponForm()
    return render(request, 'adminn/add_coupon.html', {'form': form})

@superuser_required
def delete_coupon(request, coupon_id):
    coupon = get_object_or_404(Coupon, id=coupon_id)
    coupon.delete()
    return redirect('adminn:coupon')

def generate_sales_report_data(start_date=None, end_date=None):
    
    orders = Order.objects.none()
    droporders = Order.objects.none()
    
    if start_date and end_date:
        if isinstance(start_date, str):  # Check if start_date is a string
            start_date = timezone.datetime.strptime(start_date, "%Y-%m-%d").date()
        if isinstance(end_date, str):    # Check if end_date is a string
            end_date = timezone.datetime.strptime(end_date, "%Y-%m-%d").date()
        
        print(start_date)
        print(end_date)
        orders = Order.objects.filter(created_at__date__range=[start_date, end_date])
        droporders = Order.objects.filter(Q(status='Returned') | Q(status='Cancelled'), created_at__date__range=[start_date, end_date])

    total_sales = round(orders.aggregate(total_sales=Sum('final_total'))['total_sales'] or 0, 2)
    total_drop_sales = round(droporders.aggregate(total_drop_sales=Sum('final_total'))['total_drop_sales'] or 0, 2)
    # Calculate total discount
    total_discount = round(orders.annotate(
    discount_per_product=ExpressionWrapper(
        F('orderproduct__product__price') - Coalesce(F('orderproduct__product__price') * F('orderproduct__product__discount') / 100, 0),
        output_field=DecimalField(max_digits=10, decimal_places=2)
    )
).aggregate(total_discount=Sum('discount_per_product'))['total_discount'] or 0, 2)
    # Calculate total coupons by summing the coupon discounts applied to orders with coupon_discount > 0
    # Calculate total coupons by summing the discount applied using coupons
    # Calculate total coupons with coupon_discount > 0
    total_coupons = orders.filter(~Q(coupon=None)).annotate(
        coupon_discount=ExpressionWrapper(
            F('orderproduct__product__price') * F('orderproduct__product__discount') / 100,
            output_field=DecimalField(max_digits=10, decimal_places=2)
        )
    ).filter(coupon_discount__gt=0).values('coupon').distinct().count()
    net_sales = round(total_sales - total_coupons - total_drop_sales, 2)
    
    print("Total Sales:", total_sales)
    print("Total Drop Sales:", total_drop_sales)
    print("Total Discount:", total_discount)
    print("Total Coupons:", total_coupons)
    print("Net Sales:", net_sales)
    
    return {
        'start_date': start_date,
        'end_date': end_date,
        'total_sales': total_sales,
        'total_discount': total_discount,
        'total_coupons': total_coupons,
        'net_sales': net_sales,
        'orders': orders,
        'total_drop_sales': total_drop_sales
    } or {}  # Return an empty dictionary if no data found

def sales_report(request):
    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        date_range = request.POST.get('date_range')

        if date_range:
            if date_range == '1day':
                start_date = end_date
            elif date_range == '1week':
                start_date = (timezone.now() - timedelta(days=7)).date()
            elif date_range == '1month':
                start_date = (timezone.now() - timedelta(days=30)).date()

        try:
            # Convert start_date and end_date to date objects if they are strings
            if isinstance(start_date, str):
                start_date = timezone.datetime.strptime(start_date, "%Y-%m-%d").date()
            if isinstance(end_date, str):
                end_date = timezone.datetime.strptime(end_date, "%Y-%m-%d").date()
                
            context = generate_sales_report_data(start_date, end_date)
            context['start_date'] = start_date  # Add start_date to context
            context['end_date'] = end_date      # Add end_date to context
            return render(request, 'adminn/sales_report.html', context)
        except ValueError as e:
            return HttpResponseBadRequest(str(e))
    else:
        context = generate_sales_report_data()
        return render(request, 'adminn/sales_report.html', context)
        
def render_sales_report_excel(report_data):
    # Extract data from report_data
    start_date = report_data['start_date']
    end_date = report_data['end_date']
    total_sales = report_data['total_sales']
    total_discount = report_data['total_discount']
    total_coupons = report_data['total_coupons']
    net_sales = report_data['net_sales']
    orders = report_data['orders']
    total_drop_sales = report_data['total_drop_sales']

    # Create lists to store data
    order_ids = []
    customer_names = []
    total_amounts = []
    quantities = []
    coupons = []
    statuses = []
   


    # Iterate through orders to fetch relevant data
    for order in orders:
        order_ids.append(order.id)
        customer_names.append(order.user.full_name())
        total_amounts.append(order.final_total)
        # Fetch quantity from related OrderProduct instances
        quantities.append(sum(op.quantity for op in order.orderproduct_set.all()))
        coupons.append(order.coupon)
        statuses.append(order.status)
       
    
    # Create a DataFrame with the sales data
    sales_df = pd.DataFrame({
        'Order ID': order_ids,
        'Customer Name': customer_names,
        'Total Amount': total_amounts,
        'Quantity': quantities,
        'Coupon': coupons,
        'Status': statuses,
        
    })


    # Create an Excel writer object
    excel_file_path = f'sales_report_{start_date}_{end_date}.xlsx'
    excel_writer = pd.ExcelWriter(excel_file_path, engine='openpyxl')

    # Write the DataFrame to an Excel sheet
    sales_df.to_excel(excel_writer, sheet_name='Sales Report', index=False)

    # Add summary statistics to another sheet
    summary_df = pd.DataFrame({
        'Total Sales': [total_sales],
        'Total Discount': [total_discount],
        'Total Coupons': [total_coupons],
        'Net Sales': [net_sales],
        'Total Drop Sales': [total_drop_sales]
    })
    summary_df.to_excel(excel_writer, sheet_name='Summary', index=False)

    # Close the Excel writer object
    excel_writer.close()

    return excel_file_path


def download_sales_reportpdf(request):
    start_date = request.GET.get('start_date')  # Get start_date from request
    end_date = request.GET.get('end_date')      # Get end_date from request
    # Convert start_date and end_date to date objects if they are strings
    start_date = timezone.datetime.strptime(start_date, "%Y-%m-%d").date()
    end_date = timezone.datetime.strptime(end_date, "%Y-%m-%d").date()
    
    report_data = generate_sales_report_data(start_date=start_date, end_date=end_date)
    pdf_data = render_to_string('adminn/sales_report.html', report_data)  # Render PDF template with report_data
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="sales_report_{start_date}_{end_date}.pdf"'
    pisa.CreatePDF(pdf_data, dest=response)
    return response


def download_sales_reportexcel(request):
    report_data = generate_sales_report_data(request.GET.get('start_date'), request.GET.get('end_date'))
    excel_file_path = render_sales_report_excel(report_data)

    # Open the Excel file and read its content
    with open(excel_file_path, 'rb') as excel_file:
        file_content = excel_file.read()

    # Create an HttpResponse object with the Excel file content
    response = HttpResponse(file_content, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="sales_report_{report_data["start_date"]}_{report_data["end_date"]}.xlsx"'

    return response



@superuser_required
def custom_admin_homepage(request):
    filter_period = 'yearly'
    today = timezone.now().date()

    if request.method == 'POST':
        # Check if the 'period' parameter exists in the POST data
        if 'period' in request.POST:
            filter_period = request.POST['period']
        
    start_date, end_date = calculate_date_range(filter_period, today)

    sales_report_data = generate_sales_report_data(start_date, end_date)

    if sales_report_data:
        total_sales = sales_report_data['total_sales']
        total_drop_sales = sales_report_data['total_drop_sales']
        total_discount = sales_report_data['total_discount']
        total_coupons = sales_report_data['total_coupons']
        net_sales = sales_report_data['net_sales']
        orders = sales_report_data['orders']

        top_products = OrderProduct.objects.filter(order__created_at__date__range=[start_date, end_date]).values('product__product_name').annotate(total_sales=Sum('product_price')).order_by('-total_sales')[:10]

        top_categories = OrderProduct.objects.filter(order__created_at__date__range=[start_date, end_date]).values('product__category__category_name').annotate(total_sales=Sum('product_price')).order_by('-total_sales')[:10]

    return render(request, 'adminn/custom_admin_homepage.html', {
        'total_sales': total_sales,
        'total_drop_sales': total_drop_sales,
        'total_discount': total_discount,
        'total_coupons': total_coupons,
        'net_sales': net_sales,
        'orders': orders,
        'filter_period': filter_period,
        'top_products': top_products,
        'top_categories': top_categories,
    })
    
def calculate_date_range(filter_period, today):
    start_date = end_date = today  # Default values
    
    if filter_period == 'weekly':
        start_date = today - timedelta(days=7)
    elif filter_period == 'monthly':
        start_date = today.replace(day=1)
    elif filter_period == 'yearly':
        start_date = today.replace(day=1, month=1)
    else:
        raise ValueError("Invalid filter period")
    
    return start_date, end_date
