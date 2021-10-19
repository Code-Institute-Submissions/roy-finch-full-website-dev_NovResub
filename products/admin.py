from django.contrib import admin
from .models import Product, Category, Console

# Register your models here.


class ProductAdmin():
    """
    Alters the way data is
    displayed in admin
    """
    list_display = {
        "sku",
        "name",
        "price",
        "console",
        "category",
        "rating",
        "image"
    }


class CategoryAdmin():
    """
    Alters the way data is
    displayed in admin
    """
    list_display = {
        "name",
        "display_name",
    }


class ConsoleAdmin():
    """
    Alters the way data is
    displayed in admin
    """
    list_display = {
        "name",
        "display_name",
    }


"""
Registers the alterations
"""
admin.site.register(Product)
admin.site.register(Category)
admin.site.register(Console)