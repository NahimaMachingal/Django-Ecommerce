from django.shortcuts import render, redirect, get_object_or_404
from carts.models import CartItem
from .forms import OrderForm
from django.contrib import messages
from django.http import HttpResponse
from .models import Order, OrderProduct
from django.db import transaction
from django.urls import reverse
import datetime 

# Create your views here.

def payments(request, order_number=None):
    if request.method == 'POST':
        # Get the order number from the form submission
        order_number = request.POST.get('order_number')

        try:
            # Retrieve the order
            order = Order.objects.get(order_number=order_number)

            # Update the order status to indicate payment confirmation
            order.is_ordered = True
            order.save()

            # Reduce the stock of products
            cart_items = CartItem.objects.filter(order=order)
            for cart_item in cart_items:
                product = cart_item.product
                product.stock -= cart_item.quantity
                product.save()

            # Clear the user's cart
            CartItem.objects.filter(user=request.user).delete()

            # Redirect to a success page or display a success message
            messages.success(request, 'Payment confirmed. Your order has been placed successfully!')
            return redirect('confirmpayment', order_number=order_number)

        except Order.DoesNotExist:
            # If the order does not exist, display an error message
            messages.error(request, 'Order not found.')
            return redirect('payments')

    else:
        # If the request method is GET, retrieve the order_number parameter if provided
        if order_number:
            try:
                # Retrieve the order based on the order number
                order = Order.objects.get(order_number=order_number)
            except Order.DoesNotExist:
                # If the order does not exist, handle accordingly
                messages.error(request, 'Order not found.')
                return redirect('payments')

            # Pass the order_number to the template context
            context = {
                'order_number': order_number
            }
            return render(request, 'orders/payments.html', context)
        else:
            # If order_number is not provided, render the payments page without any specific order
            return render(request, 'orders/payments.html')

def confirmpayment(request, order_number):
    # Retrieve the order based on the order number
    order = get_object_or_404(Order, order_number=order_number)

    # Update the order status to indicate payment confirmation
    order.is_ordered = True
    order.save()

    # Update the order status to 'ACCEPTED'
    order.status = 'ACCEPTED'
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

@transaction.atomic
def place_order(request, total=0, quantity=0):
    current_user = request.user

    # if the cart count is less than or equal to 0, then redirect back to shop
    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('store')
    
    grand_total = 0
    tax = 0
    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity
    tax = (2 * total)/100
    grand_total = total + tax

    if request.method == "POST":
        form = OrderForm(request.POST)
        if form.is_valid():
            #store all billing datas inside order table
            data = Order()
            data.user = current_user
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.phone = form.cleaned_data['phone']
            data.email = form.cleaned_data['email']
            data.address_line_1 = form.cleaned_data['address_line_1']
            data.address_line_2 = form.cleaned_data['address_line_2']
            data.country = form.cleaned_data['country']
            data.state = form.cleaned_data['state']
            data.city = form.cleaned_data['city']
            data.order_note = form.cleaned_data['order_note']
            data.order_total = grand_total
            data.tax = tax
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()

            # generate order number 
            yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))
            d = datetime.date(yr, dt, mt)
            current_date = d.strftime("%Y%d%m")
            order_number = current_date + str(data.id)
            data.order_number = order_number
            data.save()

            order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)
            # Reduce the stock of products in the cart items by 1
            for cart_item in cart_items:
                product = cart_item.product
                product.stock -= 1  # Reduce the stock by 1
                product.save()

            context={
                'order' : order,
                'cart_items' : cart_items,
                'total' : total,
                'tax' : tax,
                'grand_total' : grand_total,


            }
            
            return render(request, 'orders/payments.html', context)
        else:
            # Debugging: Print form errors
            print(form.errors)
            return HttpResponse("Form is not valid")  # Add an HttpResponse for debugging
    else:
        return redirect('checkout')
    


