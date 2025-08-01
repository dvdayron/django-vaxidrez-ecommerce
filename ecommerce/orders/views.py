import datetime
from django.shortcuts import render, redirect
from django.contrib import messages

from cart.models import CartItem
from .models import Order
from .forms import OrderForm

def place_order(request, quantity=0, total=0):
    current_user = request.user
    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()

    if cart_count <= 0:
        return redirect('store')

    grand_total, tax = 0, 0

    for cart_item in cart_items:
        grand_total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity

    tax = (2 * total) / 100
    grand_total = total + tax

    if request.method == 'POST':
        form = OrderForm(request.POST)

        if form.is_valid():
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
            data.note = form.cleaned_data['note']
            data.total = grand_total
            data.tax = tax
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()

            yr = int(datetime.date.today().strftime('%Y'))
            mt = int(datetime.date.today().strftime('%m'))
            dt = int(datetime.date.today().strftime('%d'))
            d = datetime.date(yr, mt, dt)
            current_date = d.strftime('%Y%m%d')
            order_number = current_date + str(data.id)
            data.number = order_number
            data.save()

            order = Order.objects.get(user=current_user, is_ordered=False, number=order_number)

            return render(
                request,
                'orders/payments.html',
                {
                    'order': order,
                    'cart_items': cart_items,
                    'total': total,
                    'grand_total': grand_total,
                    'tax': tax,
                }
            )
        else:
            messages.error(request, 'Invalid form. ' + str(form.errors))

    return redirect('checkout')

def payments(request):
    return render(
        request,
        'orders/payments.html'
    )
