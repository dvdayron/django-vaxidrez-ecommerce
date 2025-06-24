from django.contrib import admin

from .models import Category

class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {
        'slug': ('name',),
    }
    list_display = (
        'name',
        'slug',
        'description',
    )


# Register your models here.

admin.site.register(Category, CategoryAdmin)