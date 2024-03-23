from django.shortcuts import render, redirect, get_object_or_404
from carts.models import CartItem
from .forms import OrderForm
from django.utils import timezone
from store.models import Product
from django.contrib import messages
from django.http import HttpResponse
from accounts.models import Address
from .models import Order, OrderProduct, Payment, Coupon
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from datetime import datetime
from carts.models import Cart
from django.http import JsonResponse
import json
from django.db.models import Q
from .utils import get_or_create_order 
#import datetime 

# Create your views here.

def payments(request):
    body = json.loads(request.body)
    order = Order.objects.get(user=request.user, is_ordered = False, order_number=body['orderID'])
    # store transaction details inside payment model
    payment  = Payment(
        user = request.user,
        payment_id = body['transID'],
        payment_method = body['payment_method'],
        amount_paid = order.order_total,
        status = body['status'],

    )
    payment.save()

    order.payment = payment
    order.is_ordered = True
    order.save()
    #move the cart items to Order Product table
    cart_items = CartItem.objects.filter(user=request.user)
    
    for item in cart_items:
        orderproduct = OrderProduct()
        orderproduct.order_id = order.id
        orderproduct.payment = payment
        orderproduct.user_id = request.user.id
        orderproduct.product_id = item.product_id
        orderproduct.quantity = item.quantity
        orderproduct.product_price = item.product.price
        orderproduct.ordered = True
        
        orderproduct.save()

        cart_item = CartItem.objects.get(id=item.id)
        product_variation = cart_item.variations.all()
        orderproduct = OrderProduct.objects.get(id=orderproduct.id)
        orderproduct.variations.set(product_variation)
        orderproduct.save()
        # Reduce the quantity of the sold products
        product = Product.objects.get(id=item.product_id)
        product.stock -= item.quantity
        product.save()
    #clear cart
    CartItem.objects.filter(user=request.user).delete()

    # send order number and transaction id back to sendData method via JsonResponse
    data = {
        'order_number' : order.order_number,
        'transID' : payment.payment_id,

    }
    return JsonResponse(data)
    

def place_order(request, total=0, quantity=0):
    if request.method == "POST":
        current_user = request.user
        # Get the current date and time
        current_datetime = datetime.now()
        selected_address_id = request.POST.get('selected_address')
        coupon = request.POST.get('coupon')

        


        # if the cart count is less than or equal to 0, then redirect back to shop
        cart_items = CartItem.objects.filter(user=current_user)
        cart_count = cart_items.count()
        if cart_count <= 0:
            return redirect('store')

    
        if selected_address_id:
            selected_address = get_object_or_404(Address, id=selected_address_id)
            grand_total = 0
            tax = 0
            final_total = 0  # Initialize final_total here
            for cart_item in cart_items:
                total += (cart_item.product.price * cart_item.quantity)
                quantity += cart_item.quantity
            tax = (2 * total)/100
            grand_total = total + tax
        # Coupon logic
        coupon_code = request.POST.get('coupon_code')
        if coupon_code:
            try:
                coupon = Coupon.objects.get(code=coupon_code)
                current_datetime = timezone.now()
                if coupon.valid_from <= current_datetime <= coupon.valid_to:
                    discount = coupon.discount
                    final_total = grand_total - discount
                    # Ensure grand total is not negative
                    final_total = max(0, final_total)
                else:
                    discount = 0
            except Coupon.DoesNotExist:
                discount = 0
                final_total = grand_total
                pass  # Coupon does not exist
           
            order = Order.objects.create(
                user=current_user,
                first_name=current_user.first_name,
                last_name=current_user.last_name,
                coupon=coupon_code,
                email=current_user.email,
                street_address=selected_address.street_address,
                city=selected_address.city,
                state=selected_address.state,
                country=selected_address.country,
                phone_number=selected_address.phone_number,
                order_total=grand_total,
                final_total=final_total,
                tax=tax,
                ip=request.META.get('REMOTE_ADDR')
            )

            

            # generate order number 
            '''yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))'''
            yr = current_datetime.year
            mt = current_datetime.month
            dt = current_datetime.day
            d = datetime(yr, mt, dt)
            current_date = d.strftime("%Y%d%m")
            order_number = current_date + str(order.id)
            order.order_number = order_number
            order.save()

            order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)
            # Reduce the stock of products in the cart items by 1
            '''for cart_item in cart_items:
                product = cart_item.product
                product.stock -= 1  # Reduce the stock by 1
                product.save()'''

            context={
                'order' : order,
                'cart_items' : cart_items,
                'total' : total,
                'tax' : tax,
                'grand_total' : grand_total,
                'discount' : discount,
                'final_total': final_total,


            }
            
            return render(request, 'orders/payments.html', context)
        else:
            return HttpResponse("Please select an address.")
    else:
        return redirect('checkout')

def order_complete(request):
    order_number = request.GET.get('order_number')
    transID = request.GET.get('payment_id')

    

    try:
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        # Update the order status to 'ACCEPTED'
        order.status = 'COMPLETED'
        order.save()
        ordered_products = OrderProduct.objects.filter(order_id=order.id)

        subtotal = 0
        for i in ordered_products:
            subtotal += i.product_price * i.quantity

        payment = Payment.objects.get(payment_id=transID)
        context = {
            'order' : order,
            'ordered_products' : ordered_products,
            'order_number' : order.order_number,
            'transID' : payment.payment_id,
            'payment' : payment,
            'subtotal' : subtotal,

        }

        return render(request, 'orders/order_complete.html', context)
    except (Payment.DoesNotExist, Order.DoesNotExist):
        return redirect('store')
    

def cash_on_delivery(request, order_number):
    # Retrieve the order based on the order number
    order = get_object_or_404(Order, order_number=order_number)


    # Update the order status to indicate payment confirmation
    order.is_ordered = True
    order.save()


    # Update the order status to 'ACCEPTED'
    order.status = 'COMPLETED'
    order.save()

    
    # Move the cart items to Order Product table
    cart_items = CartItem.objects.filter(user=request.user)


    for item in cart_items:
        orderproduct = OrderProduct()
        orderproduct.order_id = order.id
        orderproduct.user_id = request.user.id
        orderproduct.product_id = item.product_id
        orderproduct.quantity = item.quantity
        orderproduct.product_price = item.product.price
        orderproduct.ordered = True
        orderproduct.save()






    # Delete all the current user's cart items
    CartItem.objects.filter(user=request.user).delete()

     


    # Render the confirm_payment.html template with the order details
    context = {
        'order_number': order_number,
        'order': order
    }
    return render(request, 'orders/confirmpayment.html', context)


def cancel_order(request, order_number):
    # Retrieve the order based on the order number
    order = get_object_or_404(Order, order_number=order_number)
    
    # Update order status to 'Cancelled' and set is_ordered to False
    order.status = 'Cancelled'
    order.is_ordered = False
    order.save()

    # Retrieve order items and update product stock
    order_items = OrderProduct.objects.filter(order=order)
    for order_item in order_items:
        product = order_item.product
        product.stock += order_item.quantity  # Increase product stock
        product.save()
    messages.success(request, "Order has been cancelled successfully.")
    return redirect('store')  # Redirect to a success page after cancellation


def cancell_order(request, order_number):
    # Retrieve the order based on the order number
    order = get_object_or_404(Order, order_number=order_number)
    
    # Check if the order is already cancelled
    if order.status == 'Cancelled':
        messages.warning(request, "This order has already been cancelled.")
        return redirect('store')  # Redirect to a relevant page
    
    # Update order status to 'Cancelled' and set is_ordered to False
    order.status = 'Cancelled'
    order.is_ordered = False
    order.save()

    # Retrieve order items and update product stock
    order_items = OrderProduct.objects.filter(order=order)
    for order_item in order_items:
        product = order_item.product
        product.stock += order_item.quantity  # Increase product stock
        product.save()
    
    messages.success(request, "Order has been cancelled successfully.")
    return redirect('store')  # Redirect to a success page after cancellation



