from django.shortcuts import render,redirect, get_object_or_404
from . forms import RegistrationForm, AddressForm
from . models import Account, UserProfile, Address, Wallet
from orders.models import Coupon
import io
from django.db.models import Prefetch
from store.models import Product, Variation
from reportlab.pdfgen import canvas
from django.template.loader import render_to_string
import pdfkit  # You need to install the pdfkit library
from django.template.loader import get_template
from decimal import Decimal
from django.http import FileResponse
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
from orders.models import Order
from django.contrib import messages,auth
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.utils import timezone
from xhtml2pdf import pisa
from datetime import timedelta
from django.urls import reverse
from django.http import request
from .utils import generate_otp, send_otp
from carts.views import _cart_id
from orders.models import OrderProduct
from django.core.exceptions import ObjectDoesNotExist
from carts.models import Cart, CartItem
from twilio.base.exceptions import TwilioRestException
import requests



#verification email
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from django.conf import settings
from twilio.rest import Client
import random




# Create your views here.


def register(request):
    if request.method == 'POST':
        form=RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            phone_number = form.cleaned_data['phone_number']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            username=email.split("@")[0]           

            user = Account.objects.create_user(first_name=first_name, last_name=last_name, email=email, username=username, password=password)
            user.phone_number = phone_number
            user.username = user.email.split('@')[0]  # Use email as username
            user.save()

            # Generate OTP and send it to the provided phone number
            otp = generate_otp()
            send_otp(phone_number, otp)
            request.session['otp'] = otp

            # user activation
            current_site = get_current_site(request)
            mail_subject = 'Please activate your account'
            message = render_to_string('accounts/account_verification_email.html', {
                'user' : user,
                'domain' : current_site,
                'uid' : urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user)
            })
            to_email = user.email 
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()
            # Redirect to OTP verification page
            #return redirect(reverse('verify_otp'))
            messages.success(request, 'Thank you for Registering with us, we have sent you verification email to your email address. Please verify it')
            return redirect(reverse('loginn')+'?command=verification&email='+email)
    else:
        form = RegistrationForm()
    context = {
        'form' : form,

        }
    return render(request, 'accounts/register.html', context)

def loginn(request):
    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']
        user = auth.authenticate(email=email, password=password)
        if user is not None:
            try:
                cart = Cart.objects.get(cart_id=_cart_id(request))
                is_cart_item_exists = CartItem.objects.filter(cart=cart).exists()
                if is_cart_item_exists:
                    cart_item = CartItem.objects.filter(cart=cart) 

                    # getting the product variations by cart id
                    product_variation = []
                    for item in cart_item:
                        variation = item.variations.all()
                        product_variation.append(list(variation))

                    #Get the cart items from the user to access his product variation
                    cart_item = CartItem.objects.filter(user=user)
                    ex_var_list = []
                    id = []
                    for item in cart_item:
                        existing_variation = item.variations.all()
                        ex_var_list.append(list(existing_variation))
                        id.append(item.id)

                    #product_variation = [1, 2, 3, 4, 6]
                    #ex_var_list = [4, 6, 3, 5]
                    for pr in product_variation:
                        if pr in ex_var_list:
                            index = ex_var_list.index(pr)
                            item_id = id[index]
                            item = CartItem.objects.get(id=item_id)
                            item.quantity += 1
                            item.user = user
                            item.save()
                        else:
                            cart_item = CartItem.objects.filter(cart=cart)
                            for item in cart_item:
                                item.user = user
                                item.save()

            except:
                pass

            auth.login(request, user)
            #messages.success(request, 'You are now logged in')
            if user.is_superadmin:
                # Redirect superuser to admin home 
                return redirect('adminn:adminhome')
            else:
                # Redirect regular user to user home
                messages.success(request, 'You are now logged in')
                url = request.META.get('HTTP_REFERER')
                try:
                    query = requests.utils.urlparse(url).query
                    #next=/cart/checkout/
                    params = dict(x.split('=') for x in query.split('&'))
                    if 'next' in params:
                        nextPage = params['next']
                        return redirect(nextPage)
                    
                except:
                    return redirect('dashboard')
        else:
            messages.error(request, "Invalid Login Credentials")
            return redirect('loginn')
    return render(request, 'accounts/loginn.html')

def send_otp_via_twilio(phone_number, otp):
    try:
        send_otp(phone_number, otp)
        messages.success(request, 'OTP sent successfully')
    except Exception as e:
        messages.error(request, f'Error sending OTP: {str(e)}')

    


def verify_otp(request):
    if request.method == "POST":
        otp_entered = request.POST.get('otp')
        otp_saved = request.session.get('otp')
        if otp_entered == otp_saved:
            # Successful OTP verification, you can proceed with further actions
            # For example, you can authenticate the user here
            # Clear OTP from session after successful verification
            del request.session['otp']
            return redirect('user_home')  # Redirect to user home after successful verification
        else:
            # Invalid OTP, show error message or redirect back to OTP entry page
            return render(request, 'accounts/verify_otp.html', {'error': 'Invalid OTP. Please try again.'})
    # If request method is not POST, render the OTP verification page
    return render(request, 'accounts/verify_otp.html')

@login_required(login_url = 'loginn')
def logout(request):
    auth.logout(request)
    messages.success(request, "you are logged out")
    return redirect('loginn')

def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Congratulations! Your account is activated')
        return redirect('loginn')
    else:
        messages.error(request, 'Invalid activation link')
        return redirect('register')
   
@login_required(login_url = 'loginn')  
def dashboard(request):
    orders = Order.objects.order_by('-created_at').filter(user_id=request.user.id).exclude(status='New')
    orders_count = orders.count()
    user_full_name = request.user.full_name()  # Corrected this line

    context = {
        'orders_count' : orders_count,
        'user_full_name': user_full_name,
        'user': request.user,

    }

    
    return render(request, 'accounts/dashboard.html', context)

@login_required(login_url='loginn')
def user_wallet(request):
    try:
        wallet = Wallet.objects.get(account=request.user)
    except ObjectDoesNotExist:
        # If wallet doesn't exist, create a new one for the user
        wallet = Wallet.objects.create(account=request.user, wallet_balance=0.00)
    
    # Fetching orders with payment method 'Wallet'
    orders_wallet = Order.objects.filter(user=request.user, payment__payment_method='Wallet').order_by('-created_at')
    
    return render(request, 'accounts/user_wallet.html', {'wallet': wallet, 'orders_wallet': orders_wallet})


@login_required(login_url = 'loginn')
def forgotpassword(request):
    if request.method == "POST":
        email = request.POST['email']
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__exact=email)

            # reset password email
            current_site = get_current_site(request)
            mail_subject = 'Please reset your Password'
            message = render_to_string('accounts/reset_password_email.html', {
                'user' : user,
                'domain' : current_site,
                'uid' : urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user)
            })
            to_email = email 
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()

            messages.success(request, 'Password reset email has been sent to your email address')
            return redirect('loginn')

        else:
            messages.error(request, 'Account does not exist')
            return redirect('forgotpassword')
    return render(request,'accounts/forgotpassword.html')

def resetpassword_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.success(request, 'Please reset your Password')
        return redirect('resetpassword')
    else:
        messages.error(request, "This link has been expired!")
        return redirect('loginn')

def resetpassword(request):
    if request.method == "POST":
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        if password == confirm_password:
            uid = request.session.get('uid')
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request, 'Password reset Successfull')
            return redirect('loginn')
        else:
            messages.error(request, 'Password do not match')
            return redirect('resetpassword')
    else:
        return render(request, 'accounts/resetpassword.html')

@login_required(login_url='loginn')
def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    context = {
        'orders' : orders,

    }
    return render(request, 'accounts/my_orders.html', context)

@login_required(login_url = 'loginn')
def edit_profile(request):
    user = request.user
    profile = UserProfile.objects.get_or_create(user=user)[0]
    addresses = Address.objects.filter(user=user)

    if request.method == 'POST':
        address_form = AddressForm(request.POST)
        if address_form.is_valid():
            address = address_form.save(commit=False)
            address.user = user
            address.save()
            profile.addresses.add(address)
            messages.success(request, 'Address added successfully')
            return redirect('edit_profile')
    else:
        address_form = AddressForm()

    context = {
        'address_form': address_form,
        'addresses': addresses
    }
    return render(request, 'accounts/edit_profile.html', context)

@login_required(login_url = 'loginn')
def add_address(request):
    if request.method == 'POST':
        address_form = AddressForm(request.POST)
        if address_form.is_valid():
            address = address_form.save(commit=False)
            address.user = request.user
            address.save()
            messages.success(request, 'Address added successfully')
            return redirect('edit_profile')
    else:
        address_form = AddressForm()

    context = {
        'address_form': address_form,
    }
    return render(request, 'accounts/add_address.html', context)

@login_required(login_url = 'loginn')
def edit_address(request, address_id):
    address = get_object_or_404(Address, id=address_id)
    if request.method == 'POST':
        address_form = AddressForm(request.POST, instance=address)
        if address_form.is_valid():
            address_form.save()
            messages.success(request, 'Address updated successfully')
            return redirect('edit_profile')
    else:
        address_form = AddressForm(instance=address)

    context = {
        'address_form': address_form
    }
    return render(request, 'accounts/edit_address.html', context)

@login_required(login_url = 'loginn')
def delete_address(request, address_id):
    address = Address.objects.get(pk=address_id)
    if request.method == 'POST':
        address.delete()
        messages.success(request, 'Address deleted successfully')
    return redirect('edit_profile')


@login_required(login_url='loginn')   
def change_password(request):
    if request.method == 'POST':
        current_password = request.POST['current_password']
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']
        user = Account.objects.get(username__exact = request.user.username)

        if new_password == confirm_password:
            success = user.check_password(current_password)
            if success:
                user.set_password(new_password)
                user.save()
                # auth.logout(request)
                messages.success(request, 'Password Updated Successfully')
                return redirect('change_password')
            else:
                messages.error(request, 'Please enter valid current password')
                return redirect('change_password')
        else:
            messages.error(request, 'Password does not match')
            return redirect('change_password')
            
    return render(request, 'accounts/change_password.html')

@login_required(login_url='loginn') 
def order_detail(request, order_id):
    order_detail = OrderProduct.objects.filter(order__order_number = order_id)
    order = Order.objects.get(order_number = order_id)
    subtotal = 0
    for i in order_detail:
        product = Product.objects.get(id=i.product_id)  # Retrieve the product
        subtotal += product.price_after_discount() * i.quantity  # Calculate subtotal using price_after_discount


    # Fetching payment method from the related Payment object
    payment_method = order.payment.payment_method if order.payment else None

    # Retrieve coupon discount
    coupon_discount = 0
    if order.coupon:
        try:
            coupon = Coupon.objects.get(code=order.coupon)
                # Check if the coupon is valid
            if coupon.valid_from <= order.created_at <= coupon.valid_to:
                coupon_discount = coupon.discount
        except Coupon.DoesNotExist:
            pass
    context = {
        'order_detail' : order_detail,
        'order' : order,
        'subtotal' : subtotal,
        'payment': order.payment,
        'payment_method': payment_method,
        'coupon_discount': coupon_discount,  # Pass coupon discount to the context
        
    }
    

    return render(request, 'accounts/order_detail.html', context)

def invoice(request, order_id):
    order_detail = OrderProduct.objects.filter(order__order_number=order_id).prefetch_related('product')
    order = Order.objects.get(order_number=order_id)
    subtotal = 0
    for i in order_detail:
        
        subtotal += i.product.price_after_discount() * i.quantity  # Calculate subtotal using price_after_discount
        print("subtotal is ", subtotal)
    # Fetching payment method from the related Payment object
    payment_method = order.payment.payment_method if order.payment else None

    # Retrieve coupon discount
    coupon_discount = 0
    if order.coupon:
        try:
            coupon = Coupon.objects.get(code=order.coupon)
            # Check if the coupon is valid
            if coupon.valid_from <= order.created_at <= coupon.valid_to:
                coupon_discount = coupon.discount
        except Coupon.DoesNotExist:
            pass

    print("Order Detail:", order_detail)
    print("Order:", order)
    print("Subtotal:", subtotal)
    print("Payment Method:", payment_method)
    print("Coupon Discount:", coupon_discount)

    context = {
        'order_detail': order_detail,
        'order': order,
        'subtotal': subtotal,
        'payment_method': payment_method,
        'coupon_discount': coupon_discount,
    }

    return render(request, 'accounts/invoice.html', context)


@login_required(login_url='loginn') 
def generate_invoice_pdf(request, order_number):
    # Fetch the order details and other necessary data
    order = Order.objects.get(order_number=order_number)
    order_detail = OrderProduct.objects.filter(order__order_number=order_number)

    subtotal = 0
    for i in order_detail:
        
        subtotal += i.product.price_after_discount() * i.quantity  # Calculate subtotal using price_after_discount
        print("subtotal is ", subtotal)

    # Fetching payment method from the related Payment object
    payment_method = order.payment.payment_method if order.payment else None

    # Retrieve coupon discount
    coupon_discount = 0
    if order.coupon:
        try:
            coupon = Coupon.objects.get(code=order.coupon)
            # Check if the coupon is valid
            if coupon.valid_from <= order.created_at <= coupon.valid_to:
                coupon_discount = coupon.discount
        except Coupon.DoesNotExist:
            pass

    # Render the invoice HTML template with the order data
    rendered_html = render_to_string('accounts/invoice.html', {
        'order_detail': order_detail,
        'order': order,
        'payment': order.payment,
        'subtotal': subtotal,
        'payment_method': payment_method,
        'coupon_discount': coupon_discount,
    })

    # Create an HttpResponse object with PDF content type
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="invoice.pdf"'

    # Convert the rendered HTML to PDF and write to the response
    pisa.CreatePDF(rendered_html, dest=response)
    
    return response




def return_order(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)
    #if order.status != "Delivered":
       # messages.error(request, "Order has not been delivered yet")
       # return redirect("my_orders")

    if order.status == 'Returned':
        messages.error(request, "Order has already been returned")
    elif order.status == 'New':
        messages.error(request, "Order has not been delivered yet")
    elif order.status == 'Completed':
        messages.error(request, "Order has not been delivered yet")
    
    elif order.status == "Cancelled":
        messages.error(request, "Order has already been cancelled")
    elif order.payment != "Paid":
        order.status = "Returned"
        order.save()
        messages.error(request, "Order has been returned.")
    elif order.created_at + timedelta(days=3) < timezone.now():
        messages.error(request, "Cannot return order after 3 days")
    elif order.status == "Delivered":
        for item in order.order_items.all():
            item.product.stock += item.quantity
            item.product.save()
        order.status = "Returned"
        order.save()
        messages.success(
            request, f"Return successful.")
        
    # Retrieve the final_total from the Order model
    final_total = order.final_total
    # Retrieve the user's wallet if it exists, or create a new wallet if it doesn't exist
    wallet, created = Wallet.objects.get_or_create(account=request.user)
    
    # If the wallet was just created, set the wallet balance to the final_total
    if created:
        wallet.wallet_balance = final_total
    else:
        # If the wallet already exists, add the final_total to the existing wallet balance
        wallet.wallet_balance += final_total

    wallet.save()

    return redirect("my_orders")



def cancel_orderr(request, order_number):
    # Retrieve the order based on the order number
    order = get_object_or_404(Order, order_number=order_number)
    if order.status == 'Cancelled':
        messages.error(request, "Order has already been Cancelled")
    elif order.status == "New":
        messages.error(request, "Order has not been Completed yet")
        return redirect("my_orders")
    # Update order status to 'Cancelled' and set is_ordered to False
    else:
        order.status = 'Cancelled'
        order.is_ordered = False
        order.save()
    

    # Retrieve order items and update product stock
        order_items = OrderProduct.objects.filter(order=order)
        for order_item in order_items:
            product = order_item.product
            product.stock += order_item.quantity  # Increase product stock
            product.save()
    # Retrieve the final_total from the Order model
    final_total = order.final_total
    # Retrieve the user's wallet if it exists, or create a new wallet if it doesn't exist
    wallet, created = Wallet.objects.get_or_create(account=request.user)
    
    # If the wallet was just created, set the wallet balance to the final_total
    if created:
        wallet.wallet_balance = final_total
    else:
        # If the wallet already exists, add the final_total to the existing wallet balance
        wallet.wallet_balance += final_total

    wallet.save()
    messages.success(request, "Order has been cancelled successfully.")
    return redirect('my_orders')  # Redirect to a success page after cancellation
    
