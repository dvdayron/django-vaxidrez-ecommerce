from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q

from .models import Product
from category.models import Category
from cart.models import CartItem
from cart.views import _cart_key


# Create your views here.

def store(request, category_slug=None):
    products = Product.objects.all().filter(is_available=True).order_by('-created_at')
    category = None

    if category_slug != None:
        category = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.all().filter(category=category, is_available=True).order_by('-created_at')

    total = products.count()

    paginator = Paginator(products, 12)
    page = request.GET.get('page')
    paged_products = paginator.get_page(page)

    data = {
        'products': paged_products,
        'total': total,
    }

    return render(
        request,
        'store/store.html',
        data
    )

def product_detail(request, category_slug, product_slug):
    try:
        product = Product.objects.get(category__slug=category_slug, slug=product_slug)
        in_cart = CartItem.objects.filter(cart__cart_key=_cart_key(request), product=product).exists()
    except Exception as e:
        raise e

    data = {
        'product': product,
        'in_cart': in_cart,
    }

    return render(
        request,
        'store/product_detail.html',
        data
    )

def search(request):
    products = []
    total = 0

    if 'keyword' in request.GET:
        keyword = request.GET['keyword']

        if keyword:
            products = Product.objects.order_by('-created_at').filter(
                Q(description__icontains=keyword) | Q(name__icontains=keyword)
            )
            total = products.count()

    paginator = Paginator(products, 12)
    page = request.GET.get('page')
    paged_products = paginator.get_page(page)

    data = {
        'products': paged_products,
        'total': total,
    }

    return render(
        request,
        'store/store.html',
        data
    )