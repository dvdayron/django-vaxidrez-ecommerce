from django.contrib import admin

from .models import Cart, CartItem

# Register your models here.

class CartAdmin(admin.ModelAdmin):
    list_display = (
        'cart_key',
        'created_at',
    )

admin.site.register(Cart, CartAdmin)

class CartItemAdmin(admin.ModelAdmin):
    list_display = (
        'product',
        'cart',
        'quantity',
        'is_active',
    )

admin.site.register(CartItem, CartItemAdmin)