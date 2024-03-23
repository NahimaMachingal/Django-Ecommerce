from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
import csv
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from accounts.models import Account
from django.forms import modelformset_factory
from django.shortcuts import get_object_or_404
from .forms import ProductForm, ProductImageForm, CouponForm
from store.models import Product, ProductImage
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
from reportlab.pdfgen import canvas


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

def cancelorder(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order.is_ordered = False
    order.status = 'Cancelled'
    order.save()
    return redirect('adminn:orderlist')

def order_detaill(request, order_id):
    order_detail = OrderProduct.objects.filter(order__order_number = order_id)
    order = Order.objects.get(order_number = order_id)
    subtotal = 0
    for i in order_detail:
        subtotal += i.product_price * i.quantity

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

def generate_sales_report_data(start_date=None, end_date=None):
    today = timezone.now().date()
    orders = Order.objects.none()
    droporders = Order.objects.none()
    
    if start_date and end_date:
        
        print(start_date)
        print(end_date)
        orders = Order.objects.filter(created_at__date__range=[start_date, end_date])
        droporders = Order.objects.filter(Q(status='Returned') | Q(status='Cancelled'), created_at__date__range=[start_date, end_date])

    total_sales = round(orders.aggregate(total_sales=Sum('final_total'))['total_sales'] or 0, 2)
    total_drop_sales = round(droporders.aggregate(total_drop_sales=Sum('final_total'))['total_drop_sales'] or 0, 2)
    total_discount = round(total_sales - total_drop_sales, 2)
    total_coupons = orders.aggregate(total_coupons=Count('coupon'))['total_coupons'] or 0
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
    }

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
            context = generate_sales_report_data(start_date, end_date)
            return render(request, 'adminn/sales_report.html', context)
        except ValueError as e:
            return HttpResponseBadRequest(str(e))
    else:
        context = generate_sales_report_data()
        return render(request, 'adminn/sales_report.html', context)
        
    
def render_sales_report_pdf(report_data):
    # Render HTML template with report_data
    html = render_to_string('sales_report_pdf.html', report_data)

    # Create HttpResponse object with PDF content type
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="sales_report.pdf"'

    # Generate PDF file from HTML content and attach it to the response
    pisa.CreatePDF(html, dest=response)

    return response

def render_sales_report_excel(report_data):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="sales_report.xls"'
    writer = csv.writer(response)
    writer.writerow(['Order ID', 'Customer', 'Total Value', 'Discount',
    'Net Value', 'Created At'])
    for order in report_data['orders']:
        writer.writerow([
            order.id,
            order.user.get_full_name(),
            order.original_total_value,
            order.discounted_total,
            order.created_at
    ])
    return response

def download_sales_report_pdf(request, period=None):
    if request.method == 'POST':
        # If the request method is POST, retrieve period, start_date, and end_date from POST parameters
        period = request.POST.get('period')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        print(start_date)
        print(end_date)
    else:
        # If the request method is not POST, retrieve start_date and end_date from GET parameters
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        print(start_date)
        print(end_date)

    # Validate if both start_date and end_date are provided for custom period
    if period == 'custom' and (not start_date or not end_date):
        return HttpResponseBadRequest('Missing start_date or end_date parameters for custom period')

    # Generate report data based on the period and dates
    report_data = generate_sales_report_data(period, start_date, end_date)

    # Debug print statements for start_date and end_date
    print("Start Date:", start_date)
    print("End Date:", end_date)

    # Check if period parameter is missing in report_data
    if not report_data.get('period'):
        return HttpResponseBadRequest('Missing period parameter in report data')

    # Render the PDF report using the generated data
    return render_sales_report_pdf(report_data)

def sales_report_excel(request, period=None):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    report_data = generate_sales_report_data(period, start_date, end_date)
    return render_sales_report_excel(report_data)