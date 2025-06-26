from django.contrib import admin

from .models import Product, Variation

# Register your models here.

class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'category',
        'formatted_price',
        'stock',
        'modified_at',
        'is_available',
        'show_in_home',
    )
    prepopulated_fields = {
        'slug': ('name',),
    }

    def formatted_price(self, obj):
        raw_price = float(obj.price)
        return "${:.2f}".format(raw_price)

    formatted_price.short_description = 'Price'

admin.site.register(Product, ProductAdmin)

class VariationAdmin(admin.ModelAdmin):
    list_display = (
        'product',
        'category',
        'value',
        'is_active',
    )
    list_editable = (
        'is_active',
    )
    list_filter = (
        'product',
        'category',
        'value',
        'is_active',
    )

admin.site.register(Variation, VariationAdmin)