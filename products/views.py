from django.shortcuts import render, get_object_or_404
from .models import Product


def all_products(request):
    """ This is the view for the products """
    products = Product.objects.all()

    context = {
        "products": products
    }

    return render(request, "products/products.html", context)


def product_detail(request, product_pk):
    products = get_object_or_404(Product, pk=product_pk)

    context = {
        "products": products
    }

    return render(request, "products/product.html", context)
