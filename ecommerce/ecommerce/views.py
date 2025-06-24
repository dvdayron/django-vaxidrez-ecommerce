from django.shortcuts import render

from store.models import Product


def index(request):
    products = (Product
        .objects
        .all()
        .filter(is_available=True, show_in_home=True)
    )
    data = {
        'products': products,
    }

    return render(
        request,
        'ecommerce/index.html',
        data
    )