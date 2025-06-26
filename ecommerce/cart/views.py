from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect, get_object_or_404

from store.models import Product, Variation
from .models import Cart, CartItem


# Create your views here.

def _cart_key(request):
    if not request.session.session_key:
        request.session.create()

    return request.session.session_key

def cart(request, total=0, quantity=0, cart_items=None):
    tax = 0
    grand_total = 0

    try:
        cart = Cart.objects.get(cart_key=_cart_key(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True).order_by('id')

        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity

        tax = (2 * total) / 100
        grand_total = total + tax
    except ObjectDoesNotExist:
        pass

    data = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'grand_total': grand_total,
    }

    return render(
        request,
        'cart/cart.html',
        data
    )

def add_cart(request, product_id):
    product = Product.objects.get(id=product_id)
    product_variations = []

    # Capturar variaciones desde el formulario
    if request.method == 'POST':
        for key, value in request.POST.items():
            try:
                variation = Variation.objects.get(
                    product=product,
                    category__iexact=key,
                    value__iexact=value
                )
                product_variations.append(variation)
            except Variation.DoesNotExist:
                pass

    # Obtener o crear el carrito
    try:
        cart = Cart.objects.get(cart_key=_cart_key(request))
    except Cart.DoesNotExist:
        cart = Cart.objects.create(cart_key=_cart_key(request))

    # Verificar si ya existe un CartItem para ese producto
    cart_items = CartItem.objects.filter(product=product, cart=cart)

    # Convertir la lista actual a lista de IDs ordenada
    product_variation_ids = sorted([v.id for v in product_variations])

    matched = False
    for item in cart_items:
        existing_variation_ids = sorted([v.id for v in item.variations.all()])
        if existing_variation_ids == product_variation_ids:
            item.quantity += 1
            item.save()
            matched = True
            break

    # Si no coincidió con ninguna variación existente, crear un nuevo CartItem
    if not matched:
        cart_item = CartItem.objects.create(
            product=product,
            cart=cart,
            quantity=1
        )
        if product_variations:
            cart_item.variations.add(*product_variations)
        cart_item.save()

    return redirect('cart')


def remove_cart(request, product_id, cart_item_id):
    cart = Cart.objects.get(cart_key=_cart_key(request))
    product = get_object_or_404(Product, id=product_id)

    try:
        cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)

        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    except:
        pass

    return redirect('cart')

def remove_cart_item(request, cart_item_id):
    try:
        cart_item = CartItem.objects.get(id=cart_item_id)
        cart_item.delete()
    except CartItem.DoesNotExist:
        pass

    return redirect('cart')